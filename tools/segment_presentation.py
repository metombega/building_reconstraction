import tkinter as tk
from typing import List, Tuple, Optional

def present_segments(segment_lists: List[List[Tuple[Tuple[float, float], Tuple[float, float]]]], 
                           colors: Optional[List[str]] = None,
                           title: str = "Segment Visualization",
                           canvas_size: Tuple[int, int] = (800, 600),
                           margin: int = 50,
                           line_width: int = 2) -> None:
    """
    Present multiple lists of segments on screen using Tkinter, each list in a different color.
    
    Args:
        segment_lists: List of lists, where each inner list contains segments.
                      Each segment is ((x1, y1), (x2, y2))
        colors: Optional list of colors for each segment list. If not provided, 
               uses default colors. Can be color names or hex codes.
        title: Window title
        canvas_size: (width, height) of the canvas
        margin: Margin around the drawing area
        line_width: Width of the drawn lines
    """
    
    if not segment_lists:
        print("No segment lists provided")
        return
    
    # Default colors if not provided
    if colors is None:
        default_colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 
                         'pink', 'gray', 'olive', 'cyan', 'magenta', 'yellow',
                         'navy', 'lime', 'teal', 'silver', 'maroon', 'fuchsia']
        colors = default_colors[:len(segment_lists)]
    elif len(colors) < len(segment_lists):
        # Extend colors if not enough provided
        default_colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 
                         'pink', 'gray', 'olive', 'cyan']
        colors.extend(default_colors[:(len(segment_lists) - len(colors))])
    
    # Collect all points to determine bounds
    all_points = []
    for segment_list in segment_lists:
        for segment in segment_list:
            (x1, y1), (x2, y2) = segment
            all_points.extend([(x1, y1), (x2, y2)])
    
    if not all_points:
        print("No segments to display")
        return
    
    # Calculate bounds
    min_x = min(point[0] for point in all_points)
    max_x = max(point[0] for point in all_points)
    min_y = min(point[1] for point in all_points)
    max_y = max(point[1] for point in all_points)
    
    # Add some padding to bounds
    padding = max(max_x - min_x, max_y - min_y) * 0.1
    min_x -= padding
    max_x += padding
    min_y -= padding
    max_y += padding
    
    # Calculate scale to fit in canvas
    data_width = max_x - min_x
    data_height = max_y - min_y
    draw_width = canvas_size[0] - 2 * margin
    draw_height = canvas_size[1] - 2 * margin
    
    scale_x = draw_width / data_width if data_width > 0 else 1
    scale_y = draw_height / data_height if data_height > 0 else 1
    scale = min(scale_x, scale_y)
    
    def transform_point(x, y):
        """Transform data coordinates to canvas coordinates"""
        canvas_x = margin + (x - min_x) * scale
        # Flip Y coordinate for screen display (tkinter origin is top-left)
        canvas_y = canvas_size[1] - margin - (y - min_y) * scale
        return canvas_x, canvas_y
    
    # Create Tkinter window
    root = tk.Tk()
    root.title(title)
    root.geometry(f"{canvas_size[0]}x{canvas_size[1] + 100}")
    
    # Create canvas
    canvas = tk.Canvas(root, width=canvas_size[0], height=canvas_size[1], bg='white')
    canvas.pack(pady=10)
    
    # Draw segments
    total_segments = 0
    for i, (segment_list, color) in enumerate(zip(segment_lists, colors)):
        list_segment_count = 0
        for segment in segment_list:
            (x1, y1), (x2, y2) = segment
            canvas_x1, canvas_y1 = transform_point(x1, y1)
            canvas_x2, canvas_y2 = transform_point(x2, y2)
            
            canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2,
                             fill=color, width=line_width, capstyle=tk.ROUND)
            list_segment_count += 1
        
        total_segments += list_segment_count
        # print(f"List {i+1} ({color}): {list_segment_count} segments")
    
    # Create legend and info frame
    info_frame = tk.Frame(root)
    info_frame.pack(pady=10)
    
    # Legend
    legend_frame = tk.Frame(info_frame)
    legend_frame.pack(side=tk.LEFT, padx=20)
    
    tk.Label(legend_frame, text="Legend:", font=("Arial", 12, "bold")).pack()
    for i, (segment_list, color) in enumerate(zip(segment_lists, colors)):
        legend_item = tk.Frame(legend_frame)
        legend_item.pack(anchor='w')
        
        # Color box
        color_canvas = tk.Canvas(legend_item, width=20, height=10, bg=color)
        color_canvas.pack(side=tk.LEFT, padx=(0, 5))
        
        # Label
        count = len(segment_list)
        tk.Label(legend_item, text=f"List {i+1}: {count} segments").pack(side=tk.LEFT)
    
    # Statistics
    stats_frame = tk.Frame(info_frame)
    stats_frame.pack(side=tk.RIGHT, padx=20)
    
    tk.Label(stats_frame, text="Statistics:", font=("Arial", 12, "bold")).pack()
    tk.Label(stats_frame, text=f"Total lists: {len(segment_lists)}").pack(anchor='w')
    tk.Label(stats_frame, text=f"Total segments: {total_segments}").pack(anchor='w')
    tk.Label(stats_frame, text=f"Bounds: ({min_x:.1f}, {min_y:.1f}) to ({max_x:.1f}, {max_y:.1f})").pack(anchor='w')
    
    # Close button
    close_button = tk.Button(root, text="Close", command=root.destroy, 
                           font=("Arial", 10), bg="#ffcccc", padx=20)
    close_button.pack(pady=5)
    
    root.mainloop()


# Example usage and test function
def test_segment_presentation():
    """Test function demonstrating the segment presentation functionality."""
    
    # Create sample segment lists
    
    # List 1: Horizontal and vertical lines forming a grid
    grid_segments = [
        ((0, 0), (3, 0)),    # Bottom horizontal
        ((0, 3), (3, 3)),    # Top horizontal
        ((0, 0), (0, 3)),    # Left vertical
        ((3, 0), (3, 3)),    # Right vertical
        ((1, 0), (1, 3)),    # Middle vertical
        ((0, 1), (3, 1)),    # Middle horizontal
    ]
    
    # List 2: Diagonal lines
    diagonal_segments = [
        ((0, 0), (3, 3)),    # Main diagonal
        ((0, 3), (3, 0)),    # Anti-diagonal
        ((0.5, 0.5), (2.5, 2.5)),  # Parallel to main diagonal
    ]
    
    # List 3: Random lines
    random_segments = [
        ((-4, -1), (5, -2)),
        ((-4.5, 0), (4.5, -3)),
        ((4, 2.5), (-6, 1.5)),
        ((5.5, 0.5), (6, -3)),
    ]
    
    all_segment_lists = [grid_segments, diagonal_segments,random_segments]

    present_segments(all_segment_lists)
    

if __name__ == "__main__":
    test_segment_presentation()
