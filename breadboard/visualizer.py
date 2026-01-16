"""
Breadboard Visualizer

This module provides visualization capabilities for breadboard layouts,
including rendering components, wires, and labels, with export to multiple formats.
"""

from typing import Optional, Dict, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
from matplotlib.lines import Line2D
import numpy as np

from breadboard.layout_engine import BreadboardLayout, Component, Connection


class BreadboardVisualizer:
    """Class for visualizing breadboard layouts.
    
    This class handles rendering of breadboard grids, components, wires,
    and labels, with support for multiple output formats.
    
    Attributes:
        layout: The breadboard layout to visualize
        dpi: Output resolution in DPI
        show_labels: Whether to show component labels
        fig: Matplotlib figure object
        ax: Matplotlib axes object
    
    Example:
        >>> visualizer = BreadboardVisualizer(layout, dpi=300)
        >>> visualizer.draw()
        >>> visualizer.save("breadboard.png")
    """
    
    # Color scheme
    BREADBOARD_COLOR = "#F5DEB3"  # Wheat color
    HOLE_COLOR = "#2C2C2C"  # Dark gray
    POWER_RAIL_COLOR = "#FF4444"  # Red
    GROUND_RAIL_COLOR = "#000000"  # Black
    COMPONENT_COLORS = {
        "resistor": "#D4AF37",  # Gold
        "capacitor": "#4169E1",  # Royal blue
        "led": "#FF1493",  # Deep pink
        "ic": "#708090",  # Slate gray
        "transistor": "#696969",  # Dim gray
        "default": "#808080",  # Gray
    }
    
    def __init__(
        self,
        layout: BreadboardLayout,
        dpi: int = 300,
        show_labels: bool = True,
        figsize: Optional[Tuple[float, float]] = None
    ):
        """Initialize the breadboard visualizer.
        
        Args:
            layout: The breadboard layout to visualize
            dpi: Output resolution in DPI (default: 300)
            show_labels: Whether to show component labels (default: True)
            figsize: Figure size as (width, height) in inches
        """
        self.layout = layout
        self.dpi = dpi
        self.show_labels = show_labels
        
        # Calculate figure size based on breadboard dimensions
        if figsize is None:
            aspect_ratio = layout.columns / layout.rows
            figsize = (12 * aspect_ratio, 12)
        
        self.fig, self.ax = plt.subplots(figsize=figsize, dpi=dpi)
        
        # Component highlights
        self.highlighted_components = {}
    
    def draw(self) -> None:
        """Generate the breadboard visualization.
        
        This method renders all elements of the breadboard including
        the grid, power rails, components, and wire connections.
        """
        self._setup_axes()
        self._draw_breadboard_base()
        self._draw_power_rails()
        self._draw_components()
        self._draw_wires()
        if self.show_labels:
            self._draw_labels()
    
    def _setup_axes(self) -> None:
        """Set up the matplotlib axes for drawing."""
        self.ax.set_xlim(-1, self.layout.columns + 1)
        self.ax.set_ylim(-1, self.layout.rows + 1)
        self.ax.set_aspect('equal')
        self.ax.invert_yaxis()  # Origin at top-left
        
        # Remove axis ticks and labels
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        
        # Set background color
        self.fig.patch.set_facecolor('white')
        self.ax.set_facecolor('white')
    
    def _draw_breadboard_base(self) -> None:
        """Draw the base breadboard with holes."""
        # Draw breadboard background
        breadboard_rect = Rectangle(
            (0, 0),
            self.layout.columns,
            self.layout.rows,
            facecolor=self.BREADBOARD_COLOR,
            edgecolor='black',
            linewidth=2
        )
        self.ax.add_patch(breadboard_rect)
        
        # Draw holes
        hole_radius = 0.15
        for row in range(self.layout.rows):
            for col in range(self.layout.columns):
                circle = Circle(
                    (col + 0.5, row + 0.5),
                    hole_radius,
                    facecolor=self.HOLE_COLOR,
                    edgecolor='none'
                )
                self.ax.add_patch(circle)
    
    def _draw_power_rails(self) -> None:
        """Draw power and ground rails."""
        # Top power rails
        if self.layout.power_rail_rows > 0:
            # Power rail indicator (red line)
            self.ax.plot(
                [0, self.layout.columns],
                [0.5, 0.5],
                color=self.POWER_RAIL_COLOR,
                linewidth=3,
                alpha=0.5
            )
            # Ground rail indicator (black line)
            if self.layout.power_rail_rows > 1:
                self.ax.plot(
                    [0, self.layout.columns],
                    [1.5, 1.5],
                    color=self.GROUND_RAIL_COLOR,
                    linewidth=3,
                    alpha=0.5
                )
            
            # Bottom power rails
            bottom_start = self.layout.rows - self.layout.power_rail_rows
            self.ax.plot(
                [0, self.layout.columns],
                [bottom_start + 0.5, bottom_start + 0.5],
                color=self.POWER_RAIL_COLOR,
                linewidth=3,
                alpha=0.5
            )
            if self.layout.power_rail_rows > 1:
                self.ax.plot(
                    [0, self.layout.columns],
                    [bottom_start + 1.5, bottom_start + 1.5],
                    color=self.GROUND_RAIL_COLOR,
                    linewidth=3,
                    alpha=0.5
                )
    
    def _draw_components(self) -> None:
        """Draw all components on the breadboard."""
        for component in self.layout.components:
            self._draw_component(component)
    
    def _draw_component(self, component: Component) -> None:
        """Draw a single component.
        
        Args:
            component: The component to draw
        """
        if not component.position:
            return
        
        row, col = component.position
        positions = component.get_occupied_positions()
        
        # Get component color
        color = self.COMPONENT_COLORS.get(
            component.type,
            self.COMPONENT_COLORS["default"]
        )
        
        # Check if component is highlighted
        if component.id in self.highlighted_components:
            color = self.highlighted_components[component.id]
        
        if component.orientation == "horizontal":
            # Draw horizontal component
            width = component.pins
            height = 0.6
            x = col
            y = row + 0.2
        else:  # vertical
            # Draw vertical component
            width = 0.6
            height = component.pins
            x = col + 0.2
            y = row
        
        # Draw component body
        rect = FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.05",
            facecolor=color,
            edgecolor='black',
            linewidth=2,
            alpha=0.8
        )
        self.ax.add_patch(rect)
        
        # Draw component-specific details
        if component.type == "resistor":
            self._draw_resistor_bands(x, y, width, height, component)
        elif component.type == "led":
            self._draw_led_indicator(x, y, width, height, component)
        elif component.type == "ic":
            self._draw_ic_pins(positions, component)
    
    def _draw_resistor_bands(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        component: Component
    ) -> None:
        """Draw color bands on a resistor (placeholder).
        
        Args:
            x, y: Position of resistor
            width, height: Dimensions of resistor
            component: The resistor component
        """
        # TODO: Implement actual color band calculation based on resistance
        # For now, just draw simple bands
        if width > height:  # horizontal
            band_positions = [x + width * 0.3, x + width * 0.5, x + width * 0.7]
            for band_x in band_positions:
                self.ax.plot(
                    [band_x, band_x],
                    [y, y + height],
                    color='black',
                    linewidth=1
                )
    
    def _draw_led_indicator(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        component: Component
    ) -> None:
        """Draw polarity indicator on an LED.
        
        Args:
            x, y: Position of LED
            width, height: Dimensions of LED
            component: The LED component
        """
        # Draw a small arrow or + symbol to indicate polarity
        center_x = x + width / 2
        center_y = y + height / 2
        
        # Draw + symbol (indicating anode/positive)
        self.ax.text(
            center_x,
            center_y,
            '+',
            fontsize=8,
            color='white',
            ha='center',
            va='center',
            weight='bold'
        )
    
    def _draw_ic_pins(
        self,
        positions: list,
        component: Component
    ) -> None:
        """Draw pin numbers on an IC.
        
        Args:
            positions: List of occupied positions
            component: The IC component
        """
        # Draw pin numbers
        for i, (row, col) in enumerate(positions, 1):
            self.ax.text(
                col + 0.5,
                row + 0.5,
                str(i),
                fontsize=6,
                color='white',
                ha='center',
                va='center'
            )
    
    def _draw_wires(self) -> None:
        """Draw all wire connections."""
        for connection in self.layout.connections:
            self._draw_wire(connection)
    
    def _draw_wire(self, connection: Connection) -> None:
        """Draw a single wire connection.
        
        Args:
            connection: The wire connection to draw
        """
        if not connection.path:
            # Draw direct line if no path computed
            path = [connection.start, connection.end]
        else:
            path = connection.path
        
        # Convert path to coordinates
        x_coords = [col + 0.5 for row, col in path]
        y_coords = [row + 0.5 for row, col in path]
        
        # Draw wire
        self.ax.plot(
            x_coords,
            y_coords,
            color=connection.color,
            linewidth=2,
            linestyle='-',
            marker='o',
            markersize=3,
            markerfacecolor=connection.color,
            markeredgecolor='black',
            markeredgewidth=0.5,
            alpha=0.8,
            zorder=10
        )
    
    def _draw_labels(self) -> None:
        """Draw component labels."""
        for component in self.layout.components:
            if component.position:
                row, col = component.position
                label = str(component)
                
                # Position label above or beside component
                if component.orientation == "horizontal":
                    label_x = col + component.pins / 2
                    label_y = row - 0.5
                else:
                    label_x = col + 1.5
                    label_y = row + component.pins / 2
                
                self.ax.text(
                    label_x,
                    label_y,
                    label,
                    fontsize=8,
                    ha='center',
                    va='center',
                    bbox=dict(
                        boxstyle='round,pad=0.3',
                        facecolor='white',
                        edgecolor='black',
                        alpha=0.8
                    )
                )
    
    def save(
        self,
        filename: str,
        format: str = "png",
        transparent: bool = False
    ) -> None:
        """Save the visualization to a file.
        
        Args:
            filename: Output file path
            format: Output format ("png", "svg", "pdf")
            transparent: Use transparent background
        
        Raises:
            ValueError: If format is not supported
        """
        supported_formats = ["png", "svg", "pdf"]
        if format.lower() not in supported_formats:
            raise ValueError(
                f"Unsupported format: {format}. "
                f"Supported formats: {supported_formats}"
            )
        
        self.fig.savefig(
            filename,
            format=format,
            dpi=self.dpi,
            bbox_inches='tight',
            transparent=transparent
        )
    
    def show(self) -> None:
        """Display the visualization in a window.
        
        Note: Requires GUI environment.
        """
        plt.show()
    
    def highlight_component(
        self,
        component: Component,
        color: str = "yellow"
    ) -> None:
        """Highlight a specific component.
        
        Args:
            component: Component to highlight
            color: Highlight color
        """
        self.highlighted_components[component.id] = color
    
    def set_wire_color(
        self,
        connection_id: str,
        color: str
    ) -> None:
        """Change the color of a specific wire connection.
        
        Args:
            connection_id: ID of the connection
            color: New color (hex or name)
        """
        for connection in self.layout.connections:
            if connection.id == connection_id:
                connection.color = color
                break
    
    def close(self) -> None:
        """Close the matplotlib figure."""
        plt.close(self.fig)
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.close()
        except:
            pass
