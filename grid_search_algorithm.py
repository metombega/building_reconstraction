from building import Building 
import random
import numpy as np
from k_visibility import count_crossings
from segment_presentation import present_segments


def get_top_mesurements_with_inf(building: Building):
    top_mesurements = []
    for i in range(building.width * 2 - 1):
        ray = ((0.5 + 0.5 * i, -1), (0.5 + 0.5 * i, building.height + 1))
        top_mesurements.append(count_crossings(ray, building.segments))
    return top_mesurements

def get_top_mesurements(building: Building):
    top_mesurements = []
    for i in range(building.width):
        ray = ((0.5 + i, -1), (0.5 + i, building.height + 1))
        top_mesurements.append(count_crossings(ray, building.segments))
    return top_mesurements

# def get_left_mesurements(building: Building):
#     left_mesurements = []
#     for i in range(building.height * 2 - 1):
#         ray = ((-1, 0.5 + 0.5 * i), (building.width + 1, 0.5 + 0.5 * i))
#         left_mesurements.append(count_crossings(ray, building.segments))
#     return left_mesurements

def get_grid(top_mesurements, left_mesurements):
    # TODO: find the exact rays and angles we should take. for now I will assume the entire grid and the min ray.
    pass

def create_angled_rays(width, height):
    dist_between_rays = 1/height
    left_angle_rays = []
    for i in range((width)*height):
        left_angle_rays.append(((i*dist_between_rays + dist_between_rays/2 + 1, 0), (i*dist_between_rays + dist_between_rays/2, height)))
    right_angle_rays = []
    for i in range((width)*height):
        right_angle_rays.append(((i*dist_between_rays + dist_between_rays/2 - 1, 0), (i*dist_between_rays + dist_between_rays/2, height)))
    return right_angle_rays, left_angle_rays
    
def get_angle_mesurements(right_angle_rays, left_angle_rays, building: Building):
    right_angle_rays_mesurements = []
    for ray in right_angle_rays:
        right_angle_rays_mesurements.append(count_crossings(ray, building.segments))
    left_angle_rays_mesurements = []
    for ray in left_angle_rays:
        left_angle_rays_mesurements.append(count_crossings(ray, building.segments))
    return right_angle_rays_mesurements, left_angle_rays_mesurements

def add_horizontal_edges(horizontal_segments, right_angle_ray_mesurements, left_angle_ray_mesurements, width, height):
    left_lines_found = 0
    # right_lines_found = 0
    for i in range(1, height):
        if right_angle_ray_mesurements[i] - 2 == left_lines_found + 1:
            horizontal_segments[0][height-1-i] = 1
            left_lines_found += 1
        # if left_angle_ray_mesurements[-i-1] - 2 == right_lines_found + 1:
        #     horizontal_segments[width-1][-i] = 1
        #     right_lines_found += 1

def add_vertical_edges(vertical_segments, right_angle_ray_mesurements, top_ray_mesurements, width, height):
    right_ray_ind = height # right_angle_rays[building.width + 2]
    for i in range(width-1):
        print(f'ind: {right_ray_ind}')
        print(right_angle_ray_mesurements[right_ray_ind])
        # print(top_ray_mesurements[i])
        if right_angle_ray_mesurements[height*(i+1)] == top_ray_mesurements[i] + 1:
            vertical_segments[i][-1] = 1

def get_grid_result(top_ray_mesurements, right_angle_ray_mesurements, left_angle_ray_mesurements, width, height):
    # moving through all points in the grid
    
    horizontal_segments = np.zeros((width, height-1), dtype=bool)
    vertical_segments = np.zeros((width-1, height), dtype=bool)
    print(right_angle_ray_mesurements)
    print(top_mesurements)
    add_horizontal_edges(horizontal_segments, right_angle_ray_mesurements, left_angle_ray_mesurements, width, height)
    add_vertical_edges(vertical_segments, right_angle_ray_mesurements, top_ray_mesurements, width, height)
    print(horizontal_segments)
    print(vertical_segments)
    # reorder_right_rays = []

    # for row in range(1, width):
    #     for column in range (height-2, 0):
    #         k_visibility_left = top_ray_mesurements[row - 1 + height]

if __name__ == '__main__':
    # building = Building(random.randint(3,6), random.randint(3,6))
    building = Building(4,6)
    building.fill_grid_randomly(0.5)
    top_mesurements = get_top_mesurements(building)
    # print(top_mesurements)
    # left_mesurements = get_left_mesurements(building)
    # print(left_mesurements)
    right_angle_rays, left_angle_rays = create_angled_rays(building.width, building.height)
    right_angle_ray_mesurements, left_angle_ray_mesurements = get_angle_mesurements(right_angle_rays, left_angle_rays, building)
    grid = get_grid_result(top_mesurements, right_angle_ray_mesurements, left_angle_ray_mesurements, building.width, building.height)
    present_segments([building.segments, right_angle_rays, left_angle_rays])
    
    # present_segments([building.segments])
    # get_ray_mesurements = 
    # building.present_grid()
