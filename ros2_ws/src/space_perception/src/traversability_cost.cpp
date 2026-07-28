#include "space_perception/traversability_cost.hpp"

#include <algorithm>
#include <cmath>
#include <stdexcept>

#include "nav2_costmap_2d/cost_values.hpp"

namespace space_perception
{

bool validTraversability(const float score, const uint8_t valid)
{
  return valid == 1U && std::isfinite(score) && score >= 0.0F && score <= 1.0F;
}

unsigned char traversabilityToCost(
  const double score, const unsigned char cost_min,
  const unsigned char cost_max, const double exponent)
{
  if (!std::isfinite(score) || !std::isfinite(exponent) || exponent <= 0.0) {
    throw std::invalid_argument("score and exponent must be finite");
  }
  if (cost_min > cost_max ||
    cost_max >= nav2_costmap_2d::INSCRIBED_INFLATED_OBSTACLE)
  {
    throw std::invalid_argument("terrain costs must be an ordered soft range");
  }
  const double penalty = std::clamp(1.0 - score, 0.0, 1.0);
  const double normalized = std::pow(penalty, exponent);
  const double cost = static_cast<double>(cost_min) +
    normalized * static_cast<double>(cost_max - cost_min);
  return static_cast<unsigned char>(std::lround(cost));
}

void retainMaximumCost(
  std::vector<unsigned char> & grid, const unsigned int size_x,
  const unsigned int size_y, const TerrainCell & cell,
  const unsigned char no_information)
{
  if (cell.x >= size_x || cell.y >= size_y || grid.size() != size_x * size_y) {
    return;
  }
  auto & existing = grid[cell.y * size_x + cell.x];
  if (existing == no_information || cell.cost > existing) {
    existing = cell.cost;
  }
}

void combineMaximum(
  std::vector<unsigned char> & master,
  const std::vector<unsigned char> & terrain,
  const unsigned char no_information)
{
  if (master.size() != terrain.size()) {
    throw std::invalid_argument("master and terrain grids must match");
  }
  for (std::size_t index = 0; index < master.size(); ++index) {
    if (terrain[index] != no_information &&
      (master[index] == no_information || terrain[index] > master[index]))
    {
      master[index] = terrain[index];
    }
  }
}

}  // namespace space_perception
