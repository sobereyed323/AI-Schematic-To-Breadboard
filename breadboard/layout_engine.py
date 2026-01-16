"""
Breadboard Layout Engine

This module provides the core functionality for creating breadboard layouts,
including component placement, connection routing, and conflict detection.
"""

import uuid
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Set, Dict, Any
import numpy as np
from collections import defaultdict
import heapq


class ComponentConflictError(Exception):
    """Raised when a component placement conflicts with existing components."""
    pass


class RoutingError(Exception):
    """Raised when wire routing fails."""
    pass


@dataclass
class Component:
    """Represents an electronic component on the breadboard.
    
    Attributes:
        type: Component type (e.g., "resistor", "capacitor", "led", "ic")
        value: Component value (e.g., resistance, capacitance)
        unit: Unit of measurement (e.g., "Ω", "µF", "V")
        position: Grid position as (row, column) tuple
        orientation: Component orientation ("horizontal" or "vertical")
        pins: Number of pins/leads
        id: Unique identifier
        metadata: Additional component-specific data
    """
    type: str
    value: Optional[float] = None
    unit: Optional[str] = None
    position: Optional[Tuple[int, int]] = None
    orientation: str = "horizontal"
    pins: int = 2
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation of the component."""
        if self.value and self.unit:
            return f"{self.type} ({self.value}{self.unit})"
        return self.type
    
    def get_occupied_positions(self) -> List[Tuple[int, int]]:
        """Get all grid positions occupied by this component.
        
        Returns:
            List of (row, column) tuples for occupied positions.
        """
        if not self.position:
            return []
        
        row, col = self.position
        positions = []
        
        if self.orientation == "horizontal":
            # Component extends along columns
            for i in range(self.pins):
                positions.append((row, col + i))
        else:  # vertical
            # Component extends along rows
            for i in range(self.pins):
                positions.append((row + i, col))
        
        return positions


@dataclass
class Connection:
    """Represents a wire connection on the breadboard.
    
    Attributes:
        start: Starting position (row, column)
        end: Ending position (row, column)
        color: Wire color for visualization
        wire_type: Type of connection ("signal", "power", "ground")
        path: Computed path as list of positions
        id: Unique identifier
    """
    start: Tuple[int, int]
    end: Tuple[int, int]
    color: str = "black"
    wire_type: str = "signal"
    path: Optional[List[Tuple[int, int]]] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def length(self) -> int:
        """Calculate the Manhattan distance of this connection.
        
        Returns:
            Integer length of the connection.
        """
        if self.path:
            return len(self.path)
        # Manhattan distance
        return abs(self.end[0] - self.start[0]) + abs(self.end[1] - self.start[1])


class BreadboardLayout:
    """Main class for managing breadboard layouts.
    
    This class handles component placement, wire routing, conflict detection,
    and layout optimization for standard breadboards.
    
    Attributes:
        rows: Number of rows in the breadboard grid
        columns: Number of columns in the breadboard grid
        power_rail_rows: Number of rows for power rails on each side
        hole_spacing: Physical spacing between holes in mm
    
    Example:
        >>> layout = BreadboardLayout(rows=30, columns=63)
        >>> component = Component(type="resistor", value=220, unit="Ω")
        >>> layout.place_component(component, (10, 15))
        >>> layout.route_connection((10, 15), (10, 20), color="red")
    """
    
    def __init__(
        self,
        rows: int = 30,
        columns: int = 63,
        power_rail_rows: int = 4,
        hole_spacing: float = 2.54
    ):
        """Initialize a new breadboard layout.
        
        Args:
            rows: Number of rows in the main grid (default: 30 for 830-point)
            columns: Number of columns in the main grid (default: 63)
            power_rail_rows: Rows dedicated to power rails (default: 4)
            hole_spacing: Physical spacing between holes in mm (default: 2.54)
        """
        self.rows = rows
        self.columns = columns
        self.power_rail_rows = power_rail_rows
        self.hole_spacing = hole_spacing
        
        # Grid representation: 0 = free, 1 = occupied by component, 2 = occupied by wire
        self.grid = np.zeros((rows, columns), dtype=int)
        
        # Components and connections
        self.components: List[Component] = []
        self.connections: List[Connection] = []
        
        # Track occupied positions for quick lookup
        self.occupied_positions: Set[Tuple[int, int]] = set()
        
        # Power rails (typically top and bottom rows)
        self.power_rails: Dict[str, List[Tuple[int, int]]] = {
            "power_top": [(i, j) for i in range(power_rail_rows) for j in range(columns)],
            "ground_top": [(i, j) for i in range(power_rail_rows) for j in range(columns)],
            "power_bottom": [(i, j) for i in range(rows - power_rail_rows, rows) for j in range(columns)],
            "ground_bottom": [(i, j) for i in range(rows - power_rail_rows, rows) for j in range(columns)],
        }
        
        # Wire color palette for auto-assignment
        self.wire_colors = [
            "red", "blue", "green", "yellow", "orange",
            "purple", "brown", "gray", "white"
        ]
        self.next_color_index = 0
    
    def place_component(
        self,
        component: Component,
        position: Tuple[int, int],
        orientation: str = "horizontal"
    ) -> bool:
        """Place a component at the specified position on the breadboard.
        
        Args:
            component: The component to place
            position: Grid coordinates (row, column) for the first pin
            orientation: Component orientation ("horizontal" or "vertical")
        
        Returns:
            True if placement was successful
        
        Raises:
            ValueError: If position is out of bounds
            ComponentConflictError: If position is already occupied
        """
        row, col = position
        
        # Validate position
        if not self._is_valid_position(position):
            raise ValueError(f"Position {position} is out of bounds")
        
        # Set component properties
        component.position = position
        component.orientation = orientation
        
        # Get all positions this component will occupy
        occupied = component.get_occupied_positions()
        
        # Check if all positions are valid and unoccupied
        for pos in occupied:
            if not self._is_valid_position(pos):
                raise ValueError(f"Component extends beyond breadboard bounds at {pos}")
            if pos in self.occupied_positions:
                raise ComponentConflictError(
                    f"Position {pos} is already occupied"
                )
        
        # Place the component
        for pos in occupied:
            self.grid[pos] = 1
            self.occupied_positions.add(pos)
        
        self.components.append(component)
        return True
    
    def route_connection(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int],
        color: str = "auto",
        priority: int = 0
    ) -> Optional[List[Tuple[int, int]]]:
        """Route a wire connection between two points using A* pathfinding.
        
        Args:
            start: Starting position (row, column)
            end: Ending position (row, column)
            color: Wire color ("auto" for automatic assignment)
            priority: Routing priority (higher = routed first)
        
        Returns:
            List of positions forming the wire path, or None if routing fails
        
        Raises:
            RoutingError: If no valid path can be found
        """
        # Validate positions
        if not self._is_valid_position(start):
            raise ValueError(f"Start position {start} is out of bounds")
        if not self._is_valid_position(end):
            raise ValueError(f"End position {end} is out of bounds")
        
        # Auto-assign color if needed
        if color == "auto":
            color = self._get_next_wire_color()
        
        # Find path using A* algorithm
        path = self._find_path(start, end)
        
        if not path:
            raise RoutingError(
                f"Could not find path from {start} to {end}"
            )
        
        # Create connection object
        connection = Connection(
            start=start,
            end=end,
            color=color,
            path=path
        )
        
        # Mark path positions in grid (but don't block future wires)
        for pos in path[1:-1]:  # Skip start and end points
            if self.grid[pos] == 0:
                self.grid[pos] = 2
        
        self.connections.append(connection)
        return path
    
    def _find_path(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int]
    ) -> Optional[List[Tuple[int, int]]]:
        """Find a path between two points using A* algorithm.
        
        Args:
            start: Starting position
            end: Ending position
        
        Returns:
            List of positions forming the path, or None if no path exists
        """
        def heuristic(pos: Tuple[int, int]) -> int:
            """Manhattan distance heuristic."""
            return abs(pos[0] - end[0]) + abs(pos[1] - end[1])
        
        def get_neighbors(pos: Tuple[int, int]) -> List[Tuple[int, int]]:
            """Get valid neighboring positions."""
            row, col = pos
            neighbors = []
            # 4-directional movement (Manhattan routing)
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_pos = (row + dr, col + dc)
                if self._is_valid_position(new_pos):
                    # Allow movement through wire positions (grid == 2)
                    # but prefer empty positions
                    neighbors.append(new_pos)
            return neighbors
        
        # Priority queue: (f_score, g_score, position, path)
        open_set = [(heuristic(start), 0, start, [start])]
        closed_set = set()
        g_scores = {start: 0}
        
        while open_set:
            f_score, g_score, current, path = heapq.heappop(open_set)
            
            if current == end:
                return path
            
            if current in closed_set:
                continue
            
            closed_set.add(current)
            
            for neighbor in get_neighbors(current):
                if neighbor in closed_set:
                    continue
                
                # Calculate cost (prefer empty positions)
                move_cost = 1
                if self.grid[neighbor] == 1:  # Component position
                    continue  # Can't route through components
                elif self.grid[neighbor] == 2:  # Wire position
                    move_cost = 5  # Penalty for crossing wires
                
                tentative_g = g_score + move_cost
                
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    f = tentative_g + heuristic(neighbor)
                    heapq.heappush(
                        open_set,
                        (f, tentative_g, neighbor, path + [neighbor])
                    )
        
        return None  # No path found
    
    def get_components(self) -> List[Component]:
        """Get all placed components.
        
        Returns:
            List of all components on the breadboard
        """
        return self.components.copy()
    
    def get_connections(self) -> List[Connection]:
        """Get all routed connections.
        
        Returns:
            List of all wire connections
        """
        return self.connections.copy()
    
    def clear(self) -> None:
        """Clear all components and connections from the breadboard."""
        self.grid = np.zeros((self.rows, self.columns), dtype=int)
        self.components = []
        self.connections = []
        self.occupied_positions = set()
        self.next_color_index = 0
    
    def optimize_layout(self, iterations: int = 100) -> float:
        """Optimize component layout to minimize wire crossings.
        
        This is a placeholder for future optimization algorithms.
        Current implementation returns a simple score based on wire lengths.
        
        Args:
            iterations: Number of optimization iterations
        
        Returns:
            Optimization score (lower is better)
        """
        # TODO: Implement optimization algorithm (e.g., simulated annealing)
        # For now, just calculate total wire length as a score
        total_length = sum(conn.length() for conn in self.connections)
        return total_length
    
    def _is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if a position is within the breadboard bounds.
        
        Args:
            position: Position to check
        
        Returns:
            True if position is valid, False otherwise
        """
        row, col = position
        return 0 <= row < self.rows and 0 <= col < self.columns
    
    def _get_next_wire_color(self) -> str:
        """Get the next wire color from the palette.
        
        Returns:
            Wire color string
        """
        color = self.wire_colors[self.next_color_index]
        self.next_color_index = (self.next_color_index + 1) % len(self.wire_colors)
        return color
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get layout statistics.
        
        Returns:
            Dictionary containing layout statistics
        """
        component_types = defaultdict(int)
        for component in self.components:
            component_types[component.type] += 1
        
        wire_types = defaultdict(int)
        total_wire_length = 0
        for connection in self.connections:
            wire_types[connection.wire_type] += 1
            total_wire_length += connection.length()
        
        return {
            "total_components": len(self.components),
            "component_types": dict(component_types),
            "total_connections": len(self.connections),
            "wire_types": dict(wire_types),
            "total_wire_length": total_wire_length,
            "average_wire_length": total_wire_length / len(self.connections) if self.connections else 0,
            "grid_utilization": len(self.occupied_positions) / (self.rows * self.columns),
        }
    
    def __repr__(self) -> str:
        """String representation of the breadboard layout."""
        return (
            f"BreadboardLayout({self.rows}x{self.columns}, "
            f"{len(self.components)} components, "
            f"{len(self.connections)} connections)"
        )
