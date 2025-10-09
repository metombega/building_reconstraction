import tkinter as tk
from tkinter import messagebox
import math

class GridPlayground:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("7x7 Grid Playground")
        self.root.geometry("600x700")
        self.root.resizable(True, True)  # Allow window resizing
        
        # Add maximize button functionality
        self.root.state('normal')  # Start in normal state
        
        # Grid settings
        self.grid_size = 5
        self.cell_size = 90
        self.margin = 50
        
        # Calculate canvas size
        canvas_width = self.grid_size * self.cell_size + 2 * self.margin
        canvas_height = self.grid_size * self.cell_size + 2 * self.margin
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.root, 
            width=canvas_width, 
            height=canvas_height,
            bg='white'
        )
        self.canvas.pack(pady=10)
        
        # Initialize line storage
        # horizontal_lines[row][col] represents line below square at (row, col)
        # vertical_lines[row][col] represents line to the right of square at (row, col)
        # 0 = no line, 1 = black line, 2 = blue line
        self.horizontal_lines = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.vertical_lines = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # External line storage
        self.external_points = []  # List of (x, y) coordinates for external points
        self.external_lines = []   # List of ((x1, y1), (x2, y2)) tuples for direct lines
        self.selected_point = None # Currently selected external point
        
        # Count display state
        self.show_counts = False   # Whether to show row/column line counts
        
        # Pen drawing state
        self.pen_mode = False      # Whether pen drawing mode is active
        self.pen_drawing = False   # Whether currently drawing with pen
        self.last_pen_x = None     # Last pen position x
        self.last_pen_y = None     # Last pen position y
        
        # Bind click events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Initialize display
        self.draw_grid()
        self.draw_lines()
        self.draw_external_elements()
        self.draw_counts()
    
    def count_row_lines(self, row):
        """Count the number of lines in a specific row"""
        count = 0
        # Count only vertical lines in this row (lines that cross through the row)
        for col in range(self.grid_size - 1):
            if self.vertical_lines[row][col] > 0:  # Count both black (1) and blue (2) lines
                count += 1
        return count
    
    def count_column_lines(self, col):
        """Count the number of lines in a specific column"""
        count = 0
        # Count only horizontal lines in this column (lines that cross through the column)
        for row in range(self.grid_size - 1):
            if self.horizontal_lines[row][col] > 0:  # Count both black (1) and blue (2) lines
                count += 1
        return count
    
    def draw_counts(self):
        """Draw row and column line counts if enabled"""
        self.canvas.delete("counts")
        
        if not self.show_counts:
            return
        
        # Draw column counts (above each column)
        for col in range(self.grid_size):
            count = self.count_column_lines(col)
            x = self.margin + col * self.cell_size + self.cell_size // 2
            y = self.margin - 20
            
            # Background circle
            self.canvas.create_oval(
                x - 10, y - 10, x + 10, y + 10,
                fill='lightblue',
                outline='blue',
                width=1,
                tags="counts"
            )
            
            # Count text
            self.canvas.create_text(
                x, y,
                text=str(count),
                fill='black',
                font=('Arial', 10, 'bold'),
                tags="counts"
            )
        
        # Draw row counts (left of each row)
        for row in range(self.grid_size):
            count = self.count_row_lines(row)
            x = self.margin - 20
            y = self.margin + row * self.cell_size + self.cell_size // 2
            
            # Background circle
            self.canvas.create_oval(
                x - 10, y - 10, x + 10, y + 10,
                fill='lightgreen',
                outline='green',
                width=1,
                tags="counts"
            )
            
            # Count text
            self.canvas.create_text(
                x, y,
                text=str(count),
                fill='black',
                font=('Arial', 10, 'bold'),
                tags="counts"
            )
    
    def toggle_counts(self):
        """Toggle the display of row/column counts"""
        self.show_counts = not self.show_counts
        self.draw_counts()
    
    def toggle_perimeter(self):
        """Toggle all perimeter lines (top, bottom, left, right borders) - uses blue lines only"""
        # Check if any perimeter lines exist to determine toggle action
        has_perimeter = self.has_perimeter_lines()
        
        # Set to blue (2) if adding, or 0 if removing
        new_state = 0 if has_perimeter else 2
        
        # Toggle top border (horizontal lines below row 0)
        for col in range(self.grid_size):
            if 0 < self.grid_size - 1:
                self.horizontal_lines[0][col] = new_state
        
        # Toggle bottom border (horizontal lines below the second-to-last row)
        if self.grid_size >= 2:
            for col in range(self.grid_size):
                self.horizontal_lines[self.grid_size - 2][col] = new_state
        
        # Toggle left border (vertical lines to the right of column 0)
        for row in range(self.grid_size):
            if 0 < self.grid_size - 1:
                self.vertical_lines[row][0] = new_state
        
        # Toggle right border (vertical lines to the right of the second-to-last column)
        if self.grid_size >= 2:
            for row in range(self.grid_size):
                self.vertical_lines[row][self.grid_size - 2] = new_state
        
        self.draw_lines()
        self.draw_counts()
    
    def has_perimeter_lines(self):
        """Check if perimeter lines are currently active"""
        # Check top border (horizontal lines below row 0)
        if 0 < self.grid_size - 1:
            for col in range(self.grid_size):
                if self.horizontal_lines[0][col] > 0:
                    return True
        
        # Check bottom border (horizontal lines below second-to-last row)
        if self.grid_size >= 2:
            for col in range(self.grid_size):
                if self.horizontal_lines[self.grid_size - 2][col] > 0:
                    return True
        
        # Check left border (vertical lines to the right of column 0)
        if 0 < self.grid_size - 1:
            for row in range(self.grid_size):
                if self.vertical_lines[row][0] > 0:
                    return True
        
        # Check right border (vertical lines to the right of second-to-last column)
        if self.grid_size >= 2:
            for row in range(self.grid_size):
                if self.vertical_lines[row][self.grid_size - 2] > 0:
                    return True
        
        return False
    
    def toggle_pen_mode(self):
        """Toggle pen drawing mode on/off"""
        self.pen_mode = not self.pen_mode
        # Reset pen state when toggling
        self.pen_drawing = False
        self.last_pen_x = None
        self.last_pen_y = None
        
        # Update cursor and button text to indicate mode
        if self.pen_mode:
            self.canvas.config(cursor="pencil")
            self.pen_btn.config(text="Exit Pen Mode", bg="#006600")
        else:
            self.canvas.config(cursor="")
            self.pen_btn.config(text="Pen Mode", bg="#ff6600")
    
    def clear_pen_drawings(self):
        """Clear all pen drawings from the canvas"""
        self.canvas.delete("pen_drawing")
    
    def draw_grid(self):
        """Draw the 7x7 grid of squares"""
        self.canvas.delete("grid")
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x1 = self.margin + col * self.cell_size
                y1 = self.margin + row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # Draw square outline
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    outline='lightgray',
                    width=1,
                    tags="grid"
                )
    
    def draw_lines(self):
        """Draw all the lines on the grid"""
        self.canvas.delete("lines")
        
        # Draw horizontal lines
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.horizontal_lines[row][col] > 0 and row < self.grid_size - 1:
                    x1 = self.margin + col * self.cell_size
                    x2 = x1 + self.cell_size
                    y = self.margin + (row + 1) * self.cell_size
                    
                    # Choose color based on state
                    color = 'black' if self.horizontal_lines[row][col] == 1 else 'blue'
                    
                    self.canvas.create_line(
                        x1, y, x2, y,
                        fill=color,
                        width=3,
                        tags="lines"
                    )
        
        # Draw vertical lines
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.vertical_lines[row][col] > 0 and col < self.grid_size - 1:
                    y1 = self.margin + row * self.cell_size
                    y2 = y1 + self.cell_size
                    x = self.margin + (col + 1) * self.cell_size
                    
                    # Choose color based on state
                    color = 'black' if self.vertical_lines[row][col] == 1 else 'blue'
                    
                    self.canvas.create_line(
                        x, y1, x, y2,
                        fill=color,
                        width=3,
                        tags="lines"
                    )
    
    def count_line_intersections(self, x1, y1, x2, y2):
        """Count how many grid lines (black or blue) intersect with the given line segment"""
        intersections = 0
        
        # Check intersections with horizontal lines
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.horizontal_lines[row][col] > 0 and row < self.grid_size - 1:  # Count both black and blue
                    # Horizontal line coordinates
                    hx1 = self.margin + col * self.cell_size
                    hx2 = hx1 + self.cell_size
                    hy = self.margin + (row + 1) * self.cell_size
                    
                    # Check if lines intersect
                    if self.lines_intersect(x1, y1, x2, y2, hx1, hy, hx2, hy):
                        intersections += 1
        
        # Check intersections with vertical lines
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if self.vertical_lines[row][col] > 0 and col < self.grid_size - 1:  # Count both black and blue
                    # Vertical line coordinates
                    vy1 = self.margin + row * self.cell_size
                    vy2 = vy1 + self.cell_size
                    vx = self.margin + (col + 1) * self.cell_size
                    
                    # Check if lines intersect
                    if self.lines_intersect(x1, y1, x2, y2, vx, vy1, vx, vy2):
                        intersections += 1
        
        return intersections
    
    def lines_intersect(self, x1, y1, x2, y2, x3, y3, x4, y4):
        """Check if two line segments intersect"""
        # Calculate the direction of the lines
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        
        A = (x1, y1)
        B = (x2, y2)
        C = (x3, y3)
        D = (x4, y4)
        
        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)
    
    def draw_external_elements(self):
        """Draw external points and direct lines with intersection counts"""
        self.canvas.delete("external")
        
        # Draw external lines with intersection counts
        for (x1, y1), (x2, y2) in self.external_lines:
            # Draw the line
            self.canvas.create_line(
                x1, y1, x2, y2,
                fill='green',
                width=3,
                tags="external"
            )
            
            # Count intersections
            intersections = self.count_line_intersections(x1, y1, x2, y2)
            
            # Calculate midpoint for text placement
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            
            # Create background circle for text
            self.canvas.create_oval(
                mid_x - 12, mid_y - 12, mid_x + 12, mid_y + 12,
                fill='white',
                outline='green',
                width=2,
                tags="external"
            )
            
            # Add intersection count text
            self.canvas.create_text(
                mid_x, mid_y,
                text=str(intersections),
                fill='black',
                font=('Arial', 10, 'bold'),
                tags="external"
            )
        
        # Draw external points
        for i, (x, y) in enumerate(self.external_points):
            # Choose color based on selection state
            if i == self.selected_point:
                color = 'red'
                size = 8
            else:
                color = 'orange'
                size = 6
            
            self.canvas.create_oval(
                x - size, y - size, x + size, y + size,
                fill=color,
                outline='black',
                width=2,
                tags="external"
            )
    
    def on_click(self, event):
        """Handle mouse clicks to add/remove lines or select external points"""
        # If in pen mode, start pen drawing
        if self.pen_mode:
            self.pen_drawing = True
            self.last_pen_x = event.x
            self.last_pen_y = event.y
            return
        
        # Calculate which cell was clicked and where
        rel_x = event.x - self.margin
        rel_y = event.y - self.margin
        
        # Check if click is outside grid bounds (external point)
        if (rel_x < 0 or rel_y < 0 or 
            rel_x >= self.grid_size * self.cell_size or 
            rel_y >= self.grid_size * self.cell_size):
            self.handle_external_click(event.x, event.y)
            return
        
        # Calculate grid position
        col = int(rel_x // self.cell_size)
        row = int(rel_y // self.cell_size)
        
        # Calculate position within the cell
        cell_x = rel_x % self.cell_size
        cell_y = rel_y % self.cell_size
        
        # Determine if click is near an edge to add/remove lines
        edge_threshold = 10  # pixels from edge
        
        # Check for horizontal line (bottom edge of cell)
        if (cell_y >= self.cell_size - edge_threshold and 
            row < self.grid_size - 1):
            self.toggle_horizontal_line(row, col)
        
        # Check for vertical line (right edge of cell)
        elif (cell_x >= self.cell_size - edge_threshold and 
              col < self.grid_size - 1):
            self.toggle_vertical_line(row, col)
        
        # Check for horizontal line (top edge of cell)
        elif cell_y <= edge_threshold and row > 0:
            self.toggle_horizontal_line(row - 1, col)
        
        # Check for vertical line (left edge of cell)
        elif cell_x <= edge_threshold and col > 0:
            self.toggle_vertical_line(row, col - 1)
    
    def on_drag(self, event):
        """Handle mouse drag for pen drawing"""
        if self.pen_mode and self.pen_drawing and self.last_pen_x is not None:
            # Draw line from last position to current position
            self.canvas.create_line(
                self.last_pen_x, self.last_pen_y, event.x, event.y,
                fill='red',
                width=2,
                smooth=True,
                tags="pen_drawing"
            )
            self.last_pen_x = event.x
            self.last_pen_y = event.y
    
    def on_release(self, event):
        """Handle mouse button release"""
        if self.pen_mode:
            self.pen_drawing = False
            self.last_pen_x = None
            self.last_pen_y = None
    
    def handle_external_click(self, x, y):
        """Handle clicks outside the grid to create external points and lines"""
        # Check if clicking on an existing external point
        for i, (px, py) in enumerate(self.external_points):
            if abs(x - px) <= 10 and abs(y - py) <= 10:
                # Clicking on existing point
                if self.selected_point is None:
                    self.selected_point = i
                elif self.selected_point == i:
                    # Deselect the same point
                    self.selected_point = None
                else:
                    # Create line between selected point and this point
                    point1 = self.external_points[self.selected_point]
                    point2 = self.external_points[i]
                    
                    # Check if line already exists
                    line_tuple = (point1, point2)
                    reverse_line = (point2, point1)
                    
                    if line_tuple in self.external_lines:
                        # Remove existing line
                        self.external_lines.remove(line_tuple)
                    elif reverse_line in self.external_lines:
                        # Remove existing line (reverse direction)
                        self.external_lines.remove(reverse_line)
                    else:
                        # Add new line
                        self.external_lines.append(line_tuple)
                    
                    self.selected_point = None
                
                self.draw_external_elements()
                return
        
        # Create new external point
        self.external_points.append((x, y))
        
        # If we have a selected point, create a line to the new point
        if self.selected_point is not None:
            point1 = self.external_points[self.selected_point]
            point2 = (x, y)
            self.external_lines.append((point1, point2))
            self.selected_point = None
        
        self.draw_external_elements()
    
    def toggle_horizontal_line(self, row, col):
        """Toggle horizontal line below the specified cell through states: none -> black -> blue -> none"""
        if 0 <= row < self.grid_size - 1 and 0 <= col < self.grid_size:
            # Cycle through states: 0 -> 1 -> 2 -> 0
            self.horizontal_lines[row][col] = (self.horizontal_lines[row][col] + 1) % 3
            self.draw_lines()
            self.draw_counts()
    
    def toggle_vertical_line(self, row, col):
        """Toggle vertical line to the right of the specified cell through states: none -> black -> blue -> none"""
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size - 1:
            # Cycle through states: 0 -> 1 -> 2 -> 0
            self.vertical_lines[row][col] = (self.vertical_lines[row][col] + 1) % 3
            self.draw_lines()
            self.draw_counts()
    
    def clear_all_lines(self):
        """Remove all lines from the grid"""
        self.horizontal_lines = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.vertical_lines = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.draw_lines()
        self.draw_counts()
    
    def clear_external_elements(self):
        """Remove all external points and lines"""
        self.external_points = []
        self.external_lines = []
        self.selected_point = None
        self.draw_external_elements()
    
    def clear_everything(self):
        """Remove all lines, external elements, and pen drawings"""
        self.clear_all_lines()
        self.clear_external_elements()
        self.clear_pen_drawings()
    
    def create_controls(self):
        """Create control buttons"""
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)
        
        clear_lines_btn = tk.Button(
            control_frame, 
            text="Clear Grid Lines", 
            command=self.clear_all_lines,
            font=("Arial", 10),
            bg="#ff4444",
            fg="white",
            padx=15
        )
        clear_lines_btn.pack(side=tk.LEFT, padx=5)
        
        clear_external_btn = tk.Button(
            control_frame, 
            text="Clear External", 
            command=self.clear_external_elements,
            font=("Arial", 10),
            bg="#ff8800",
            fg="white",
            padx=15
        )
        clear_external_btn.pack(side=tk.LEFT, padx=5)
        
        clear_all_btn = tk.Button(
            control_frame, 
            text="Clear Everything", 
            command=self.clear_everything,
            font=("Arial", 10),
            bg="#cc0000",
            fg="white",
            padx=15
        )
        clear_all_btn.pack(side=tk.LEFT, padx=5)
        
        toggle_counts_btn = tk.Button(
            control_frame, 
            text="Toggle Counts", 
            command=self.toggle_counts,
            font=("Arial", 10),
            bg="#00aa00",
            fg="white",
            padx=15
        )
        toggle_counts_btn.pack(side=tk.LEFT, padx=5)
        
        perimeter_btn = tk.Button(
            control_frame, 
            text="Toggle Perimeter", 
            command=self.toggle_perimeter,
            font=("Arial", 10),
            bg="#aa00aa",
            fg="white",
            padx=15
        )
        perimeter_btn.pack(side=tk.LEFT, padx=5)
        
        pen_btn = tk.Button(
            control_frame, 
            text="Pen Mode", 
            command=self.toggle_pen_mode,
            font=("Arial", 10),
            bg="#ff6600",
            fg="white",
            padx=15
        )
        pen_btn.pack(side=tk.LEFT, padx=5)
        
        # Store reference to pen button for text updates
        self.pen_btn = pen_btn
        
        clear_pen_btn = tk.Button(
            control_frame, 
            text="Clear Pen", 
            command=self.clear_pen_drawings,
            font=("Arial", 10),
            bg="#cc4400",
            fg="white",
            padx=15
        )
        clear_pen_btn.pack(side=tk.LEFT, padx=5)
        
        info_btn = tk.Button(
            control_frame, 
            text="How to Use", 
            command=self.show_instructions,
            font=("Arial", 10),
            bg="#4444ff",
            fg="white",
            padx=15
        )
        info_btn.pack(side=tk.LEFT, padx=5)
    
    def show_instructions(self):
        """Show usage instructions"""
        instructions = """How to use the Grid Playground:

GRID LINES (Black/Blue):
1. Click near edges of grid squares to cycle: none → black → blue → none
2. Click near the bottom or right edge of a square to add lines
3. Click on existing lines to change their color or remove them

EXTERNAL LINES (Green):
1. Click outside the grid to create orange points
2. Click on two points to draw green lines between them
3. Click on existing green lines to remove them
4. Red points indicate selected points
5. Numbers on green lines show how many grid lines they cross

PEN DRAWING (Red):
1. Click "Pen Mode" to enable freehand drawing
2. Drag mouse to draw red pen lines anywhere on canvas
3. Click "Exit Pen Mode" to return to normal grid editing
4. Use "Clear Pen" to remove all pen drawings

ROW/COLUMN COUNTS:
- Toggle Counts: Show/hide line counts for each row and column
- Blue circles above columns show column line counts
- Green circles left of rows show row line counts

CONTROLS:
- Clear Grid Lines: Remove only grid lines (black/blue)
- Clear External: Remove only green lines and orange points
- Clear Pen: Remove only red pen drawings
- Clear Everything: Remove all elements
- Toggle Perimeter: Add/remove blue border around entire grid

Tips:
- Pen mode changes cursor to pencil and disables grid editing
- All counting and intersection features work with both black and blue lines
- Use pen drawing for annotations, sketches, or freehand designs!"""
        
        messagebox.showinfo("Instructions", instructions)
    
    def run(self):
        """Start the application"""
        self.create_controls()
        self.root.mainloop()


if __name__ == "__main__":
    # Create and run the grid playground
    app = GridPlayground()
    app.run()
