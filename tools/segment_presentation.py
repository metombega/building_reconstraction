import tkinter as tk
from typing import List, Tuple, Optional

def present_segments(
    segment_lists: List[List[Tuple[Tuple[float, float], Tuple[float, float]]]],
    colors: Optional[List[str]] = None,
    points_lists: Optional[List[List[Tuple[float, float]]]] = None,
    points_colors: Optional[List[str]] = None,
    title: str = "Segment Visualization",
    canvas_size: Tuple[int, int] = (800, 600),
    margin: int = 50,
    line_width: int = 2,
    point_radius: int = 4,
    side_by_side: bool = False,
    same_scale: bool = True,
) -> None:
    """
    Present multiple lists of segments on screen using Tkinter, each list in a different color.
    Optionally present one or more lists of points on the same display.
    If `side_by_side` is True and exactly two segment lists are provided, the
    function will render them in two canvases placed side-by-side. When
    `same_scale` is True (default) both canvases will use the same coordinate
    transform so visual comparison is easier. If `same_scale` is False each
    side is scaled independently to its contents.
    
    Args:
    segment_lists: List of lists, where each inner list contains segments.
               Each segment is ((x1, y1), (x2, y2))
    colors: Optional list of colors for each segment list. If not provided,
        uses default colors. Can be color names or hex codes.
    points_lists: Optional list of lists of points to draw on the same canvas.
              Each point is (x, y). Each inner list will be drawn with a
              matching entry from `points_colors` when provided.
    points_colors: Optional list of colors for each points list. If not
               provided, defaults will be used.
        title: Window title
        canvas_size: (width, height) of the canvas
        margin: Margin around the drawing area
        line_width: Width of the drawn lines
    """
    
    if not segment_lists:
        print("No segment lists provided")
        return
    
    # Default colors if not provided (for segments)
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

    # Prepare points colors and default points_lists
    if points_lists is None:
        points_lists = []

    if points_colors is None:
        # Reuse the same palette but prefer black for points if possible
        default_point_colors = ['black', 'red', 'blue', 'green', 'purple', 'orange']
        points_colors = default_point_colors[:len(points_lists)]
    elif len(points_colors) < len(points_lists):
        default_point_colors = ['black', 'red', 'blue', 'green', 'purple', 'orange']
        points_colors.extend(default_point_colors[:(len(points_lists) - len(points_colors))])
    
    # Collect all points to determine bounds (include segment endpoints and point lists)
    all_points = []
    for segment_list in segment_lists:
        for segment in segment_list:
            (x1, y1), (x2, y2) = segment
            all_points.extend([(x1, y1), (x2, y2)])

    for pts in points_lists:
        for (x, y) in pts:
            all_points.append((x, y))
    
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
    
    total_segments = 0
    # If side_by_side and exactly 2 lists provided, create two canvases
    if side_by_side and len(segment_lists) == 2:
        left_segments = segment_lists[0]
        right_segments = segment_lists[1]

        # Prepare points lists per side (if provided). Expect points_lists to be
        # either None or a list of two lists when side_by_side=True. Fall back to
        # empty lists when missing.
        if points_lists and len(points_lists) >= 2:
            left_points = points_lists[0]
            right_points = points_lists[1]
        else:
            left_points = []
            right_points = []

        # Determine bounds. If same_scale is True, use combined bounds so both
        # canvases align. Otherwise compute per-side bounds.
        if same_scale:
            combined_points = []
            for s in (left_segments, right_segments):
                for seg in s:
                    (x1, y1), (x2, y2) = seg
                    combined_points.extend([(x1, y1), (x2, y2)])
            for (x, y) in left_points + right_points:
                combined_points.append((x, y))

            if combined_points:
                min_x = min(p[0] for p in combined_points)
                max_x = max(p[0] for p in combined_points)
                min_y = min(p[1] for p in combined_points)
                max_y = max(p[1] for p in combined_points)
            else:
                print("No segments to display")
                return

            padding = max(max_x - min_x, max_y - min_y) * 0.1
            min_x -= padding
            max_x += padding
            min_y -= padding
            max_y += padding

            data_width = max_x - min_x
            data_height = max_y - min_y

            # Each canvas gets half the width
            canvas_w = canvas_size[0] // 2
            draw_width = canvas_w - 2 * margin
            draw_height = canvas_size[1] - 2 * margin
            scale_x = draw_width / data_width if data_width > 0 else 1
            scale_y = draw_height / data_height if data_height > 0 else 1
            scale = min(scale_x, scale_y)

            def make_transform_for_canvas(canvas_w_local):
                def _t(x, y):
                    cx = margin + (x - min_x) * scale
                    cy = canvas_size[1] - margin - (y - min_y) * scale
                    return cx, cy
                return _t

            transform_left = make_transform_for_canvas(canvas_w)
            transform_right = make_transform_for_canvas(canvas_w)

        else:
            # independent scales: compute bounds per side and create transforms
            def compute_bounds_and_transform(segments, pts):
                pts_all = []
                for seg in segments:
                    (x1, y1), (x2, y2) = seg
                    pts_all.extend([(x1, y1), (x2, y2)])
                for (x, y) in pts:
                    pts_all.append((x, y))
                if not pts_all:
                    return None
                minx = min(p[0] for p in pts_all)
                maxx = max(p[0] for p in pts_all)
                miny = min(p[1] for p in pts_all)
                maxy = max(p[1] for p in pts_all)
                padding = max(maxx - minx, maxy - miny) * 0.1
                minx -= padding; maxx += padding; miny -= padding; maxy += padding

                data_w = maxx - minx; data_h = maxy - miny
                canvas_w = canvas_size[0] // 2
                draw_w = canvas_w - 2 * margin
                draw_h = canvas_size[1] - 2 * margin
                sx = draw_w / data_w if data_w > 0 else 1
                sy = draw_h / data_h if data_h > 0 else 1
                s = min(sx, sy)

                def _t(x, y):
                    cx = margin + (x - minx) * s
                    cy = canvas_size[1] - margin - (y - miny) * s
                    return cx, cy

                return _t

            transform_left = compute_bounds_and_transform(left_segments, left_points) or (lambda x, y: (x, y))
            transform_right = compute_bounds_and_transform(right_segments, right_points) or (lambda x, y: (x, y))

        # Create two canvases side by side
        frame = tk.Frame(root)
        frame.pack(pady=10)

        canvas_left = tk.Canvas(frame, width=canvas_size[0] // 2, height=canvas_size[1], bg='white')
        canvas_left.pack(side=tk.LEFT)
        canvas_right = tk.Canvas(frame, width=canvas_size[0] // 2, height=canvas_size[1], bg='white')
        canvas_right.pack(side=tk.RIGHT)

        # Draw left
        for seg in left_segments:
            (x1, y1), (x2, y2) = seg
            cx1, cy1 = transform_left(x1, y1)
            cx2, cy2 = transform_left(x2, y2)
            canvas_left.create_line(cx1, cy1, cx2, cy2, fill=colors[0] if colors else 'red', width=line_width, capstyle=tk.ROUND)
            total_segments += 1

        # Draw right
        for seg in right_segments:
            (x1, y1), (x2, y2) = seg
            cx1, cy1 = transform_right(x1, y1)
            cx2, cy2 = transform_right(x2, y2)
            canvas_right.create_line(cx1, cy1, cx2, cy2, fill=colors[1] if colors and len(colors) > 1 else 'blue', width=line_width, capstyle=tk.ROUND)
            total_segments += 1

        # Draw points per side
        for (pts, canv, pcolors) in ((left_points, canvas_left, points_colors[0] if points_colors else 'black'), (right_points, canvas_right, points_colors[1] if points_colors and len(points_colors) > 1 else 'black')):
            pcolor = pcolors
            for (x, y) in pts:
                cx, cy = (transform_left if canv is canvas_left else transform_right)(x, y)
                r = point_radius
                canv.create_oval(cx - r, cy - r, cx + r, cy + r, fill=pcolor, outline='')

    else:
        # Single canvas mode (original behavior)
        canvas = tk.Canvas(root, width=canvas_size[0], height=canvas_size[1], bg='white')
        canvas.pack(pady=10)

        # Draw segments
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

    # Draw points (if any)
    for i, pts in enumerate(points_lists):
        pcolor = points_colors[i] if i < len(points_colors) else 'black'
        for (x, y) in pts:
            cx, cy = transform_point(x, y)
            r = point_radius
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=pcolor, outline='')
    
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

    # Add points lists to legend (if any)
    for i, pts in enumerate(points_lists):
        legend_item = tk.Frame(legend_frame)
        legend_item.pack(anchor='w')

        color = points_colors[i] if i < len(points_colors) else 'black'
        color_canvas = tk.Canvas(legend_item, width=20, height=10, bg=color)
        color_canvas.pack(side=tk.LEFT, padx=(0, 5))
        tk.Label(legend_item, text=f"Points {i+1}: {len(pts)} points").pack(side=tk.LEFT)
    
    # Statistics
    stats_frame = tk.Frame(info_frame)
    stats_frame.pack(side=tk.RIGHT, padx=20)
    
    tk.Label(stats_frame, text="Statistics:", font=("Arial", 12, "bold")).pack()
    tk.Label(stats_frame, text=f"Total segment lists: {len(segment_lists)}").pack(anchor='w')
    tk.Label(stats_frame, text=f"Total segments: {total_segments}").pack(anchor='w')
    total_points = sum(len(pts) for pts in points_lists)
    tk.Label(stats_frame, text=f"Total points lists: {len(points_lists)}").pack(anchor='w')
    tk.Label(stats_frame, text=f"Total points: {total_points}").pack(anchor='w')
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
    
    all_segment_lists = [grid_segments, diagonal_segments, random_segments]

    # Sample point lists to display on the same canvas
    points_a = [(0.5, 0.5), (1.5, 1.5), (2.5, 2.5)]
    points_b = [(-3, 0), (0, -1), (4, 1)]

    present_segments(all_segment_lists, points_lists=[points_a, points_b], points_colors=['black', 'magenta'])
    

if __name__ == "__main__":
    test_segment_presentation()
