import tkinter as tk
from tkinter import messagebox, colorchooser
import math

class LineDrawingApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Line Drawing Canvas")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Drawing settings
        self.line_color = "black"
        self.line_width = 2
        
        # Canvas
        self.canvas_width = 750
        self.canvas_height = 600
        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='white',
            bd=2,
            relief='sunken'
        )
        self.canvas.pack(pady=10, padx=10)
        
        # Drawing state
        self.points = []  # Store all placed points
        self.selected_points = []  # Points selected for connecting
        self.lines = []  # Store all drawn lines
        self.point_radius = 4  # Radius for drawing points
        
        # Measurement lines
        self.measurement_lines = {'vertical': [], 'horizontal': []}
        self.intersection_counts = {'vertical': [0] * 7, 'horizontal': [0] * 7}
        
        # Pen drawing mode
        self.pen_mode = False
        self.pen_drawing = False
        self.pen_last_x = None
        self.pen_last_y = None
        self.pen_strokes = []  # Store pen stroke canvas IDs
        
        # Eraser mode
        self.eraser_mode = False
        
        # Create measurement lines
        self.create_measurement_lines()
        
        # Control frame
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=5)
        
        # Create control buttons and widgets
        self.create_controls()
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.connect_points)  # Right-click to connect
        
        # Bind keyboard events
        self.root.bind("<Control-z>", self.undo_last_action)
        self.root.bind("<Delete>", self.clear_canvas)
        self.root.bind("<c>", self.connect_selected_points)  # 'c' key to connect
        self.root.focus_set()  # Allow keyboard events
        
    def create_controls(self):
        """Create control buttons and settings"""
        # Color selection
        color_button = tk.Button(
            self.control_frame,
            text="Choose Color",
            command=self.choose_color,
            bg=self.line_color,
            width=12
        )
        color_button.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_button = tk.Button(
            self.control_frame,
            text="Clear All",
            command=self.clear_canvas,
            bg="#ffcccc",
            width=10
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Undo button
        undo_button = tk.Button(
            self.control_frame,
            text="Undo",
            command=self.undo_last_action,
            bg="#ccffcc",
            width=8
        )
        undo_button.pack(side=tk.LEFT, padx=5)
        
        # Connect button
        connect_button = tk.Button(
            self.control_frame,
            text="Connect Points",
            command=self.connect_selected_points,
            bg="#ffffcc",
            width=12
        )
        connect_button.pack(side=tk.LEFT, padx=5)
        
        # Pen mode toggle button
        self.pen_button = tk.Button(
            self.control_frame,
            text="Pen Mode OFF",
            command=self.toggle_pen_mode,
            bg="#ffeeee",
            width=12
        )
        self.pen_button.pack(side=tk.LEFT, padx=5)
        
        # Eraser mode toggle button
        self.eraser_button = tk.Button(
            self.control_frame,
            text="Eraser OFF",
            command=self.toggle_eraser_mode,
            bg="#ffeeff",
            width=10
        )
        self.eraser_button.pack(side=tk.LEFT, padx=5)
        
        # Info label
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)
        
        info_text = "Left-click to place points • Right-click on points to select/connect • 'C' key to connect selected • Ctrl+Z to undo • Toggle Pen/Eraser modes"
        self.info_label = tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 9),
            fg="gray"
        )
        self.info_label.pack()
        
        # Point and line count label
        self.count_label = tk.Label(
            info_frame,
            text="Points: 0 | Lines: 0",
            font=("Arial", 9),
            fg="blue"
        )
        self.count_label.pack()
    
    def create_measurement_lines(self):
        """Create 7 vertical and 7 horizontal measurement lines with count labels"""
        # Spacing for the measurement lines
        v_spacing = self.canvas_width / 8  # 8 spaces for 7 lines
        h_spacing = self.canvas_height / 8  # 8 spaces for 7 lines
        
        # Create vertical measurement lines
        for i in range(7):
            x = v_spacing * (i + 1)
            line_id = self.canvas.create_line(
                x, 0, x, self.canvas_height,
                fill="lightgray", width=1, dash=(5, 5)
            )
            
            # Add count label at the top of vertical line
            text_id = self.canvas.create_text(
                x, 15,
                text="0",
                fill="red",
                font=("Arial", 10, "bold")
            )
            
            self.measurement_lines['vertical'].append({
                'canvas_id': line_id,
                'text_id': text_id,
                'x': x,
                'index': i
            })
        
        # Create horizontal measurement lines  
        for i in range(7):
            y = h_spacing * (i + 1)
            line_id = self.canvas.create_line(
                0, y, self.canvas_width, y,
                fill="lightgray", width=1, dash=(5, 5)
            )
            
            # Add count label to the left of horizontal line
            text_id = self.canvas.create_text(
                15, y,
                text="0",
                fill="blue",
                font=("Arial", 10, "bold")
            )
            
            self.measurement_lines['horizontal'].append({
                'canvas_id': line_id,
                'text_id': text_id,
                'y': y,
                'index': i
            })
        
    def choose_color(self):
        """Open color chooser dialog"""
        color = colorchooser.askcolor(initialcolor=self.line_color)[1]
        if color:
            self.line_color = color
            # Update button color
            for widget in self.control_frame.winfo_children():
                if isinstance(widget, tk.Button) and widget.cget("text") == "Choose Color":
                    widget.config(bg=self.line_color)
                    break
    
    def toggle_pen_mode(self):
        """Toggle between pen mode and point mode"""
        self.pen_mode = not self.pen_mode
        
        if self.pen_mode:
            self.pen_button.config(text="Pen Mode ON", bg="#ccffcc")
        else:
            self.pen_button.config(text="Pen Mode OFF", bg="#ffeeee")
            # Reset pen drawing state
            self.pen_drawing = False
            self.pen_last_x = None
            self.pen_last_y = None
    
    def toggle_eraser_mode(self):
        """Toggle eraser mode on/off"""
        self.eraser_mode = not self.eraser_mode
        
        if self.eraser_mode:
            self.eraser_button.config(text="Eraser ON", bg="#ffcccc")
            # Turn off pen mode when eraser is on
            if self.pen_mode:
                self.pen_mode = False
                self.pen_button.config(text="Pen Mode OFF", bg="#ffeeee")
        else:
            self.eraser_button.config(text="Eraser OFF", bg="#ffeeff")
    
    def on_click(self, event):
        """Handle mouse click - dispatch to pen, eraser, or point mode"""
        if self.eraser_mode:
            self.erase_at_position(event)
        elif self.pen_mode:
            self.start_pen_drawing(event)
        else:
            self.place_point(event)
    
    def on_drag(self, event):
        """Handle mouse drag - only for pen mode"""
        if self.pen_mode and self.pen_drawing:
            self.continue_pen_drawing(event)
    
    def on_release(self, event):
        """Handle mouse release - only for pen mode"""
        if self.pen_mode:
            self.end_pen_drawing(event)
    
    def start_pen_drawing(self, event):
        """Start pen drawing"""
        self.pen_drawing = True
        self.pen_last_x = event.x
        self.pen_last_y = event.y
    
    def continue_pen_drawing(self, event):
        """Continue pen drawing with line segments"""
        if self.pen_last_x is not None and self.pen_last_y is not None:
            # Draw line from last position to current position
            line_id = self.canvas.create_line(
                self.pen_last_x, self.pen_last_y,
                event.x, event.y,
                fill=self.line_color,
                width=1,
                capstyle=tk.ROUND,
                smooth=True
            )
            self.pen_strokes.append(line_id)
            
            # Update last position
            self.pen_last_x = event.x
            self.pen_last_y = event.y
    
    def end_pen_drawing(self, event):
        """End pen drawing"""
        self.pen_drawing = False
        self.pen_last_x = None
        self.pen_last_y = None
    
    def erase_at_position(self, event):
        """Erase only pen strokes at the clicked position"""
        x, y = event.x, event.y
        erase_radius = 10  # Pixels around click to check for elements
        
        # Check for pen strokes to erase
        pen_strokes_to_remove = []
        for stroke_id in self.pen_strokes:
            coords = self.canvas.coords(stroke_id)
            if len(coords) >= 4:  # Line has start and end points
                x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                # Check if click is near the line
                if self.point_near_line(x, y, x1, y1, x2, y2, erase_radius):
                    pen_strokes_to_remove.append(stroke_id)
        
        # Remove pen strokes
        for stroke_id in pen_strokes_to_remove:
            self.canvas.delete(stroke_id)
            self.pen_strokes.remove(stroke_id)
        
        # No need to update intersection counts since pen strokes don't affect them
    
    def point_near_line(self, px, py, x1, y1, x2, y2, threshold):
        """Check if point (px, py) is within threshold distance of line from (x1,y1) to (x2,y2)"""
        # Calculate distance from point to line segment
        line_length_sq = (x2 - x1)**2 + (y2 - y1)**2
        
        if line_length_sq == 0:
            # Line is actually a point
            return ((px - x1)**2 + (py - y1)**2)**0.5 <= threshold
        
        # Calculate the parameter t for the closest point on the line
        t = max(0, min(1, ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / line_length_sq))
        
        # Find the closest point on the line segment
        closest_x = x1 + t * (x2 - x1)
        closest_y = y1 + t * (y2 - y1)
        
        # Calculate distance from point to closest point on line
        distance = ((px - closest_x)**2 + (py - closest_y)**2)**0.5
        
        return distance <= threshold
    
    def line_intersects_vertical(self, x1, y1, x2, y2, vx):
        """Check if line segment intersects with vertical line at x=vx"""
        # Check if vertical line is within x range of segment
        if min(x1, x2) <= vx <= max(x1, x2):
            # Avoid division by zero for vertical segments
            if abs(x2 - x1) < 1e-10:
                return False
            # Calculate y intersection point
            t = (vx - x1) / (x2 - x1)
            y_intersect = y1 + t * (y2 - y1)
            # Check if intersection is within canvas bounds
            return 0 <= y_intersect <= self.canvas_height
        return False
    
    def line_intersects_horizontal(self, x1, y1, x2, y2, hy):
        """Check if line segment intersects with horizontal line at y=hy"""
        # Check if horizontal line is within y range of segment
        if min(y1, y2) <= hy <= max(y1, y2):
            # Avoid division by zero for horizontal segments
            if abs(y2 - y1) < 1e-10:
                return False
            # Calculate x intersection point
            t = (hy - y1) / (y2 - y1)
            x_intersect = x1 + t * (x2 - x1)
            # Check if intersection is within canvas bounds
            return 0 <= x_intersect <= self.canvas_width
        return False
    
    def count_all_intersections(self):
        """Count intersections of all drawn lines with measurement lines"""
        # Reset counts
        self.intersection_counts = {'vertical': [0] * 7, 'horizontal': [0] * 7}
        
        # Count intersections for each drawn line
        for line in self.lines:
            point1 = self.points[line['start_point']]
            point2 = self.points[line['end_point']]
            
            x1, y1 = point1['x'], point1['y']
            x2, y2 = point2['x'], point2['y']
            
            # Check intersections with vertical measurement lines
            for v_line in self.measurement_lines['vertical']:
                if self.line_intersects_vertical(x1, y1, x2, y2, v_line['x']):
                    self.intersection_counts['vertical'][v_line['index']] += 1
            
            # Check intersections with horizontal measurement lines
            for h_line in self.measurement_lines['horizontal']:
                if self.line_intersects_horizontal(x1, y1, x2, y2, h_line['y']):
                    self.intersection_counts['horizontal'][h_line['index']] += 1
        
        self.update_intersection_display()
    
    def place_point(self, event):
        """Place a new point at the clicked location"""
        x, y = event.x, event.y
        
        # Check if clicking near an existing point
        for i, point in enumerate(self.points):
            distance = math.sqrt((x - point['x'])**2 + (y - point['y'])**2)
            if distance <= self.point_radius * 2:  # Click within point area
                self.toggle_point_selection(i)
                return
        
        # Create new point
        point_id = self.canvas.create_oval(
            x - self.point_radius, y - self.point_radius,
            x + self.point_radius, y + self.point_radius,
            fill="red", outline="darkred", width=2
        )
        
        point_info = {
            'canvas_id': point_id,
            'x': x,
            'y': y,
            'selected': False
        }
        
        self.points.append(point_info)
        self.update_counts()
    
    def toggle_point_selection(self, point_index):
        """Toggle selection state of a point"""
        point = self.points[point_index]
        point['selected'] = not point['selected']
        
        # Update visual appearance
        if point['selected']:
            self.canvas.itemconfig(point['canvas_id'], fill="blue", outline="darkblue")
            if point_index not in self.selected_points:
                self.selected_points.append(point_index)
        else:
            self.canvas.itemconfig(point['canvas_id'], fill="red", outline="darkred")
            if point_index in self.selected_points:
                self.selected_points.remove(point_index)
        
        self.update_counts()
    
    def connect_points(self, event):
        """Right-click handler - select point or connect if 2+ selected"""
        x, y = event.x, event.y
        
        # Check if clicking on a point
        for i, point in enumerate(self.points):
            distance = math.sqrt((x - point['x'])**2 + (y - point['y'])**2)
            if distance <= self.point_radius * 2:
                self.toggle_point_selection(i)
                return
    
    def connect_selected_points(self, event=None):
        """Connect all selected points with lines"""
        if len(self.selected_points) < 2:
            messagebox.showwarning("Not Enough Points", "Select at least 2 points to connect!")
            return
        
        # Connect each pair of consecutive selected points
        for i in range(len(self.selected_points) - 1):
            point1_idx = self.selected_points[i]
            point2_idx = self.selected_points[i + 1]
            
            point1 = self.points[point1_idx]
            point2 = self.points[point2_idx]
            
            # Check if line already exists between these points
            line_exists = any(
                (line['start_point'] == point1_idx and line['end_point'] == point2_idx) or
                (line['start_point'] == point2_idx and line['end_point'] == point1_idx)
                for line in self.lines
            )
            
            if not line_exists:
                line_id = self.canvas.create_line(
                    point1['x'], point1['y'],
                    point2['x'], point2['y'],
                    fill=self.line_color,
                    width=self.line_width,
                    capstyle=tk.ROUND
                )
                
                length = math.sqrt(
                    (point2['x'] - point1['x'])**2 + 
                    (point2['y'] - point1['y'])**2
                )
                
                line_info = {
                    'canvas_id': line_id,
                    'start_point': point1_idx,
                    'end_point': point2_idx,
                    'color': self.line_color,
                    'width': self.line_width,
                    'length': length
                }
                
                self.lines.append(line_info)
        
        # Clear selection after connecting
        for point_idx in self.selected_points:
            point = self.points[point_idx]
            point['selected'] = False
            self.canvas.itemconfig(point['canvas_id'], fill="red", outline="darkred")
        
        self.selected_points.clear()
        self.update_counts()
        self.count_all_intersections()  # Recalculate intersections
    
    def undo_last_action(self, event=None):
        """Remove the last added point, line, or pen stroke"""
        if self.pen_strokes:
            # Remove last pen stroke
            last_stroke = self.pen_strokes.pop()
            self.canvas.delete(last_stroke)
        elif self.lines:
            # Remove last line
            last_line = self.lines.pop()
            self.canvas.delete(last_line['canvas_id'])
        elif self.points:
            # Remove last point
            last_point = self.points.pop()
            self.canvas.delete(last_point['canvas_id'])
            # Remove from selected points if it was selected
            if len(self.points) in self.selected_points:
                self.selected_points.remove(len(self.points))
        
        self.update_counts()
        self.count_all_intersections()  # Recalculate intersections
    
    def clear_canvas(self, event=None):
        """Clear all points, lines, and pen strokes"""
        total_items = len(self.points) + len(self.lines) + len(self.pen_strokes)
        if total_items > 0:
            result = messagebox.askyesno(
                "Clear Canvas",
                f"Are you sure you want to clear all {len(self.points)} points, {len(self.lines)} lines, and {len(self.pen_strokes)} pen strokes?"
            )
            if result:
                self.canvas.delete("all")
                self.points.clear()
                self.lines.clear()
                self.selected_points.clear()
                self.pen_strokes.clear()
                self.eraser_mode = False
                self.eraser_button.config(text="Eraser OFF", bg="#ffeeff")
                self.intersection_counts = {'vertical': [0] * 7, 'horizontal': [0] * 7}
                self.measurement_lines = {'vertical': [], 'horizontal': []}
                self.create_measurement_lines()  # Recreate measurement lines
                self.update_counts()
                self.update_intersection_display()
    
    def update_counts(self):
        """Update the point and line count display"""
        point_count = len(self.points)
        line_count = len(self.lines)
        selected_count = len(self.selected_points)
        
        if selected_count > 0:
            self.count_label.config(
                text=f"Points: {point_count} | Lines: {line_count} | Selected: {selected_count}"
            )
        else:
            self.count_label.config(text=f"Points: {point_count} | Lines: {line_count}")
    
    def update_intersection_display(self):
        """Update the intersection count labels on the measurement lines"""
        # Update vertical line labels
        for i, v_line in enumerate(self.measurement_lines['vertical']):
            count = self.intersection_counts['vertical'][i]
            self.canvas.itemconfig(v_line['text_id'], text=str(count))
        
        # Update horizontal line labels
        for i, h_line in enumerate(self.measurement_lines['horizontal']):
            count = self.intersection_counts['horizontal'][i]
            self.canvas.itemconfig(h_line['text_id'], text=str(count))
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Run the line drawing application"""
    app = LineDrawingApp()
    app.run()

if __name__ == "__main__":
    main()
