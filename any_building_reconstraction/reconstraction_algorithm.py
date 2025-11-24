from multiprocessing import Pool
from any_building import AnyBuilding
from tools.confirm_dist_calculation import calculate_dist
from tools.segment_presentation import present_segments
from tools.k_visibility import count_crossings
from tools.geometric import center_of_three_parallel_pairs
from shapely.geometry import Point, LineString
from tqdm import tqdm
import math

def create_rays(width, height, dist_between_rays ,angle):
    if angle == 0:
        angle_dist = 0
    else:
        angle_dist = height / math.tan(angle)
    rays = []
    if angle < math.pi/2:
        for i in range(int((width + angle_dist)//dist_between_rays) + 3):
            x1 = i*dist_between_rays - angle_dist - dist_between_rays/2
            x2 = x1 + angle_dist
            rays.append([(x1,0), (x2,height)])
    else:
        for i in range(int((width - angle_dist)//dist_between_rays) + 3):
            x1 = i*dist_between_rays - dist_between_rays/2
            x2 = x1 + angle_dist
            rays.append([(x1,0), (x2,height)])
    return rays

def get_angle_mesurements(rays, building: AnyBuilding):
    mesurements = []
    for ray in tqdm(rays):
        mesurements.append(count_crossings(ray, building.segments))
    return mesurements


def find_key_rays(rays, mesure):
    key_couples = []
    for i in range(len(mesure) - 1):
        if mesure[i] != mesure[i+1]:

            key_couples.append({'rays': (rays[i], rays[i+1]), 'mesure': (mesure[i], mesure[i+1])})
            # assert(abs(mesure[i] - mesure[i+1]) <= 2)
    return key_couples


def find_triple_intersections(rays1, rays2, rays3, width, height):
    points = []
    min_dist = 0.1
    for ray1 in tqdm(rays1):
        for ray2 in rays2:
            for ray3 in rays3:
                p = center_of_three_parallel_pairs(ray1['rays'][0], ray1['rays'][1], ray2['rays'][0], ray2['rays'][1], ray3['rays'][0], ray3['rays'][1])
                if p:
                    if p[0] > -1*min_dist and p[1] > -1*min_dist and p[0] < width + min_dist and p[1] < height + min_dist:
                        points.append({'rays': [ray1['rays'], ray2['rays'], ray3['rays']], 'mesure':[ray1['mesure'], ray2['mesure'], ray3['mesure']], 'point': p})
    return points


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
    else:
        print('illigal point')
    return ans


def find_segments(intersections_r: list, intersections_l: list, dist_between_rays):
    all_points = []

    # find non corner points
    for p1 in intersections_r:
        for p2 in intersections_l:
            point1 = Point(p1['point'])
            point2 = Point(p2['point'])
            if point1.distance(point2) < 4*dist_between_rays:
                new_point = ((point1.x+point2.x)/2, (point1.y+point2.y)/2)
                direction = find_direction(p1['mesure'][0][0], p1['mesure'][0][1], p2['mesure'][0][0], p2['mesure'][0][1])
                all_points.append({'point': new_point, 'direction': direction})
                p1['found'] = True
                p2['found'] = True
                break

    # find corner points
    for p in intersections_r:
        if 'found' not in p.keys():
            direction = find_direction(p['mesure'][0][0], p['mesure'][0][1], 0, 0)
            all_points.append({'point': p['point'], 'direction': direction})
    for p in intersections_l:
        if 'found' not in p.keys():
            direction = find_direction(0, 0, p['mesure'][0][0], p['mesure'][0][1])
            all_points.append({'point': p['point'], 'direction': direction})

    # find segments using directions
    segments = []
    for i in range(len(all_points) - 1):
        for j in range(i+1, len(all_points)):
            if abs(all_points[i]['point'][0] - all_points[j]['point'][0]) < 4*dist_between_rays:
                if (all_points[i]['direction']['up'] and all_points[j]['direction']['down']
                    or all_points[i]['direction']['down'] and all_points[j]['direction']['up']):
                    segments.append([all_points[i]['point'], all_points[j]['point']])
            elif abs(all_points[i]['point'][1] - all_points[j]['point'][1]) < 4*dist_between_rays:
                if (all_points[i]['direction']['left'] and all_points[j]['direction']['right']
                    or all_points[i]['direction']['right'] and all_points[j]['direction']['left']):
                    segments.append([all_points[i]['point'], all_points[j]['point']])

    return segments

def reconstract_building(building: AnyBuilding, present_results=False):
    # we assume one wall every 4 meters 
    estimated_num_of_walls = int(building.width * building.height / 9)
    # this will return the distance between each ray we want to mesure
    dist_between_rays = calculate_dist(building.width, building.height, estimated_num_of_walls, 0.99)

    num_of_angles = 9
    all_rays = []
    for i in range(num_of_angles):
        angle = i * (math.pi / 2) / num_of_angles
        angle_rays = create_rays(building.width, building.height, dist_between_rays=dist_between_rays ,angle=angle)
        all_rays.append(angle_rays)
    
    # find the k-visibility for each angle
    inputs = []
    for ray in all_rays:
        inputs.append((ray, building))
    with Pool(processes=6) as pool:
        mesurements = pool.starmap(get_angle_mesurements, inputs)
    
    key_rays = []
    for i in range(len(all_rays)):
        key_rays.append(find_key_rays(all_rays[i], mesurements[i]))

    intersections = []
    for i in range(len(key_rays)-2):
        angle_intersections = find_triple_intersections(key_rays[i], key_rays[i+1], key_rays[i+2], building.width, building.height)
        intersections.append([a['point'] for a in angle_intersections])
    
    
    
    # segments = find_segments(intersections, dist_between_rays)
    if present_results:
        present_segments([building.segments], points_lists=intersections)

    return None

if __name__ == '__main__':

    # import json
    # with open("data.json", "r") as f:
    #     data = json.load(f)
    # building = StraitBuilding(8, 10, 1, data)
    # reconstracted_building = reconstract_building(building, True)
    for _ in range(3):
        building = AnyBuilding(8, 10)
        building.create_random_building(14)
        
        reconstracted_building = reconstract_building(building, True)

