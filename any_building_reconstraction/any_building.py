import sys, os
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import random
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
    
    def add_random_points(self, num_of_segments):
        points = []
        for _ in range(num_of_segments*2):
            if random.random() < 0.5 and len(points) >= 2:
                # create a point on an existing line
                p1, p2 = random.choices(points, k=2)
                x1,y1 = p1[0], p1[1]
                x2,y2 = p2[0], p2[1]
                t = random.random()
                x = x1 + (x2 - x1) * t
                y = y1 + (y2 - y1) * t
            else:
                x = random.uniform(0, self.width)
                y = random.uniform(0, self.height)
            points.append((x,y))
        return points

    def add_random_segments(self, num_of_segments, points):
        while len(self.segments) < num_of_segments:
            p1,p2 = random.choices(points, k=2)
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