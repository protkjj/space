#ifndef SPACE_PERCEPTION__TRAVERSABILITY_COST_HPP_
#define SPACE_PERCEPTION__TRAVERSABILITY_COST_HPP_

#include <cstdint>
#include <vector>

namespace space_perception
{

struct TerrainCell
{
  unsigned int x;
  unsigned int y;
  unsigned char cost;
};

bool validTraversability(float score, uint8_t valid);

unsigned char traversabilityToCost(
  double score, unsigned char cost_min, unsigned char cost_max,
  double exponent);

void retainMaximumCost(
  std::vector<unsigned char> & grid, unsigned int size_x,
  unsigned int size_y, const TerrainCell & cell,
  unsigned char no_information);

void combineMaximum(
  std::vector<unsigned char> & master,
  const std::vector<unsigned char> & terrain,
  unsigned char no_information);

}  // namespace space_perception

#endif  // SPACE_PERCEPTION__TRAVERSABILITY_COST_HPP_
