from multiprocessing import Pool
from any_building import AnyBuilding
from tools.confirm_dist_calculation import calculate_dist
from tools.segment_presentation import present_segments
from tools.k_visibility import count_crossings
from tools.geometric import center_of_three_parallel_pairs, combine_close_points
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


def find_external_rays(p1,p2,dist_between_rays,width,height):
    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    y0 = p1[1] - m*p1[0]
    
    if m > 1 or m < -1:
        x1 = -y0 / m
        y1 = 0
        x2 = (height - y0) / m
        y2 = height
        ray1 = [(x1 - dist_between_rays, y1), (x2 - dist_between_rays, y2)]
        ray2 = [(x1 + dist_between_rays, y1), (x2 + dist_between_rays, y2)]
        
    else:
        x1 = 0
        y1 = y0
        x2 = width
        y2 = y0 + m * width
        ray1 = [(x1, y1 - dist_between_rays), (x2, y2 - dist_between_rays)]
        ray2 = [(x1, y1 + dist_between_rays), (x2, y2 + dist_between_rays)]
    return ray1, ray2

def find_internal_rays(p1, p2, exray1, exray2, width, height):
    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    mid_point = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    if m > 1 or m < -1:
        if mid_point[1] > height / 2:
            t = height / mid_point[1]
            ray1 = [(exray1[0][0], 0), (exray1[0][0] + t * (mid_point[0] - exray1[0][0]), height)] 
            ray2 = [(exray2[0][0], 0), (exray2[0][0] + t * (mid_point[0] - exray2[0][0]), height)]
        else:
            t = height / mid_point[1]
            ray1 = [(exray1[1][0], height), ((exray1[1][0] - t * mid_point[0]) / (1 - t), 0)] 
            ray2 = [(exray2[1][0], height), ((exray2[1][0] - t * mid_point[0]) / (1 - t), 0)]
    else:
        if mid_point[0] > width / 2:
            t = width / mid_point[0]
            ray1 = [(0, exray1[0][1]), (width, exray1[0][1] + t * (mid_point[1] - exray1[0][1]))] 
            ray2 = [(0, exray2[0][1]), (width, exray2[0][1] + t * (mid_point[1] - exray2[0][1]))]
        else:
            t = width / mid_point[0]
            ray1 = [(width, exray1[1][1]), (0, (exray1[1][1] - t * mid_point[1]) / (1 - t))] 
            ray2 = [(width, exray2[1][1]), (0, (exray2[1][1] - t * mid_point[1]) / (1 - t))]
    return ray1, ray2

def is_segment_there(p1, p2, dist_between_rays, building):
    exray1, exray2 = find_external_rays(p1, p2, dist_between_rays, building.width, building.height)
    inray1, inray2 = find_internal_rays(p1, p2, exray1, exray2, building.width, building.height)
    mesurements = get_angle_mesurements([exray1, exray2, inray1, inray2], building)
    if mesurements[0] + mesurements[1] + 2 == mesurements[2] + mesurements[3]:
        return True
    else:
        return False
    

def reconstract_building(building: AnyBuilding, present_results=False):
    # we assume one wall every 4 meters 
    estimated_num_of_walls = int(building.width * building.height / 9)
    # this will return the distance between each ray we want to mesure
    dist_between_rays = calculate_dist(building.width, building.height, estimated_num_of_walls, 0.99)
    print(dist_between_rays)
    num_of_angles = 9
    all_rays = []
    for i in range(num_of_angles):
        angle = i * math.pi / num_of_angles
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
    all_intersections = []
    n = len(key_rays)
    for i in range(n):
        angle_intersections = find_triple_intersections(key_rays[(i) % n], key_rays[(i+1) % n], key_rays[(i+2) % n], building.width, building.height)
        intersections.append([a['point'] for a in angle_intersections])
        all_intersections.extend([a['point'] for a in angle_intersections])
    all_intersections = combine_close_points(all_intersections, dist_between_rays*4)
    segments = []
    for i in range(len(all_intersections) - 1):
        for j in range(i+1, len(all_intersections)):
            if is_segment_there(all_intersections[i], all_intersections[j], dist_between_rays, building):
                segments.append([all_intersections[i],all_intersections[j]])
            
    if present_results:
        present_segments([building.segments, segments], side_by_side=True, same_scale=False)

    return None

if __name__ == '__main__':

    # import json
    # with open("data.json", "r") as f:
    #     data = json.load(f)
    # building = StraitBuilding(8, 10, 1, data)
    # reconstracted_building = reconstract_building(building, True)
    for _ in range(1):
        building = AnyBuilding(8, 10)
        building.create_random_building(12)
    #     building.segments = [
    #     ((0, 0), (8, 0)),
    #     ((8, 0), (8, 10)),
    #     ((8, 10), (0, 10)),
    #     ((0, 10), (0, 0)),
    #     ((5.778027418280737, 3.6221263865376265), (3.0294874811259414, 1.567961185216555)),
    #     ((0.34063599801817634, 8.512395982072805), (3.0294874811259414, 1.567961185216555)),
    #     ((6.945695347938577, 3.6434546120961544), (5.830982134140663, 3.696774243762092)),
    #     ((5.377475144342135, 3.462178330389297), (0.34063599801817634, 8.512395982072805)), # inray
    # ]
        
        reconstracted_building = reconstract_building(building, True)

