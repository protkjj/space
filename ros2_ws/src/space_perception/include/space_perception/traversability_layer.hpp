#ifndef SPACE_PERCEPTION__TRAVERSABILITY_LAYER_HPP_
#define SPACE_PERCEPTION__TRAVERSABILITY_LAYER_HPP_

#include <chrono>
#include <memory>
#include <mutex>
#include <string>

#include "nav2_costmap_2d/costmap_layer.hpp"
#include "diagnostic_msgs/msg/diagnostic_array.hpp"
#include "nav_msgs/msg/occupancy_grid.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/lifecycle_publisher.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"

namespace space_perception
{

class TraversabilityLayer : public nav2_costmap_2d::CostmapLayer
{
public:
  TraversabilityLayer();
  ~TraversabilityLayer() override = default;

  void onInitialize() override;
  void matchSize() override;
  void updateBounds(
    double robot_x, double robot_y, double robot_yaw,
    double * min_x, double * min_y, double * max_x, double * max_y) override;
  void updateCosts(
    nav2_costmap_2d::Costmap2D & master_grid,
    int min_i, int min_j, int max_i, int max_j) override;
  void reset() override;
  bool isClearable() override;
  void activate() override;
  void deactivate() override;

private:
  bool validateSchema(const sensor_msgs::msg::PointCloud2 & message) const;
  void cloudCallback(sensor_msgs::msg::PointCloud2::ConstSharedPtr message);
  bool rebuild(const sensor_msgs::msg::PointCloud2 & message);
  void clearLayer();
  void touchWholeMap(
    double * min_x, double * min_y, double * max_x, double * max_y);
  void publishDebugGrid(const builtin_interfaces::msg::Time & stamp);
  void publishDiagnostics();
  bool isStale(const builtin_interfaces::msg::Time & stamp) const;

  std::mutex mutex_;
  sensor_msgs::msg::PointCloud2::ConstSharedPtr latest_message_;
  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr subscription_;
  rclcpp_lifecycle::LifecyclePublisher<nav_msgs::msg::OccupancyGrid>::SharedPtr
    debug_publisher_;
  rclcpp_lifecycle::LifecyclePublisher<
    diagnostic_msgs::msg::DiagnosticArray>::SharedPtr diagnostics_publisher_;
  rclcpp::Time last_accepted_stamp_{0, 0, RCL_ROS_TIME};
  rclcpp::Time last_rendered_stamp_{0, 0, RCL_ROS_TIME};
  bool has_accepted_stamp_{false};
  bool has_rendered_stamp_{false};
  bool active_{false};
  bool clear_pending_{false};
  std::string input_topic_;
  std::string global_frame_;
  double maximum_input_age_{1.0};
  double cost_exponent_{1.0};
  double minimum_traversability_{0.0};
  double transform_tolerance_{0.2};
  unsigned char cost_min_{1};
  unsigned char cost_max_{180};
  int combination_method_{1};
  bool drop_stale_input_{true};
  bool use_minimum_traversability_gate_{false};
  bool clear_on_stale_{true};
  bool publish_debug_grid_{false};
  uint64_t duplicate_count_{0};
  uint64_t stale_count_{0};
  uint64_t malformed_count_{0};
  uint64_t tf_failure_count_{0};
  uint64_t processed_cells_{0};
  uint64_t written_cells_{0};
  double callback_duration_ms_{0.0};
  double update_bounds_duration_ms_{0.0};
  double update_costs_duration_ms_{0.0};
  rclcpp::Time last_diagnostic_time_{0, 0, RCL_ROS_TIME};
};

}  // namespace space_perception

#endif  // SPACE_PERCEPTION__TRAVERSABILITY_LAYER_HPP_
