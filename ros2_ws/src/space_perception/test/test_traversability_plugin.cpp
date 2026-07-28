#include <algorithm>
#include <memory>

#include "gtest/gtest.h"
#include "nav2_costmap_2d/layer.hpp"
#include "pluginlib/class_loader.hpp"

TEST(TraversabilityPlugin, IsDiscoverableAndConstructible)
{
  pluginlib::ClassLoader<nav2_costmap_2d::Layer> loader(
    "nav2_costmap_2d", "nav2_costmap_2d::Layer");
  const auto classes = loader.getDeclaredClasses();
  EXPECT_NE(
    std::find(
      classes.begin(), classes.end(),
      "space_perception::TraversabilityLayer"),
    classes.end());
  auto layer =
    loader.createSharedInstance("space_perception::TraversabilityLayer");
  ASSERT_NE(layer, nullptr);
  EXPECT_TRUE(layer->isClearable());
}
