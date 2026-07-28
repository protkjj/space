#include "space_perception/traversability_layer.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <limits>
#include <memory>
#include <string>
#include <unordered_map>
#include <utility>

#include "geometry_msgs/msg/point_stamped.hpp"
#include "diagnostic_msgs/msg/diagnostic_status.hpp"
#include "diagnostic_msgs/msg/key_value.hpp"
#include "nav2_costmap_2d/cost_values.hpp"
#include "pluginlib/class_list_macros.hpp"
#include "rclcpp/duration.hpp"
#include "sensor_msgs/msg/point_field.hpp"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include "tf2_ros/buffer.h"
#include "space_perception/traversability_cost.hpp"

namespace space_perception
{

namespace
{
using PointField = sensor_msgs::msg::PointField;

const std::unordered_map<std::string, uint8_t> REQUIRED_FIELDS = {
  {"x", PointField::FLOAT32},
  {"y", PointField::FLOAT32},
  {"z", PointField::FLOAT32},
  {"traversability", PointField::FLOAT32},
  {"slope_penalty", PointField::FLOAT32},
  {"roughness_penalty", PointField::FLOAT32},
  {"step_penalty", PointField::FLOAT32},
  {"uncertainty_penalty", PointField::FLOAT32},
  {"confidence", PointField::FLOAT32},
  {"valid", PointField::UINT8},
  {"limiting_factor", PointField::UINT8},
};

template<typename T>
T readValue(
  const sensor_msgs::msg::PointCloud2 & message, const std::size_t point,
  const uint32_t offset)
{
  T value{};
  const auto byte = point * message.point_step + offset;
  std::memcpy(&value, message.data.data() + byte, sizeof(T));
  return value;
}
}  // namespace

TraversabilityLayer::TraversabilityLayer()
{
  enabled_ = true;
  current_ = true;
}

void TraversabilityLayer::onInitialize()
{
  auto node = node_.lock();
  if (!node) {
    throw std::runtime_error("TraversabilityLayer parent node expired");
  }
  logger_ = node->get_logger();
  clock_ = node->get_clock();
  global_frame_ = layered_costmap_->getGlobalFrameID();

  declareParameter("enabled", rclcpp::ParameterValue(true));
  declareParameter("input_topic", rclcpp::ParameterValue("/terrain/traversability"));
  declareParameter("maximum_input_age", rclcpp::ParameterValue(1.0));
  declareParameter("drop_stale_input", rclcpp::ParameterValue(true));
  declareParameter("cost_min", rclcpp::ParameterValue(1));
  declareParameter("cost_max", rclcpp::ParameterValue(180));
  declareParameter("cost_exponent", rclcpp::ParameterValue(1.0));
  declareParameter("minimum_traversability", rclcpp::ParameterValue(0.0));
  declareParameter("use_minimum_traversability_gate", rclcpp::ParameterValue(false));
  declareParameter("combination_method", rclcpp::ParameterValue(1));
  declareParameter("transform_tolerance", rclcpp::ParameterValue(0.2));
  declareParameter("clear_on_stale", rclcpp::ParameterValue(true));
  declareParameter("publish_debug_grid", rclcpp::ParameterValue(false));

  node->get_parameter(getFullName("enabled"), enabled_);
  node->get_parameter(getFullName("input_topic"), input_topic_);
  node->get_parameter(getFullName("maximum_input_age"), maximum_input_age_);
  node->get_parameter(getFullName("drop_stale_input"), drop_stale_input_);
  int cost_min = 1;
  int cost_max = 180;
  node->get_parameter(getFullName("cost_min"), cost_min);
  node->get_parameter(getFullName("cost_max"), cost_max);
  node->get_parameter(getFullName("cost_exponent"), cost_exponent_);
  node->get_parameter(
    getFullName("minimum_traversability"), minimum_traversability_);
  node->get_parameter(
    getFullName("use_minimum_traversability_gate"),
    use_minimum_traversability_gate_);
  node->get_parameter(getFullName("combination_method"), combination_method_);
  node->get_parameter(getFullName("transform_tolerance"), transform_tolerance_);
  node->get_parameter(getFullName("clear_on_stale"), clear_on_stale_);
  node->get_parameter(getFullName("publish_debug_grid"), publish_debug_grid_);

  if (maximum_input_age_ < 0.0 || transform_tolerance_ < 0.0 ||
    cost_exponent_ <= 0.0 || minimum_traversability_ < 0.0 ||
    minimum_traversability_ > 1.0 || cost_min < 0 || cost_max < cost_min ||
    cost_max >= nav2_costmap_2d::INSCRIBED_INFLATED_OBSTACLE ||
    (combination_method_ != 1 && combination_method_ != 2))
  {
    throw std::invalid_argument("invalid TraversabilityLayer parameters");
  }
  cost_min_ = static_cast<unsigned char>(cost_min);
  cost_max_ = static_cast<unsigned char>(cost_max);

  const auto qos = rclcpp::QoS(rclcpp::KeepLast(1)).best_effort();
  rclcpp::SubscriptionOptions subscription_options;
  subscription_options.callback_group = callback_group_;
  subscription_ = node->create_subscription<sensor_msgs::msg::PointCloud2>(
    input_topic_, qos,
    std::bind(&TraversabilityLayer::cloudCallback, this, std::placeholders::_1),
    subscription_options);
  debug_publisher_ =
    node->create_publisher<nav_msgs::msg::OccupancyGrid>(
    "/terrain/nav2_costs", rclcpp::QoS(1).transient_local());
  diagnostics_publisher_ =
    node->create_publisher<diagnostic_msgs::msg::DiagnosticArray>(
    "/terrain/nav2_cost_diagnostics", rclcpp::QoS(10));
  matchSize();
  RCLCPP_INFO(
    logger_,
    "TraversabilityLayer initialized: topic=%s frame=%s costs=[%u,%u]",
    input_topic_.c_str(), global_frame_.c_str(), cost_min_, cost_max_);
}

void TraversabilityLayer::matchSize()
{
  CostmapLayer::matchSize();
  resetMaps();
  clear_pending_ = true;
  has_rendered_stamp_ = false;
}

bool TraversabilityLayer::validateSchema(
  const sensor_msgs::msg::PointCloud2 & message) const
{
  if (message.point_step == 0U ||
    message.data.size() < static_cast<std::size_t>(message.row_step) * message.height)
  {
    return false;
  }
  for (const auto & required : REQUIRED_FIELDS) {
    const auto found = std::find_if(
      message.fields.begin(), message.fields.end(),
      [&required](const PointField & field) {
        return field.name == required.first &&
               field.datatype == required.second && field.count == 1U;
      });
    if (found == message.fields.end() ||
      found->offset + (required.second == PointField::FLOAT32 ? 4U : 1U) >
      message.point_step)
    {
      return false;
    }
  }
  return true;
}

bool TraversabilityLayer::isStale(
  const builtin_interfaces::msg::Time & stamp) const
{
  if (!drop_stale_input_) {
    return false;
  }
  return (clock_->now() - rclcpp::Time(stamp)).seconds() > maximum_input_age_;
}

void TraversabilityLayer::cloudCallback(
  sensor_msgs::msg::PointCloud2::ConstSharedPtr message)
{
  const auto started = std::chrono::steady_clock::now();
  if (!validateSchema(*message)) {
    ++malformed_count_;
    RCLCPP_WARN_THROTTLE(
      logger_, *clock_, 5000, "Malformed traversability cloud skipped");
    return;
  }
  const rclcpp::Time stamp(message->header.stamp);
  std::lock_guard<std::mutex> lock(mutex_);
  if (has_accepted_stamp_ && stamp == last_accepted_stamp_) {
    ++duplicate_count_;
    return;
  }
  if (isStale(message->header.stamp)) {
    ++stale_count_;
    RCLCPP_WARN_THROTTLE(
      logger_, *clock_, 5000, "Stale traversability cloud skipped");
    return;
  }
  latest_message_ = std::move(message);
  last_accepted_stamp_ = stamp;
  has_accepted_stamp_ = true;
  current_ = true;
  callback_duration_ms_ = std::chrono::duration<double, std::milli>(
    std::chrono::steady_clock::now() - started).count();
}

bool TraversabilityLayer::rebuild(
  const sensor_msgs::msg::PointCloud2 & message)
{
  std::unordered_map<std::string, uint32_t> offsets;
  for (const auto & field : message.fields) {
    offsets[field.name] = field.offset;
  }

  geometry_msgs::msg::TransformStamped transform;
  const bool transform_required =
    !message.header.frame_id.empty() && message.header.frame_id != global_frame_;
  if (transform_required) {
    try {
      transform = tf_->lookupTransform(
        global_frame_, message.header.frame_id, message.header.stamp,
        rclcpp::Duration::from_seconds(transform_tolerance_));
    } catch (const tf2::TransformException & error) {
      ++tf_failure_count_;
      current_ = false;
      RCLCPP_WARN_THROTTLE(
        logger_, *clock_, 5000, "Traversability transform unavailable: %s",
        error.what());
      return false;
    }
  }

  resetMaps();
  processed_cells_ = 0;
  written_cells_ = 0;
  const auto count =
    static_cast<std::size_t>(message.width) * message.height;
  for (std::size_t point = 0; point < count; ++point) {
    ++processed_cells_;
    const float score =
      readValue<float>(message, point, offsets.at("traversability"));
    const uint8_t valid = readValue<uint8_t>(message, point, offsets.at("valid"));
    if (!validTraversability(score, valid) ||
      (use_minimum_traversability_gate_ && score < minimum_traversability_))
    {
      continue;
    }
    geometry_msgs::msg::PointStamped input;
    input.header = message.header;
    input.point.x = readValue<float>(message, point, offsets.at("x"));
    input.point.y = readValue<float>(message, point, offsets.at("y"));
    input.point.z = readValue<float>(message, point, offsets.at("z"));
    if (!std::isfinite(input.point.x) || !std::isfinite(input.point.y)) {
      continue;
    }
    geometry_msgs::msg::PointStamped output = input;
    if (transform_required) {
      tf2::doTransform(input, output, transform);
    }
    unsigned int mx = 0;
    unsigned int my = 0;
    if (!worldToMap(output.point.x, output.point.y, mx, my)) {
      continue;
    }
    const auto cost =
      traversabilityToCost(score, cost_min_, cost_max_, cost_exponent_);
    const auto previous = getCost(mx, my);
    if (previous == nav2_costmap_2d::NO_INFORMATION || cost > previous) {
      setCost(mx, my, cost);
      ++written_cells_;
    }
  }
  current_ = true;
  publishDebugGrid(message.header.stamp);
  return true;
}

void TraversabilityLayer::touchWholeMap(
  double * min_x, double * min_y, double * max_x, double * max_y)
{
  touch(getOriginX(), getOriginY(), min_x, min_y, max_x, max_y);
  touch(
    getOriginX() + getSizeInMetersX(),
    getOriginY() + getSizeInMetersY(),
    min_x, min_y, max_x, max_y);
}

void TraversabilityLayer::updateBounds(
  double, double, double, double * min_x, double * min_y,
  double * max_x, double * max_y)
{
  const auto started = std::chrono::steady_clock::now();
  if (!enabled_) {
    return;
  }
  const auto * master = layered_costmap_->getCostmap();
  const bool geometry_changed =
    getSizeInCellsX() != master->getSizeInCellsX() ||
    getSizeInCellsY() != master->getSizeInCellsY() ||
    getResolution() != master->getResolution();
  const bool origin_changed =
    getOriginX() != master->getOriginX() ||
    getOriginY() != master->getOriginY();
  if (geometry_changed) {
    matchSize();
  } else if (origin_changed) {
    updateOrigin(master->getOriginX(), master->getOriginY());
    resetMaps();
    clear_pending_ = true;
    has_rendered_stamp_ = false;
  }

  sensor_msgs::msg::PointCloud2::ConstSharedPtr message;
  {
    std::lock_guard<std::mutex> lock(mutex_);
    message = latest_message_;
  }
  if (message && isStale(message->header.stamp) && clear_on_stale_) {
    if (has_rendered_stamp_) {
      clearLayer();
      touchWholeMap(min_x, min_y, max_x, max_y);
    }
  } else if (message &&
    (!has_rendered_stamp_ ||
    rclcpp::Time(message->header.stamp) != last_rendered_stamp_))
  {
    touchWholeMap(min_x, min_y, max_x, max_y);
    if (rebuild(*message)) {
      last_rendered_stamp_ = rclcpp::Time(message->header.stamp);
      has_rendered_stamp_ = true;
      clear_pending_ = false;
    }
  } else if (clear_pending_) {
    touchWholeMap(min_x, min_y, max_x, max_y);
    clear_pending_ = false;
  }
  update_bounds_duration_ms_ = std::chrono::duration<double, std::milli>(
    std::chrono::steady_clock::now() - started).count();
}

void TraversabilityLayer::updateCosts(
  nav2_costmap_2d::Costmap2D & master_grid,
  const int min_i, const int min_j, const int max_i, const int max_j)
{
  const auto started = std::chrono::steady_clock::now();
  if (!enabled_) {
    return;
  }
  if (combination_method_ == 2) {
    updateWithMaxWithoutUnknownOverwrite(
      master_grid, min_i, min_j, max_i, max_j);
  } else {
    updateWithMax(master_grid, min_i, min_j, max_i, max_j);
  }
  update_costs_duration_ms_ = std::chrono::duration<double, std::milli>(
    std::chrono::steady_clock::now() - started).count();
  RCLCPP_DEBUG_THROTTLE(
    logger_, *clock_, 5000,
    "terrain callback=%.3fms bounds=%.3fms costs=%.3fms cells=%lu/%lu "
    "drops duplicate=%lu stale=%lu malformed=%lu tf=%lu",
    callback_duration_ms_, update_bounds_duration_ms_, update_costs_duration_ms_,
    processed_cells_, written_cells_, duplicate_count_, stale_count_,
    malformed_count_, tf_failure_count_);
  publishDiagnostics();
}

void TraversabilityLayer::clearLayer()
{
  resetMaps();
  has_rendered_stamp_ = false;
  clear_pending_ = true;
  current_ = true;
  publishDebugGrid(clock_->now());
}

void TraversabilityLayer::reset()
{
  std::lock_guard<std::mutex> lock(mutex_);
  latest_message_.reset();
  has_accepted_stamp_ = false;
  clearLayer();
}

bool TraversabilityLayer::isClearable()
{
  return true;
}

void TraversabilityLayer::activate()
{
  active_ = true;
  if (debug_publisher_) {
    debug_publisher_->on_activate();
  }
  if (diagnostics_publisher_) {
    diagnostics_publisher_->on_activate();
  }
}

void TraversabilityLayer::deactivate()
{
  active_ = false;
  if (debug_publisher_) {
    debug_publisher_->on_deactivate();
  }
  if (diagnostics_publisher_) {
    diagnostics_publisher_->on_deactivate();
  }
}

void TraversabilityLayer::publishDiagnostics()
{
  const auto now = clock_->now();
  if (!active_ || !diagnostics_publisher_ ||
    (now - last_diagnostic_time_).seconds() < 1.0)
  {
    return;
  }
  last_diagnostic_time_ = now;
  double input_age = -1.0;
  {
    std::lock_guard<std::mutex> lock(mutex_);
    if (latest_message_) {
      input_age = std::max(
        0.0, (now - rclcpp::Time(latest_message_->header.stamp)).seconds());
    }
  }
  using diagnostic_msgs::msg::KeyValue;
  diagnostic_msgs::msg::DiagnosticStatus status;
  status.level = current_ ?
    diagnostic_msgs::msg::DiagnosticStatus::OK :
    diagnostic_msgs::msg::DiagnosticStatus::WARN;
  status.name = "traversability_layer";
  status.message = current_ ? "current" : "waiting for current terrain";
  status.values = {
    KeyValue().set__key("enabled").set__value(enabled_ ? "true" : "false"),
    KeyValue().set__key("input_age_seconds").set__value(
      std::to_string(input_age)),
    KeyValue().set__key("callback_duration_ms").set__value(
      std::to_string(callback_duration_ms_)),
    KeyValue().set__key("update_bounds_duration_ms").set__value(
      std::to_string(update_bounds_duration_ms_)),
    KeyValue().set__key("update_costs_duration_ms").set__value(
      std::to_string(update_costs_duration_ms_)),
    KeyValue().set__key("terrain_cells_processed").set__value(
      std::to_string(processed_cells_)),
    KeyValue().set__key("costmap_cells_written").set__value(
      std::to_string(written_cells_)),
    KeyValue().set__key("duplicate_drop_count").set__value(
      std::to_string(duplicate_count_)),
    KeyValue().set__key("stale_drop_count").set__value(
      std::to_string(stale_count_)),
    KeyValue().set__key("malformed_drop_count").set__value(
      std::to_string(malformed_count_)),
    KeyValue().set__key("tf_failure_count").set__value(
      std::to_string(tf_failure_count_)),
  };
  diagnostic_msgs::msg::DiagnosticArray array;
  array.header.stamp = now;
  array.status.push_back(std::move(status));
  diagnostics_publisher_->publish(array);
}

void TraversabilityLayer::publishDebugGrid(
  const builtin_interfaces::msg::Time & stamp)
{
  if (!publish_debug_grid_ || !active_ || !debug_publisher_) {
    return;
  }
  nav_msgs::msg::OccupancyGrid grid;
  grid.header.frame_id = global_frame_;
  grid.header.stamp = stamp;
  grid.info.resolution = getResolution();
  grid.info.width = getSizeInCellsX();
  grid.info.height = getSizeInCellsY();
  grid.info.origin.position.x = getOriginX();
  grid.info.origin.position.y = getOriginY();
  grid.info.origin.orientation.w = 1.0;
  grid.data.resize(grid.info.width * grid.info.height, -1);
  for (unsigned int y = 0; y < grid.info.height; ++y) {
    for (unsigned int x = 0; x < grid.info.width; ++x) {
      const auto cost = getCost(x, y);
      if (cost != nav2_costmap_2d::NO_INFORMATION) {
        grid.data[y * grid.info.width + x] = static_cast<int8_t>(
          std::lround(100.0 * cost / nav2_costmap_2d::MAX_NON_OBSTACLE));
      }
    }
  }
  debug_publisher_->publish(grid);
}

}  // namespace space_perception

PLUGINLIB_EXPORT_CLASS(
  space_perception::TraversabilityLayer, nav2_costmap_2d::Layer)
