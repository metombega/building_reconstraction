from building import Building 
import random
import numpy as np
from tools.k_visibility import count_crossings
from tools.segment_presentation import present_segments

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

def add_horizontal_edges(horizontal_segments, right_angle_ray_mesurements, height):
    left_lines_found = 0
    for i in range(1, height):
        if right_angle_ray_mesurements[i] - 2 == left_lines_found + 1:
            horizontal_segments[0][height-1-i] = 1
            left_lines_found += 1

def add_vertical_edges(vertical_segments, left_angle_ray_mesurements, top_ray_mesurements, width, height):
    for i in range(width-1):
        if left_angle_ray_mesurements[i*height] - 1 == top_ray_mesurements[i]:
            vertical_segments[i][0] = 1

def get_grid(top_ray_mesurements, right_angle_ray_mesurements, left_angle_ray_mesurements, width, height):
    # moving through all points in the grid
    horizontal_segments = np.zeros((width, height-1), dtype=bool)
    vertical_segments = np.zeros((width-1, height), dtype=bool)
    add_horizontal_edges(horizontal_segments, right_angle_ray_mesurements, height)
    add_vertical_edges(vertical_segments, left_angle_ray_mesurements, top_ray_mesurements, width, height)
    add_internal_points(horizontal_segments, vertical_segments, right_angle_ray_mesurements, left_angle_ray_mesurements, width, height)
    return horizontal_segments, vertical_segments


def add_internal_points(horizontal_segments, vertical_segments, right_angle_ray_mesurements, left_angle_ray_mesurements, width, height):
    for i in range(width-1):
        for j in range(height-1):
            point = (i,j)
            right_indices, left_indices = find_intersection_rays(point, height)
            k_visibility_r1 = right_angle_ray_mesurements[right_indices[0]]
            k_visibility_r2 = right_angle_ray_mesurements[right_indices[1]]
            k_visibility_l1 = left_angle_ray_mesurements[left_indices[0]]
            k_visibility_l2 = left_angle_ray_mesurements[left_indices[1]]
            has_line_below = vertical_segments[i,j]
            has_line_left = horizontal_segments[i,j]
            has_line_above, has_line_right = process_point(k_visibility_r1, k_visibility_r2, k_visibility_l1, k_visibility_l2, has_line_below, has_line_left)
            vertical_segments[i,j+1] = int(has_line_above)
            horizontal_segments[i+1,j] = int(has_line_right)
            

def process_point(k_visibility_r1, k_visibility_r2, k_visibility_l1, k_visibility_l2, has_line_below, has_line_left):
    sum_of_given_lines = int(has_line_below) + int(has_line_left)
    if k_visibility_l1 - sum_of_given_lines == k_visibility_l2 - 2:
        return True, True
    elif k_visibility_l1 - sum_of_given_lines == k_visibility_l2:
        return False, False
    elif k_visibility_r1 - int(has_line_left) == k_visibility_r2 - int(has_line_below) + 1:
        return True, False
    elif k_visibility_r1 - int(has_line_left) == k_visibility_r2 - int(has_line_below) - 1:
        return False, True
    else:
        raise AssertionError("visibility mesurements are not as expected")

def find_intersection_rays(point, height):
    x = point[0]
    y = point[1]
    # compute the indices of the rays that pass near the internal grid point
    r1 = height*(2 + x) - y - 2
    r2 = height*(2 + x) - y - 1
    l1 = height*x + y
    l2 = height*x + y + 1
    # Return indices (not the measurement values) so callers can index into the ray lists
    right_indices = [r1, r2]
    left_indices = [l1, l2]
    return right_indices, left_indices

def add_frame(matrix, horizontal):
    if horizontal:
        # Create a column of True values with the same number of rows
        col_true = np.ones((matrix.shape[0], 1), dtype=bool)
        # Concatenate at the beginning and at the end
        new_matrix = np.hstack([col_true, matrix, col_true])
    else:
        # Create a row of True values with the same number of columns
        row_true = np.ones((1, matrix.shape[1]), dtype=bool)
        # Concatenate at the beginning and at the end
        new_matrix = np.vstack([row_true, matrix, row_true])
    return new_matrix

def reconstract_building(building: Building, presen_results):
    # define the angles to mesure
    right_angle_rays, left_angle_rays = create_angled_rays(building.width, building.height)
    
    # find the k-visibility for each angle
    top_mesurements = get_top_mesurements(building)
    right_angle_ray_mesurements, left_angle_ray_mesurements = get_angle_mesurements(right_angle_rays, left_angle_rays, building)
    
    # reconstract the building using the k-vsibility mesurements
    horizontal_matrix, vertical_matrix = get_grid(top_mesurements, right_angle_ray_mesurements, left_angle_ray_mesurements, building.width, building.height)
    new_horizontal_lines = add_frame(horizontal_matrix, True)
    new_vertical_lines = add_frame(vertical_matrix, False)
    reconstracted_building = Building(width=building.width, height=building.height, horizontal_lines=new_horizontal_lines, vertical_lines=new_vertical_lines)
    
    # present results
    if presen_results:
        present_segments([building.segments, right_angle_rays, left_angle_rays])
        present_segments([reconstracted_building.segments])
    
    return reconstracted_building

if __name__ == '__main__':
    for _ in range(3):
        # create a random building
        building = Building(random.randint(4,7), random.randint(4,7))
        building.fill_grid_randomly(0.25)
        
        reconstracted_building = reconstract_building(building, True)
        assert(np.array_equal(reconstracted_building.horizontal_lines, building.horizontal_lines) and np.array_equal(reconstracted_building.vertical_lines, building.vertical_lines))
