#include <limits>
#include <stdexcept>
#include <vector>

#include "gtest/gtest.h"
#include "nav2_costmap_2d/cost_values.hpp"
#include "space_perception/traversability_cost.hpp"

using nav2_costmap_2d::LETHAL_OBSTACLE;
using nav2_costmap_2d::NO_INFORMATION;
using space_perception::TerrainCell;
using space_perception::combineMaximum;
using space_perception::retainMaximumCost;
using space_perception::traversabilityToCost;
using space_perception::validTraversability;

TEST(TraversabilityCost, PerfectScoreMapsToMinimum)
{
  EXPECT_EQ(traversabilityToCost(1.0, 1, 180, 1.0), 1);
}

TEST(TraversabilityCost, ZeroScoreMapsToMaximum)
{
  EXPECT_EQ(traversabilityToCost(0.0, 1, 180, 1.0), 180);
}

TEST(TraversabilityCost, IntermediateScoresAreMonotonic)
{
  EXPECT_LT(
    traversabilityToCost(0.8, 1, 180, 1.0),
    traversabilityToCost(0.4, 1, 180, 1.0));
}

TEST(TraversabilityCost, ExponentShapesPenalty)
{
  EXPECT_LT(
    traversabilityToCost(0.5, 1, 180, 2.0),
    traversabilityToCost(0.5, 1, 180, 1.0));
}

TEST(TraversabilityCost, ScoresAreClampedToBounds)
{
  EXPECT_EQ(traversabilityToCost(2.0, 10, 100, 1.0), 10);
  EXPECT_EQ(traversabilityToCost(-2.0, 10, 100, 1.0), 100);
}

TEST(TraversabilityCost, RejectsNan)
{
  EXPECT_THROW(
    traversabilityToCost(
      std::numeric_limits<double>::quiet_NaN(), 1, 180, 1.0),
    std::invalid_argument);
}

TEST(TraversabilityCost, RejectsNonPositiveExponent)
{
  EXPECT_THROW(traversabilityToCost(0.5, 1, 180, 0.0), std::invalid_argument);
}

TEST(TraversabilityCost, RejectsReversedBounds)
{
  EXPECT_THROW(traversabilityToCost(0.5, 100, 10, 1.0), std::invalid_argument);
}

TEST(TraversabilityCost, RejectsObstacleCost)
{
  EXPECT_THROW(
    traversabilityToCost(0.5, 1, LETHAL_OBSTACLE, 1.0),
    std::invalid_argument);
}

TEST(TraversabilityValidity, AcceptsFiniteValidScore)
{
  EXPECT_TRUE(validTraversability(0.5F, 1U));
}

TEST(TraversabilityValidity, RejectsInvalidFlag)
{
  EXPECT_FALSE(validTraversability(0.5F, 0U));
}

TEST(TraversabilityValidity, RejectsNan)
{
  EXPECT_FALSE(validTraversability(
    std::numeric_limits<float>::quiet_NaN(), 1U));
}

TEST(TraversabilityValidity, RejectsOutOfRange)
{
  EXPECT_FALSE(validTraversability(-0.1F, 1U));
  EXPECT_FALSE(validTraversability(1.1F, 1U));
}

TEST(TerrainGrid, MultiplePointsRetainMaximum)
{
  std::vector<unsigned char> grid(4, NO_INFORMATION);
  retainMaximumCost(grid, 2, 2, TerrainCell{0, 1, 20}, NO_INFORMATION);
  retainMaximumCost(grid, 2, 2, TerrainCell{0, 1, 80}, NO_INFORMATION);
  retainMaximumCost(grid, 2, 2, TerrainCell{0, 1, 40}, NO_INFORMATION);
  EXPECT_EQ(grid[2], 80);
}

TEST(TerrainGrid, ReplacementDoesNotAccumulate)
{
  std::vector<unsigned char> first(4, NO_INFORMATION);
  retainMaximumCost(first, 2, 2, TerrainCell{0, 0, 90}, NO_INFORMATION);
  std::vector<unsigned char> replacement(4, NO_INFORMATION);
  retainMaximumCost(replacement, 2, 2, TerrainCell{1, 1, 20}, NO_INFORMATION);
  EXPECT_EQ(replacement[0], NO_INFORMATION);
  EXPECT_EQ(replacement[3], 20);
}

TEST(TerrainGrid, ResizeStartsWithNoContribution)
{
  std::vector<unsigned char> resized(9, NO_INFORMATION);
  EXPECT_EQ(resized.size(), 9U);
  EXPECT_EQ(resized.front(), NO_INFORMATION);
}

TEST(TerrainGrid, OutOfBoundsPointHasNoEffect)
{
  std::vector<unsigned char> grid(4, NO_INFORMATION);
  retainMaximumCost(grid, 2, 2, TerrainCell{4, 4, 100}, NO_INFORMATION);
  EXPECT_EQ(grid, std::vector<unsigned char>(4, NO_INFORMATION));
}

TEST(TerrainCombination, LethalMasterCostIsPreserved)
{
  std::vector<unsigned char> master{LETHAL_OBSTACLE};
  combineMaximum(master, std::vector<unsigned char>{180}, NO_INFORMATION);
  EXPECT_EQ(master[0], LETHAL_OBSTACLE);
}

TEST(TerrainCombination, InflationCostIsNotReduced)
{
  std::vector<unsigned char> master{200};
  combineMaximum(master, std::vector<unsigned char>{120}, NO_INFORMATION);
  EXPECT_EQ(master[0], 200);
}

TEST(TerrainCombination, NoContributionDoesNotChangeMaster)
{
  std::vector<unsigned char> master{42};
  combineMaximum(
    master, std::vector<unsigned char>{NO_INFORMATION}, NO_INFORMATION);
  EXPECT_EQ(master[0], 42);
}

TEST(TerrainCombination, SoftCostRaisesLowerMasterCost)
{
  std::vector<unsigned char> master{20};
  combineMaximum(master, std::vector<unsigned char>{120}, NO_INFORMATION);
  EXPECT_EQ(master[0], 120);
}

TEST(TerrainCombination, UnknownMasterCanReceiveTerrainCost)
{
  std::vector<unsigned char> master{NO_INFORMATION};
  combineMaximum(master, std::vector<unsigned char>{120}, NO_INFORMATION);
  EXPECT_EQ(master[0], 120);
}

TEST(TerrainCombination, MismatchedGridsAreRejected)
{
  std::vector<unsigned char> master(2, 0);
  EXPECT_THROW(
    combineMaximum(master, std::vector<unsigned char>(1, 0), NO_INFORMATION),
    std::invalid_argument);
}

TEST(TerrainGrid, DeterministicForInputOrder)
{
  std::vector<unsigned char> forward(1, NO_INFORMATION);
  std::vector<unsigned char> reverse(1, NO_INFORMATION);
  retainMaximumCost(forward, 1, 1, TerrainCell{0, 0, 20}, NO_INFORMATION);
  retainMaximumCost(forward, 1, 1, TerrainCell{0, 0, 80}, NO_INFORMATION);
  retainMaximumCost(reverse, 1, 1, TerrainCell{0, 0, 80}, NO_INFORMATION);
  retainMaximumCost(reverse, 1, 1, TerrainCell{0, 0, 20}, NO_INFORMATION);
  EXPECT_EQ(forward, reverse);
}
