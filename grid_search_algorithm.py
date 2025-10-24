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

def add_vertical_edges(vertical_segments, left_angle_ray_mesurements, top_ray_mesurements, width, height):
    # right_ray_ind = height # right_angle_rays[building.width + 2]
    for i in range(width-1):
        # print(f'ind: {right_ray_ind}')
        print(left_angle_ray_mesurements[i*height])
        print(top_ray_mesurements[i])
        if left_angle_ray_mesurements[i*height] - 1 == top_ray_mesurements[i]:
            vertical_segments[i][0] = 1

def get_grid_result(building, top_ray_mesurements, right_angle_ray_mesurements, right_angle_rays, left_angle_rays, left_angle_ray_mesurements, width, height):
    # moving through all points in the grid
    
    horizontal_segments = np.zeros((width, height-1), dtype=bool)
    vertical_segments = np.zeros((width-1, height), dtype=bool)
    print(right_angle_ray_mesurements)
    print(top_ray_mesurements)
    add_horizontal_edges(horizontal_segments, right_angle_ray_mesurements, left_angle_ray_mesurements, width, height)
    add_vertical_edges(vertical_segments, left_angle_ray_mesurements, top_ray_mesurements, width, height)
    add_internal_points(building, horizontal_segments, vertical_segments, right_angle_ray_mesurements, left_angle_ray_mesurements, right_angle_rays, left_angle_rays, width, height)
    print(horizontal_segments)
    print(vertical_segments)
    # print(building.horizontal_lines)
    # print(building.vertical_lines)
    # reorder_right_rays = []

    # for row in range(1, width):
    #     for column in range (height-2, 0):
    #         k_visibility_left = top_ray_mesurements[row - 1 + height]

def add_internal_points(building, horizontal_segments, vertical_segments, right_angle_ray_mesurements, left_angle_ray_mesurements, right_angle_rays, left_angle_rays, width, height):
    # print(vertical_segments)
    # print(horizontal_segments)
    present_segments([building.segments])
    for i in range(width-1):
        for j in range(height-1):
            point = (i,j)
            print(point)
            # find_intersection_rays returns indices into the ray lists
            right_indices, left_indices = find_intersection_rays(point, right_angle_ray_mesurements, left_angle_ray_mesurements, height, width)
            # Build small lists of the two rays that intersect near this internal point
            # right_ray_pair = [right_angle_rays[right_indices[0]], right_angle_rays[right_indices[1]]]
            # left_ray_pair = [left_angle_rays[left_indices[0]], left_angle_rays[left_indices[1]]]
            # present_segments([building.segments, right_ray_pair, left_ray_pair])
            k_visibility_r1 = right_angle_ray_mesurements[right_indices[0]]
            k_visibility_r2 = right_angle_ray_mesurements[right_indices[1]]
            k_visibility_l1 = left_angle_ray_mesurements[left_indices[0]]
            k_visibility_l2 = left_angle_ray_mesurements[left_indices[1]]
            has_line_below = vertical_segments[i,j]
            has_line_left = horizontal_segments[i,j]
            print(k_visibility_r1, k_visibility_r2, k_visibility_l1, k_visibility_l2, has_line_below, has_line_left)
            has_line_above, has_line_right = process_point(k_visibility_r1, k_visibility_r2, k_visibility_l1, k_visibility_l2, has_line_below, has_line_left)
            print(has_line_above, has_line_right)
            vertical_segments[i,j+1] = int(has_line_above)
            horizontal_segments[i+1,j] = int(has_line_right)
            # print(vertical_segments)
            # print(horizontal_segments)
            # continue
            # Present building segments together with the two intersecting rays (each as its own list)
    print(horizontal_segments)
    print(vertical_segments)
            

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
def find_intersection_rays(point, right_angle_ray_mesurements, left_angle_ray_mesurements, height, width):
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

if __name__ == '__main__':
    # building = Building(random.randint(3,6), random.randint(3,6))
    building = Building(4,6)
    building.fill_grid_randomly(0.5)
    print(building.horizontal_lines)
    print(building.vertical_lines)
    top_mesurements = get_top_mesurements(building)
    # print(top_mesurements)
    # left_mesurements = get_left_mesurements(building)
    # print(left_mesurements)
    right_angle_rays, left_angle_rays = create_angled_rays(building.width, building.height)
    right_angle_ray_mesurements, left_angle_ray_mesurements = get_angle_mesurements(right_angle_rays, left_angle_rays, building)
    grid = get_grid_result(building, top_mesurements, right_angle_ray_mesurements, right_angle_rays, left_angle_rays, left_angle_ray_mesurements, building.width, building.height)
    present_segments([building.segments, right_angle_rays, left_angle_rays])
    
    # present_segments([building.segments])
    # get_ray_mesurements = 
    # building.present_grid()
