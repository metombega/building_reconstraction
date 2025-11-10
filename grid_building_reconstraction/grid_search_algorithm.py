from building import GridBuilding 
import random
from tools.k_visibility import count_crossings
from tools.segment_presentation import present_segments

def create_angled_rays(width, height):
    dist_between_rays = 1/(height+1)
    left_angle_rays = []
    for i in range((width + 1)*(height+1) + 1):
        left_angle_rays.append(((i*dist_between_rays - dist_between_rays/2, 0), (i*dist_between_rays + dist_between_rays/2 - 1, height)))
    right_angle_rays = []
    for i in range((width + 1)*(height+1) + 1):
        right_angle_rays.append(((i*dist_between_rays + dist_between_rays/2 - 1, 0), (i*dist_between_rays - dist_between_rays/2, height)))
    return right_angle_rays, left_angle_rays
    
def get_angle_mesurements(right_angle_rays, left_angle_rays, building: GridBuilding):
    right_angle_rays_mesurements = []
    for ray in right_angle_rays:
        right_angle_rays_mesurements.append(count_crossings(ray, building.segments))
    left_angle_rays_mesurements = []
    for ray in left_angle_rays:
        left_angle_rays_mesurements.append(count_crossings(ray, building.segments))
    return right_angle_rays_mesurements, left_angle_rays_mesurements

def get_grid(right_angle_ray_mesurements, left_angle_ray_mesurements, width, height):
    # moving through all points in the grid
    points_directions = find_points_direction(right_angle_ray_mesurements, left_angle_ray_mesurements, width, height)
    segments = find_segments(points_directions, width, height, right_angle_ray_mesurements, left_angle_ray_mesurements)
    return segments

def find_points_direction(right_angle_ray_mesurements, left_angle_ray_mesurements, width, height):
    points_directions = []
    for i in range(width + 1):
        points_directions.append([])
        for j in range(height + 1):
            point = (i,j)
            right_indices, left_indices = find_intersection_rays(point, height, width)
            k_visibility_r1 = right_angle_ray_mesurements[right_indices[0]]
            k_visibility_r2 = right_angle_ray_mesurements[right_indices[1]]
            k_visibility_l1 = left_angle_ray_mesurements[left_indices[0]]
            k_visibility_l2 = left_angle_ray_mesurements[left_indices[1]]
            direction = find_direction(k_visibility_r1, k_visibility_r2, k_visibility_l1, k_visibility_l2)
            points_directions[i].append(direction)
    return points_directions

def find_segments(points_directions, width, height, right_angle_ray_mesurements, left_angle_ray_mesurements):
    segments = []
    # find horizontal segments using directions
    for y in range(height + 1):
        open_point = None
        for x in range(width + 1):
            if points_directions[x][y]['right']:
                open_point = (x,y)
            elif points_directions[x][y]['left']:
                segments.append((open_point, (x, y)))
                assert(open_point != None)
                open_point = None
    # find vertical segments using directions
    for x in range(width + 1):
        open_point = None
        for y in range(height + 1):
            if points_directions[x][y]['up']:
                open_point = (x,y)
            elif points_directions[x][y]['down']:
                segments.append((open_point, (x, y)))
                assert(open_point != None)
                open_point = None
    
    return segments

def find_direction(k_r1, k_r2, k_l1, k_l2):
    ans = {'up': False, 'down': False, 'left': False, 'right': False}
    if k_r1 == k_r2 + 2:
        ans['up'] = True
        ans['left'] = True
    elif k_r1 == k_r2 - 2:
        ans['down'] = True
        ans['right'] = True
    elif k_l1 == k_l2 + 2:
        ans['down'] = True
        ans['left'] = True
    elif k_l1 == k_l2 - 2:
        ans['up'] = True
        ans['right'] = True
    elif k_r1 == k_r2 + 1 and k_l1 == k_l2 + 1:
        ans['left'] = True
    elif k_r1 == k_r2 - 1 and k_l1 == k_l2 + 1:
        ans['down'] = True
    elif k_r1 == k_r2 + 1 and k_l1 == k_l2 - 1:
        ans['up'] = True
    elif k_r1 == k_r2 - 1 and k_l1 == k_l2 - 1:
        ans['right'] = True
    elif abs(k_r1 - k_r2) > 2 or abs(k_l1 - k_l2) > 2:
        print('illigal point')
    return ans

def find_intersection_rays(point, height, width):
    x = point[0]
    y = point[1]
    # compute the indices of the rays that pass near the internal grid point
    r1 = (height+1)*(1 + x) - y - 1
    r2 = (height+1)*(1 + x) - y 
    l1 = (height+1)*x + y
    l2 = (height+1)*x + y + 1
    # Return indices (not the measurement values) so callers can index into the ray lists
    right_indices = [r1, r2]
    left_indices = [l1, l2]
    return right_indices, left_indices

def reconstract_building(building: GridBuilding, presen_results):
    # define the angles to mesure
    right_angle_rays, left_angle_rays = create_angled_rays(building.width, building.height)
    # find the k-visibility for each angle
    right_angle_ray_mesurements, left_angle_ray_mesurements = get_angle_mesurements(right_angle_rays, left_angle_rays, building)
    # reconstract the building using the k-vsibility mesurements
    segments = get_grid(right_angle_ray_mesurements, left_angle_ray_mesurements, building.width, building.height)
    reconstracted_building = GridBuilding(width=building.width, height=building.height, segments=segments)
    # present results
    if presen_results:
        present_segments([building.segments, segments], side_by_side=True, same_scale=False)
    return reconstracted_building

if __name__ == '__main__':
    for _ in range(3):
        # create a random building
        building = GridBuilding(random.randint(4,7), random.randint(4,7), frame=True)
        building.fill_grid_randomly(0.4)
        reconstracted_building = reconstract_building(building, True)
        assert(building.segments == reconstracted_building.segments)
