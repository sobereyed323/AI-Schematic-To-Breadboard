"""
Unit Tests for Breadboard Engine

This module contains unit tests for the breadboard layout engine,
including component placement, wire routing, and visualization.
"""

import pytest
import numpy as np
from pathlib import Path

from breadboard.layout_engine import (
    BreadboardLayout,
    Component,
    Connection,
    ComponentConflictError,
    RoutingError
)
from breadboard.visualizer import BreadboardVisualizer
from breadboard.instructions import (
    InstructionGenerator,
    BillOfMaterials,
    BOMItem,
    InstructionStep
)


class TestBreadboardLayout:
    """Tests for BreadboardLayout class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.layout = BreadboardLayout()
    
    def test_initialization(self):
        """Test that layout initializes correctly."""
        assert self.layout.rows == 30
        assert self.layout.columns == 63
        assert self.layout.power_rail_rows == 4
        assert len(self.layout.components) == 0
        assert len(self.layout.connections) == 0
    
    def test_custom_initialization(self):
        """Test layout with custom dimensions."""
        layout = BreadboardLayout(rows=20, columns=40, power_rail_rows=2)
        assert layout.rows == 20
        assert layout.columns == 40
        assert layout.power_rail_rows == 2
    
    def test_place_component_success(self):
        """Test successful component placement."""
        component = Component(type="resistor", value=220, unit="Ω", pins=2)
        result = self.layout.place_component(component, (10, 15))
        
        assert result is True
        assert component in self.layout.components
        assert component.position == (10, 15)
        assert len(self.layout.occupied_positions) == 2  # 2-pin component
    
    def test_place_component_vertical(self):
        """Test vertical component placement."""
        component = Component(type="led", value=None, pins=2)
        result = self.layout.place_component(
            component, (10, 15), orientation="vertical"
        )
        
        assert result is True
        assert component.orientation == "vertical"
        positions = component.get_occupied_positions()
        assert positions == [(10, 15), (11, 15)]
    
    def test_place_component_conflict(self):
        """Test that placing on occupied position raises error."""
        component1 = Component(type="resistor", value=220, unit="Ω")
        component2 = Component(type="resistor", value=330, unit="Ω")
        
        self.layout.place_component(component1, (10, 15))
        
        with pytest.raises(ComponentConflictError):
            self.layout.place_component(component2, (10, 15))
    
    def test_place_component_out_of_bounds(self):
        """Test that out-of-bounds placement raises error."""
        component = Component(type="resistor", value=220, unit="Ω")
        
        with pytest.raises(ValueError):
            self.layout.place_component(component, (-1, 0))
        
        with pytest.raises(ValueError):
            self.layout.place_component(component, (100, 100))
    
    def test_place_component_extends_beyond_bounds(self):
        """Test that component extending beyond bounds raises error."""
        component = Component(type="ic", pins=8)
        
        # Try to place near right edge where it would extend beyond
        with pytest.raises(ValueError):
            self.layout.place_component(component, (10, 60))
    
    def test_route_connection_success(self):
        """Test successful connection routing."""
        path = self.layout.route_connection(
            start=(10, 15),
            end=(10, 20),
            color="red"
        )
        
        assert path is not None
        assert len(path) > 0
        assert path[0] == (10, 15)
        assert path[-1] == (10, 20)
        assert len(self.layout.connections) == 1
    
    def test_route_connection_auto_color(self):
        """Test auto color assignment."""
        self.layout.route_connection((10, 15), (10, 20), color="auto")
        
        connection = self.layout.connections[0]
        assert connection.color in self.layout.wire_colors
    
    def test_route_connection_invalid_position(self):
        """Test routing with invalid positions."""
        with pytest.raises(ValueError):
            self.layout.route_connection((-1, 0), (10, 10))
        
        with pytest.raises(ValueError):
            self.layout.route_connection((10, 10), (100, 100))
    
    def test_route_connection_around_component(self):
        """Test that routing avoids placed components."""
        # Place a component in the middle
        component = Component(type="ic", pins=8)
        self.layout.place_component(component, (10, 20))
        
        # Try to route around it
        path = self.layout.route_connection((10, 15), (10, 30))
        
        assert path is not None
        # Path should avoid component positions
        component_positions = set(component.get_occupied_positions())
        path_positions = set(path[1:-1])  # Exclude start and end
        assert len(component_positions.intersection(path_positions)) == 0
    
    def test_get_components(self):
        """Test retrieving all components."""
        component1 = Component(type="resistor", value=220, unit="Ω")
        component2 = Component(type="led")
        
        self.layout.place_component(component1, (10, 15))
        self.layout.place_component(component2, (15, 20))
        
        components = self.layout.get_components()
        assert len(components) == 2
        assert component1 in components
        assert component2 in components
    
    def test_get_connections(self):
        """Test retrieving all connections."""
        self.layout.route_connection((10, 15), (10, 20))
        self.layout.route_connection((15, 20), (15, 30))
        
        connections = self.layout.get_connections()
        assert len(connections) == 2
    
    def test_clear(self):
        """Test clearing the breadboard."""
        component = Component(type="resistor", value=220, unit="Ω")
        self.layout.place_component(component, (10, 15))
        self.layout.route_connection((10, 15), (10, 20))
        
        self.layout.clear()
        
        assert len(self.layout.components) == 0
        assert len(self.layout.connections) == 0
        assert len(self.layout.occupied_positions) == 0
    
    def test_optimize_layout(self):
        """Test layout optimization."""
        # Place some components and route connections
        component1 = Component(type="resistor", value=220, unit="Ω")
        component2 = Component(type="led")
        
        self.layout.place_component(component1, (10, 15))
        self.layout.place_component(component2, (15, 15))
        self.layout.route_connection((10, 17), (15, 14))
        
        score = self.layout.optimize_layout(iterations=10)
        
        # Score should be a positive number
        assert isinstance(score, (int, float))
        assert score >= 0
    
    def test_get_statistics(self):
        """Test layout statistics."""
        component1 = Component(type="resistor", value=220, unit="Ω")
        component2 = Component(type="resistor", value=330, unit="Ω")
        component3 = Component(type="led")
        
        self.layout.place_component(component1, (10, 15))
        self.layout.place_component(component2, (12, 15))
        self.layout.place_component(component3, (15, 15))
        self.layout.route_connection((10, 17), (12, 14))
        
        stats = self.layout.get_statistics()
        
        assert stats["total_components"] == 3
        assert stats["component_types"]["resistor"] == 2
        assert stats["component_types"]["led"] == 1
        assert stats["total_connections"] == 1


class TestComponent:
    """Tests for Component class."""
    
    def test_component_creation(self):
        """Test creating a component."""
        component = Component(
            type="resistor",
            value=220,
            unit="Ω",
            pins=2
        )
        
        assert component.type == "resistor"
        assert component.value == 220
        assert component.unit == "Ω"
        assert component.pins == 2
        assert component.id is not None
    
    def test_component_string(self):
        """Test component string representation."""
        component = Component(type="resistor", value=220, unit="Ω")
        
        assert str(component) == "resistor (220Ω)"
    
    def test_get_occupied_positions_horizontal(self):
        """Test getting occupied positions for horizontal component."""
        component = Component(type="resistor", pins=2, position=(10, 15))
        component.orientation = "horizontal"
        
        positions = component.get_occupied_positions()
        
        assert positions == [(10, 15), (10, 16)]
    
    def test_get_occupied_positions_vertical(self):
        """Test getting occupied positions for vertical component."""
        component = Component(type="led", pins=2, position=(10, 15))
        component.orientation = "vertical"
        
        positions = component.get_occupied_positions()
        
        assert positions == [(10, 15), (11, 15)]
    
    def test_get_occupied_positions_no_position(self):
        """Test getting positions when no position set."""
        component = Component(type="resistor", pins=2)
        
        positions = component.get_occupied_positions()
        
        assert positions == []


class TestConnection:
    """Tests for Connection class."""
    
    def test_connection_creation(self):
        """Test creating a connection."""
        connection = Connection(
            start=(10, 15),
            end=(10, 20),
            color="red",
            wire_type="power"
        )
        
        assert connection.start == (10, 15)
        assert connection.end == (10, 20)
        assert connection.color == "red"
        assert connection.wire_type == "power"
    
    def test_connection_length_with_path(self):
        """Test connection length calculation with path."""
        connection = Connection(
            start=(10, 15),
            end=(10, 20),
            path=[(10, 15), (10, 16), (10, 17), (10, 18), (10, 19), (10, 20)]
        )
        
        assert connection.length() == 6
    
    def test_connection_length_without_path(self):
        """Test connection length calculation without path (Manhattan distance)."""
        connection = Connection(start=(10, 15), end=(15, 20))
        
        # Manhattan distance: |15-10| + |20-15| = 10
        assert connection.length() == 10


class TestBreadboardVisualizer:
    """Tests for BreadboardVisualizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.layout = BreadboardLayout()
        
        # Add some components
        component1 = Component(type="resistor", value=220, unit="Ω")
        component2 = Component(type="led")
        
        self.layout.place_component(component1, (10, 15))
        self.layout.place_component(component2, (15, 15))
        self.layout.route_connection((10, 17), (15, 14), color="red")
    
    def test_visualizer_initialization(self):
        """Test visualizer initialization."""
        visualizer = BreadboardVisualizer(self.layout)
        
        assert visualizer.layout == self.layout
        assert visualizer.dpi == 300
        assert visualizer.show_labels is True
    
    def test_visualizer_draw(self):
        """Test visualization drawing (no errors)."""
        visualizer = BreadboardVisualizer(self.layout)
        
        # Should not raise any errors
        visualizer.draw()
    
    def test_visualizer_save_png(self, tmp_path):
        """Test saving visualization as PNG."""
        visualizer = BreadboardVisualizer(self.layout)
        visualizer.draw()
        
        output_file = tmp_path / "test_breadboard.png"
        visualizer.save(str(output_file), format="png")
        
        assert output_file.exists()
    
    def test_highlight_component(self):
        """Test component highlighting."""
        visualizer = BreadboardVisualizer(self.layout)
        component = self.layout.components[0]
        
        visualizer.highlight_component(component, color="yellow")
        
        assert component.id in visualizer.highlighted_components


