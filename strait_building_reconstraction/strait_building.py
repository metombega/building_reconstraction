import sys, os
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import numpy as np
import random
from tools.geometric import point_to_line_dist, point_to_point_dist
from tools.segment_presentation import present_segments

class StraitBuilding():
    def __init__(self, width, height, min_wall_length=1, segments: list=[]):
        self.width = width
        self.height = height
        self.min_wall_length = min_wall_length
        self.segments = segments

    def create_random_building(self, num_of_segments):
        
        while(len(self.segments) < num_of_segments):
            if len(self.segments) % 2 == 0:
                w = random.uniform(0, self.width)/2
                x1 = random.uniform(0, self.width - w)
                y1 = random.uniform(0, self.height)
                x2 = x1 + w
                y2 = y1
            else:
                h = random.uniform(0, self.height)/2
                x1 = random.uniform(0, self.width)
                y1 = random.uniform(0, self.height - h)
                x2 = x1
                y2 = y1 + h
            new_segment = self.frame_check(x1, x2, y1, y2)
            
            if (self.seg_legal_check(new_segment) and 
                point_to_point_dist(new_segment[0], new_segment[1]) >= self.min_wall_length):
                self.segments.append(new_segment)
        self.add_frame()
    
    def add_frame(self):
        self.segments.append([(0,0), (self.width, 0)])
        self.segments.append([(self.width, 0), (self.width, self.height)])
        self.segments.append([(self.width, self.height), (0,self.height)])
        self.segments.append([(0,self.height), (0,0)])

    def seg_legal_check(self, new_segment):
        # check if segment is not too close to another segment
        for seg in self.segments:
            if (point_to_line_dist(seg[0], new_segment) < self.min_wall_length 
                or point_to_line_dist(seg[1], new_segment) < self.min_wall_length 
                or point_to_line_dist(new_segment[0], seg) < self.min_wall_length 
                or point_to_line_dist(new_segment[1], seg) < self.min_wall_length):
                return False
        return True
    
    def move_point_from_edge(self, x, y):
        if x < self.min_wall_length:
            if x < self.min_wall_length/2:
                x = 0
            else:
                x = self.min_wall_length
        
        elif x > self.width - self.min_wall_length:
            if x > self.width - self.min_wall_length/2:
                x = self.width
            else:
                x = self.width - self.min_wall_length

        if y < self.min_wall_length:
            if y < self.min_wall_length/2:
                y = 0
            else:
                y = self.min_wall_length
        
        if y > self.height - self.min_wall_length:
            if y > self.height - self.min_wall_length/2:
                y = self.height
            else:
                y = self.height - self.min_wall_length
        return x, y

    def frame_check(self, x1, x2, y1, y2):
        # check segment is not too close to the frame
        x1, y1 = self.move_point_from_edge(x1, y1)
        x2, y2 = self.move_point_from_edge(x2, y2)
        
        return [(x1,y1), (x2,y2)]

if __name__ == '__main__':
    building = StraitBuilding(10,8)
    building.create_random_building(8)
    print(building.segments)
    present_segments([building.segments])
