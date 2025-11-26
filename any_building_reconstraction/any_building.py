
import sys, os

workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import random
import math
from tools.geometric import lines_are_overlap, point_to_line_dist
from tools.segment_presentation import present_segments

class AnyBuilding():
    def __init__(self, width, height,segments: list = None):
        self.width = width
        self.height = height
        # Avoid using a mutable default argument. Create a fresh list per instance.
        self.segments = list(segments) if segments is not None else []
        self.frame_segments = []

    def create_random_building(self, num_of_segments):
        self.add_frame()
        points = self.add_random_points(num_of_segments)
        self.add_random_segments(num_of_segments, points)
    
    def add_random_points(self, num_of_segments, min_dist=1):
        points = []
        while len(points) < num_of_segments*1.25:
            if random.random() < 0 and len(points) >= 2:
                # create a point on an existing line
                p1, p2 = random.sample(points, k=2)
                x1,y1 = p1[0], p1[1]
                x2,y2 = p2[0], p2[1]
                t = random.random()
                x = x1 + (x2 - x1) * t
                y = y1 + (y2 - y1) * t
            else:
                x = random.uniform(0, self.width)
                y = random.uniform(0, self.height)
            point_too_close = False
            for p in points:
                if math.sqrt((p[0] - x)**2 + (p[1]-y)**2) < min_dist:
                    point_too_close = True
            if point_too_close:
                continue
            else:
                points.append((x,y))
        return points

    def seg_legal_check(self, new_segment, min_dist):
        # check if segment is not too close to another segment, or overlaps
        for seg in self.segments:
            if ((point_to_line_dist(seg[0], new_segment) < min_dist
                and point_to_line_dist(seg[0], new_segment) != 0)
                or (point_to_line_dist(seg[1], new_segment) < min_dist 
                and point_to_line_dist(seg[1], new_segment) != 0)
                or (point_to_line_dist(new_segment[0], seg) < min_dist 
                and point_to_line_dist(new_segment[0], seg) != 0)
                or (point_to_line_dist(new_segment[1], seg) < min_dist
                and point_to_line_dist(new_segment[1], seg) != 0)
                or lines_are_overlap(seg, new_segment)):
                    return False
        return True
    
    def add_random_segments(self, num_of_segments, points):
        while len(self.segments) < num_of_segments:
            p1,p2 = random.sample(points, k=2)
            if self.seg_legal_check([p1,p2], 1):
                self.segments.append([p1,p2])

    def add_frame(self):
        self.segments.append([(0,0), (self.width, 0)])
        self.frame_segments.append([(0,0), (self.width, 0)])
        self.segments.append([(self.width, 0), (self.width, self.height)])
        self.frame_segments.append([(self.width, 0), (self.width, self.height)])
        self.segments.append([(self.width, self.height), (0,self.height)])
        self.frame_segments.append([(self.width, self.height), (0,self.height)])
        self.segments.append([(0,self.height), (0,0)])
        self.frame_segments.append([(0,self.height), (0,0)])


if __name__ == '__main__':
    building = AnyBuilding(8,10)
    building.create_random_building(14)
    print(building.segments)
    present_segments([building.segments])