class TestInstructionGenerator:
    """Tests for InstructionGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.layout = BreadboardLayout()
        
        # Create a simple circuit
        resistor = Component(type="resistor", value=220, unit="Ω")
        led = Component(type="led")
        
        self.layout.place_component(resistor, (10, 15))
        self.layout.place_component(led, (15, 15))
        self.layout.route_connection((10, 17), (15, 14), color="red")
    
    def test_generator_initialization(self):
        """Test instruction generator initialization."""
        generator = InstructionGenerator(self.layout)
        
        assert generator.layout == self.layout
        assert generator.include_images is True
        assert generator.difficulty_level == "beginner"
    
    def test_generate_instructions(self):
        """Test instruction generation."""
        generator = InstructionGenerator(self.layout)
        instructions = generator.generate_instructions()
        
        assert len(instructions) > 0
        assert isinstance(instructions[0], InstructionStep)
        # Should have intro + components + connections + final check
        assert len(instructions) >= 4
    
    def test_generate_bom(self):
        """Test BOM generation."""
        generator = InstructionGenerator(self.layout)
        bom = generator.generate_bom()
        
        assert isinstance(bom, BillOfMaterials)
        assert len(bom.items) > 0
        
        # Should include breadboard and jumper wires
        types = [item.component_type for item in bom.items]
        assert "breadboard" in types
    
    def test_export_markdown(self, tmp_path):
        """Test Markdown export."""
        generator = InstructionGenerator(self.layout)
        generator.generate_instructions()
        generator.generate_bom()
        
        output_file = tmp_path / "instructions.md"
        generator.export_markdown(str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "Breadboard Assembly Instructions" in content
        assert "Bill of Materials" in content
    
    def test_export_html(self, tmp_path):
        """Test HTML export."""
        generator = InstructionGenerator(self.layout)
        generator.generate_instructions()
        generator.generate_bom()
        
        output_file = tmp_path / "instructions.html"
        generator.export_html(str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "Breadboard Assembly Instructions" in content


class TestBOMItem:
    """Tests for BOMItem class."""
    
    def test_bom_item_creation(self):
        """Test creating a BOM item."""
        item = BOMItem(
            component_type="resistor",
            value="220Ω",
            quantity=2,
            description="220 ohm resistor, 1/4W"
        )
        
        assert item.component_type == "resistor"
        assert item.value == "220Ω"
        assert item.quantity == 2
    
    def test_bom_item_string(self):
        """Test BOM item string representation."""
        item = BOMItem(
            component_type="resistor",
            value="220Ω",
            quantity=2,
            description="220 ohm resistor"
        )
        
        assert "2x" in str(item)
        assert "resistor" in str(item)


# Integration test
class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_complete_workflow(self, tmp_path):
        """Test complete breadboard creation workflow."""
        # Create layout
        layout = BreadboardLayout()
        
        # Add components
        resistor = Component(type="resistor", value=220, unit="Ω")
        led = Component(type="led")
        
        layout.place_component(resistor, (10, 15))
        layout.place_component(led, (15, 15))
        
        # Route connections (connect from resistor end to LED start)
        # Resistor occupies (10,15) and (10,16), LED occupies (15,15) and (15,16)
        # Connect a point near the resistor to a point near the LED
        layout.route_connection((10, 17), (15, 14), color="red")
        
        # Generate visualization
        visualizer = BreadboardVisualizer(layout)
        visualizer.draw()
        image_path = tmp_path / "breadboard.png"
        visualizer.save(str(image_path))
        
        assert image_path.exists()
        
        # Generate instructions
        generator = InstructionGenerator(layout)
        instructions = generator.generate_instructions()
        bom = generator.generate_bom()
        
        assert len(instructions) > 0
        assert len(bom.items) > 0
        
        # Export instructions
        md_path = tmp_path / "instructions.md"
        generator.export_markdown(str(md_path))
        
        assert md_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
