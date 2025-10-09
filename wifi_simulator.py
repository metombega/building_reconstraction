import numpy as np
import matplotlib.pyplot as plt
import math
from typing import List, Tuple, Optional

class Wall:
    """Represents a wall that can block or attenuate WiFi signals."""
    
    def __init__(self, start: Tuple[float, float], end: Tuple[float, float], 
                 attenuation_db: float = 10.0):
        """
        Initialize a wall.
        
        Args:
            start: (x, y) coordinates of wall start point
            end: (x, y) coordinates of wall end point
            attenuation_db: Signal attenuation in dB when passing through wall
        """
        self.start = start
        self.end = end
        self.attenuation_db = attenuation_db
    
    def intersects_line(self, point1: Tuple[float, float], 
                       point2: Tuple[float, float]) -> bool:
        """
        Check if this wall intersects with a line segment.
        
        Args:
            point1: First point of the line segment
            point2: Second point of the line segment
            
        Returns:
            True if the wall intersects with the line segment
        """
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        
        def intersect(A, B, C, D):
            return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)
        
        return intersect(point1, point2, self.start, self.end)


class WiFiSimulator:
    """Simulates WiFi signal strength with wall attenuation."""
    
    def __init__(self, source_position: Tuple[float, float], 
                 source_power_dbm: float = 20.0):
        """
        Initialize WiFi simulator.
        
        Args:
            source_position: (x, y) coordinates of WiFi source
            source_power_dbm: Transmission power in dBm
        """
        self.source_position = source_position
        self.source_power_dbm = source_power_dbm
        self.walls: List[Wall] = []
    
    def add_wall(self, start: Tuple[float, float], end: Tuple[float, float], 
                 attenuation_db: float = 10.0):
        """Add a wall to the simulation."""
        wall = Wall(start, end, attenuation_db)
        self.walls.append(wall)
    
    def calculate_free_space_loss(self, distance: float, 
                                frequency_mhz: float = 2400.0) -> float:
        """
        Calculate free space path loss.
        
        Args:
            distance: Distance in meters
            frequency_mhz: Frequency in MHz (default 2.4 GHz WiFi)
            
        Returns:
            Path loss in dB
        """
        if distance == 0:
            return 0
        
        # Free space path loss formula: 20*log10(d) + 20*log10(f) + 32.44
        # where d is in km and f is in MHz
        distance_km = distance / 1000.0
        return 20 * math.log10(distance_km) + 20 * math.log10(frequency_mhz) + 32.44
    
    def calculate_wall_attenuation(self, point: Tuple[float, float]) -> float:
        """
        Calculate total wall attenuation for signal path from source to point.
        
        Args:
            point: Target point coordinates
            
        Returns:
            Total attenuation in dB
        """
        total_attenuation = 0.0
        
        for wall in self.walls:
            if wall.intersects_line(self.source_position, point):
                total_attenuation += wall.attenuation_db
        
        return total_attenuation
    
    def calculate_signal_strength(self, point: Tuple[float, float]) -> float:
        """
        Calculate signal strength at a given point.
        
        Args:
            point: Target point coordinates
            
        Returns:
            Signal strength in dBm
        """
        # Calculate distance
        dx = point[0] - self.source_position[0]
        dy = point[1] - self.source_position[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Calculate free space loss
        path_loss = self.calculate_free_space_loss(distance)
        
        # Calculate wall attenuation
        wall_loss = self.calculate_wall_attenuation(point)
        
        # Total received power
        received_power = self.source_power_dbm - path_loss - wall_loss
        
        return received_power
    
    def generate_heatmap(self, x_range: Tuple[float, float], 
                        y_range: Tuple[float, float],
                        resolution: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate a heatmap of signal strength.
        
        Args:
            x_range: (min_x, max_x) range for heatmap
            y_range: (min_y, max_y) range for heatmap
            resolution: Number of points along each axis
            
        Returns:
            Tuple of (X, Y, signal_strength) arrays for plotting
        """
        x = np.linspace(x_range[0], x_range[1], resolution)
        y = np.linspace(y_range[0], y_range[1], resolution)
        X, Y = np.meshgrid(x, y)
        
        signal_strength = np.zeros_like(X)
        
        for i in range(len(y)):
            for j in range(len(x)):
                point = (X[i, j], Y[i, j])
                signal_strength[i, j] = self.calculate_signal_strength(point)
        
        return X, Y, signal_strength
    
    def plot_heatmap(self, x_range: Tuple[float, float], 
                    y_range: Tuple[float, float],
                    resolution: int = 100, 
                    title: str = "WiFi Signal Strength Heatmap",
                    save_filename: Optional[str] = None):
        """
        Plot and display the WiFi signal strength heatmap.
        
        Args:
            x_range: (min_x, max_x) range for heatmap
            y_range: (min_y, max_y) range for heatmap
            resolution: Number of points along each axis
            title: Plot title
            save_filename: Optional filename to save the plot
        """
        X, Y, signal_strength = self.generate_heatmap(x_range, y_range, resolution)
        
        plt.figure(figsize=(12, 10))
        
        # Create heatmap
        im = plt.imshow(signal_strength, extent=[x_range[0], x_range[1], 
                                               y_range[0], y_range[1]],
                       origin='lower', cmap='viridis', aspect='equal')
        
        # Add colorbar
        cbar = plt.colorbar(im)
        cbar.set_label('Signal Strength (dBm)', rotation=270, labelpad=20)
        
        # Plot WiFi source
        plt.plot(self.source_position[0], self.source_position[1], 
                'r*', markersize=20, label='WiFi Source')
        
        # Plot walls
        for i, wall in enumerate(self.walls):
            plt.plot([wall.start[0], wall.end[0]], 
                    [wall.start[1], wall.end[1]], 
                    'k-', linewidth=4, alpha=0.8, 
                    label='Wall' if i == 0 else "")
        
        plt.xlabel('X Position (m)')
        plt.ylabel('Y Position (m)')
        plt.title(title)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_filename:
            plt.savefig(save_filename, dpi=300, bbox_inches='tight')
        
        plt.show()


def example_with_walls():
    """Example usage showing WiFi simulation with walls."""
    
    # Create WiFi simulator with source at (5, 5)
    wifi = WiFiSimulator(source_position=(4.5, 4.5), source_power_dbm=20.0)
    
    # Add some walls
    # Vertical wall
    wifi.add_wall(start=(2.0, 5.0), end=(6.0, 5.0), attenuation_db=12.0)
    
    # Horizontal wall  
    wifi.add_wall(start=(2.0, 7.0), end=(6.0, 7.0), attenuation_db=10.0)
    
    # Diagonal wall
    wifi.add_wall(start=(8.0, 4.2), end=(8.0, 4.0), attenuation_db=8.0)
    
    # Generate and plot heatmap
    wifi.plot_heatmap(
        x_range=(0.0, 12.0),
        y_range=(0.0, 10.0),
        resolution=150,
        title="WiFi Signal Strength with Walls",
        # save_filename="wifi_heatmap_with_walls.png"
    )
    
    print(f"WiFi source position: {wifi.source_position}")
    print(f"Number of walls: {len(wifi.walls)}")
    for i, wall in enumerate(wifi.walls):
        print(f"Wall {i+1}: {wall.start} to {wall.end}, "
              f"attenuation: {wall.attenuation_db} dB")


if __name__ == "__main__":
    example_with_walls()
