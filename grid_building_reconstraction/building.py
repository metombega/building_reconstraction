import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import numpy as np
import random
from tools.segment_presentation import present_segments

class GridBuilding():
    def __init__(self, width, height, frame=True, segments=None):
        self.width = width
        self.height = height
        self.segments = segments
        if segments is None:
            self._horizontal_lines = np.zeros((width,height+1), dtype=bool)
            self._vertical_lines = np.zeros((width+1,height), dtype=bool)
            self.fill_grid_randomly()
            if frame:
                self.fill_frame()

    def update_segments(self):
        """
        Returns merged line segments from the grid.
        Continuous horizontal and vertical segments are merged into longer segments.
        """
        self.segments = []
        # Process horizontal lines - merge consecutive horizontal segments
        for j in range(self.height + 1):  # for each row
            i = 0
            while i < self.width:
                if self._horizontal_lines[i][j]:
                    # Found start of a horizontal segment
                    start_i = i
                    # Find the end of consecutive segments
                    while i < self.width and self._horizontal_lines[i][j]:
                        i += 1
                    end_i = i
                    # Add merged segment from (start_i, j) to (end_i, j)
                    self.segments.append(((start_i, j), (end_i, j)))
                else:
                    i += 1
        
        # Process vertical lines - merge consecutive vertical segments  
        for i in range(self.width + 1):  # for each column
            j = 0
            while j < self.height:
                if self._vertical_lines[i][j]:
                    # Found start of a vertical segment
                    start_j = j
                    # Find the end of consecutive segments
                    while j < self.height and self._vertical_lines[i][j]:
                        j += 1
                    end_j = j
                    # Add merged segment from (i, start_j) to (i, end_j)
                    self.segments.append(((i, start_j), (i, end_j)))
                else:
                    j += 1
        
    def fill_frame(self):
        for i in range(self.width):
            self._horizontal_lines[i][0] = 1
            self._horizontal_lines[i][-1] = 1
        for i in range(self.height):
            self._vertical_lines[0][i] = 1
            self._vertical_lines[-1][i] = 1
        self.update_segments()
    
    def fill_grid_randomly(self, prob=0.1):
        for i in range(self.width):
            for j in range(self.height + 1):
                if random.random()<prob:
                    self._horizontal_lines[i][j] = 1
        for i in range(self.width+1):
            for j in range(self.height):
                if random.random()<prob:
                    self._vertical_lines[i][j] = 1
        self.update_segments()


# def calculate_ray_points(column_start_x, column_end_x, column_height):
if __name__ == '__main__':
    grid = GridBuilding(5,3)
    present_segments([grid.segments])
    