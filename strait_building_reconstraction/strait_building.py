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
        self.horizontal_segments = []
        self.vertical_segments = []
        self.frame_segments = []

    def create_random_building(self, num_of_segments):
            
        self.add_frame()

        while(len(self.segments) < num_of_segments):
            if random.random() < 0.3:
                self.add_rand_seg()
            elif random.random() < 0.8:
                self.add_rand_corner_seg()
            else:
                self.add_rand_t_seg()

    def add_rand_t_seg(self):
        seg_to_connect = random.choice(self.segments)
        reverse = False
        if seg_to_connect in self.horizontal_segments:
            h = random.uniform(self.min_wall_length, self.height/2)
            if seg_to_connect[1][0] - seg_to_connect[0][0] <= 2*self.min_wall_length:
                return
            x1 = random.uniform(seg_to_connect[0][0] + self.min_wall_length, seg_to_connect[1][0] - self.min_wall_length)
            y1 = seg_to_connect[0][1]
            x2 = x1
            if random.random() < 0.5:
                y2 = min(y1 + h, self.height)
            else:
                y2 = max(y1 - h, 0)
                reverse = True
            
        else:
            w = random.uniform(self.min_wall_length, self.width/2)
            if seg_to_connect[1][1] - seg_to_connect[0][1] <= 2*self.min_wall_length:
                return
            x1 = seg_to_connect[0][0]
            y1 = random.uniform(seg_to_connect[0][1] + self.min_wall_length, seg_to_connect[1][1] - self.min_wall_length)
            if random.random() < 0.5:
                x2 = min(x1 + w, self.width)
            else:
                x2 = max(x1 - w, 0)
                reverse = True
            y2 = y1
        if reverse:
            new_segment = [(x2,y2), (x1,y1)]
        else:
            new_segment = [(x1,y1), (x2,y2)]
        if (self.seg_legal_check(new_segment)):
            self.segments.append(new_segment)
            if seg_to_connect in self.horizontal_segments:
                self.vertical_segments.append(new_segment)
            else:
                self.horizontal_segments.append(new_segment)
    
    def add_rand_corner_seg(self):
        seg_to_connect = random.choice(self.segments)
        point_to_connect = random.choice(seg_to_connect)
        reverse = False
        if seg_to_connect in self.horizontal_segments:
            h = random.uniform(self.min_wall_length, self.height/2)
            x2 = point_to_connect[0]
            if random.random() < 0.5:
                y2 = min(point_to_connect[1] + h, self.height)
            else:
                y2 = max(point_to_connect[1] - h, 0)
                reverse = True 
        elif seg_to_connect in self.vertical_segments:
            w = random.uniform(self.min_wall_length, self.width/2)
            y2 = point_to_connect[1]
            if random.random() < 0.5:
                x2 = min(point_to_connect[0] + w, self.width)
            else:
                x2 = max(point_to_connect[0] - w, 0)
                reverse = True
        else: 
            return
        if reverse:
            new_segment = [(x2,y2), point_to_connect]    
        else:
            new_segment = [point_to_connect, (x2,y2)]
        if (self.seg_legal_check(new_segment)):
            self.segments.append(new_segment)
            if seg_to_connect in self.horizontal_segments:
                self.vertical_segments.append(new_segment)
            else:
                self.horizontal_segments.append(new_segment)
         
    def add_rand_seg(self):
        is_horizontal = random.random() < 0.5
        if is_horizontal:
            w = random.uniform(self.min_wall_length, self.width/2)
            x1 = random.uniform(self.min_wall_length, self.width - w - self.min_wall_length)
            y1 = random.uniform(self.min_wall_length, self.height - self.min_wall_length)
            x2 = x1 + w
            y2 = y1
        else:
            h = random.uniform(self.min_wall_length, self.height/2)
            x1 = random.uniform(self.min_wall_length, self.width - self.min_wall_length)
            y1 = random.uniform(self.min_wall_length, self.height - h - self.min_wall_length)
            x2 = x1
            y2 = y1 + h
        new_segment = [(x1, y1), (x2, y2)]
        
        if (self.seg_legal_check(new_segment)):
            self.segments.append(new_segment)
            if is_horizontal:
                self.horizontal_segments.append(new_segment)
            else:
                self.vertical_segments.append(new_segment)
    
    def add_frame(self):
        self.segments.append([(0,0), (self.width, 0)])
        # self.horizontal_segments.append([(0,0), (self.width, 0)])
        self.frame_segments.append([(0,0), (self.width, 0)])
        self.segments.append([(self.width, 0), (self.width, self.height)])
        # self.vertical_segments.append([(self.width, 0), (self.width, self.height)])
        self.frame_segments.append([(self.width, 0), (self.width, self.height)])
        self.segments.append([(self.width, self.height), (0,self.height)])
        # self.horizontal_segments.append([(self.width, self.height), (0,self.height)])
        self.frame_segments.append([(self.width, self.height), (0,self.height)])
        self.segments.append([(0,self.height), (0,0)])
        # self.vertical_segments.append([(0,self.height), (0,0)])
        self.frame_segments.append([(0,self.height), (0,0)])

    def seg_legal_check(self, new_segment):
        # check if segment is not too close to another segment
        for seg in self.segments:
            if (point_to_line_dist(seg[0], new_segment) < self.min_wall_length
                and point_to_line_dist(seg[0], new_segment) != 0
                or point_to_line_dist(seg[1], new_segment) < self.min_wall_length 
                and point_to_line_dist(seg[1], new_segment) != 0
                or point_to_line_dist(new_segment[0], seg) < self.min_wall_length 
                and point_to_line_dist(new_segment[0], seg) != 0
                or point_to_line_dist(new_segment[1], seg) < self.min_wall_length
                and point_to_line_dist(new_segment[1], seg) != 0):
                return False
        return True
    
    # def move_point_from_edge(self, x, y):
    #     if x < self.min_wall_length:
    #         if x < self.min_wall_length/2:
    #             x = 0
    #         else:
    #             x = self.min_wall_length
        
    #     elif x > self.width - self.min_wall_length:
    #         if x > self.width - self.min_wall_length/2:
    #             x = self.width
    #         else:
    #             x = self.width - self.min_wall_length

    #     if y < self.min_wall_length:
    #         if y < self.min_wall_length/2:
    #             y = 0
    #         else:
    #             y = self.min_wall_length
        
    #     if y > self.height - self.min_wall_length:
    #         if y > self.height - self.min_wall_length/2:
    #             y = self.height
    #         else:
    #             y = self.height - self.min_wall_length
    #     return x, y

    # def frame_check(self, x1, x2, y1, y2):
    #     # check segment is not too close to the frame
    #     x1, y1 = self.move_point_from_edge(x1, y1)
    #     x2, y2 = self.move_point_from_edge(x2, y2)
        
    #     return [(x1,y1), (x2,y2)]

if __name__ == '__main__':
    building = StraitBuilding(10,8)
    building.create_random_building(14)
    print(building.segments)
    present_segments([building.segments])
