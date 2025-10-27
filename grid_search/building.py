import sys
from pathlib import Path

# Ensure project root (parent of this file's parent) is on sys.path so sibling
# packages like `tools` can be imported when this file is executed directly.
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
import numpy as np
import random
from tools.segment_presentation import present_segments

class Building():
    def __init__(self, width, height, horizontal_lines=None, vertical_lines=None):
        self.width = width
        self.height = height
        self.segments = []
        if horizontal_lines is None or vertical_lines is None:
            self.horizontal_lines = np.zeros((width,height+1), dtype=bool)
            self.vertical_lines = np.zeros((width+1,height), dtype=bool)
            self.fill_frame()
        else:
            self.horizontal_lines = horizontal_lines
            self.vertical_lines = vertical_lines
        self.update_segments()

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
                if self.horizontal_lines[i][j]:
                    # Found start of a horizontal segment
                    start_i = i
                    # Find the end of consecutive segments
                    while i < self.width and self.horizontal_lines[i][j]:
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
                if self.vertical_lines[i][j]:
                    # Found start of a vertical segment
                    start_j = j
                    # Find the end of consecutive segments
                    while j < self.height and self.vertical_lines[i][j]:
                        j += 1
                    end_j = j
                    # Add merged segment from (i, start_j) to (i, end_j)
                    self.segments.append(((i, start_j), (i, end_j)))
                else:
                    j += 1
        
    def fill_frame(self):
        for i in range(self.width):
            self.horizontal_lines[i][0] = 1
            self.horizontal_lines[i][-1] = 1
        for i in range(self.height):
            self.vertical_lines[0][i] = 1
            self.vertical_lines[-1][i] = 1
    
    def fill_grid_randomly(self, prob=0.1):
        for i in range(self.width):
            for j in range(self.height + 1):
                if random.random()<prob:
                    self.horizontal_lines[i][j] = 1
        for i in range(self.width+1):
            for j in range(self.height):
                if random.random()<prob:
                    self.vertical_lines[i][j] = 1
        self.update_segments()
    
    def present_grid(self):
        present_segments([self.segments])

# def calculate_ray_points(column_start_x, column_end_x, column_height):
if __name__ == '__main__':
    grid = Building(5,3)
    grid.fill_grid_randomly(0.5)
    print(grid.segments)
    grid.present_grid()
    