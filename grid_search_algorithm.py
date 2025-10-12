from building import Building 
import random
import numpy as np
from k_visibility import count_crossings
from segment_presentation import present_segments


def get_top_mesurements(building: Building):
    top_mesurements = []
    for i in range(building.width * 2 - 1):
        ray = ((0.5 + 0.5 * i, -1), (0.5 + 0.5 * i, building.height + 1))
        top_mesurements.append(count_crossings(ray, building.segments))
    return top_mesurements

def get_left_mesurements(building: Building):
    left_mesurements = []
    for i in range(building.height * 2 - 1):
        ray = ((-1, 0.5 + 0.5 * i), (building.width + 1, 0.5 + 0.5 * i))
        left_mesurements.append(count_crossings(ray, building.segments))
    return left_mesurements

def get_grid(top_mesurements, left_mesurements):
    # TODO: find the exact rays and angles we should take. for now I will assume the entire grid and the min ray.
    pass

def create_rays(width, height, min_width=1, min_height=1):
    # top_rays_angle = math.tan(min_width/height)
    top_rays = []
    dist_between_top_rays = min_width/height
    for i in range((width-1)*height//min_width):
        top_rays.append(((i*dist_between_top_rays + dist_between_top_rays/2 , 0), (i*dist_between_top_rays + dist_between_top_rays/2 + min_width, height)))
    side_rays = []
    dist_between_left_rays = min_height/width
    for i in range((height-1)*width//min_height):
        side_rays.append(((width, i*dist_between_left_rays + dist_between_left_rays/2), (0, i*dist_between_left_rays + dist_between_left_rays/2 + min_height)))
    return top_rays, side_rays
    
def get_angle_mesurements(top_rays, side_rays, building: Building):
    top_rays_mesurements = []
    for ray in top_rays:
        top_rays_mesurements.append(count_crossings(ray, building.segments))
    side_rays_mesurements = []
    for ray in side_rays:
        side_rays_mesurements.append(count_crossings(ray, building.segments))
    return top_rays_mesurements, side_rays_mesurements

def get_grid_result(top_ray_mesurements, side_ray_mesurements, width, height):
    # moving through all points in the grid
    for row in range(1, width):
        for column in range (height-2, 0):
            k_visibility_left = top_ray_mesurements[row - 1 + height]

if __name__ == '__main__':
    building = Building(random.randint(3,6), random.randint(3,6))
    building.fill_grid_randomly(1)
    top_mesurements = get_top_mesurements(building)
    # print(top_mesurements)
    left_mesurements = get_left_mesurements(building)
    # print(left_mesurements)
    top_rays, side_rays = create_rays(building.width,building.height)
    top_ray_mesurements, side_ray_mesurements = get_angle_mesurements(top_rays, side_rays, building)
    
    present_segments([building.segments, top_rays, side_rays])
    # present_segments([building.segments])
    # get_ray_mesurements = 
    # building.present_grid()
