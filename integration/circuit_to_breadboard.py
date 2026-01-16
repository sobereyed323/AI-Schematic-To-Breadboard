"""
CircuitNet to Breadboard Bridge

This module provides integration between CircuitNet's circuit diagram generation
and the breadboard layout engine.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from breadboard.layout_engine import (
    BreadboardLayout,
    Component,
    Connection,
    ComponentConflictError,
    RoutingError
)
from breadboard.visualizer import BreadboardVisualizer
from breadboard.instructions import InstructionGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CircuitNetBridge:
    """Bridge between CircuitNet output and Breadboard Engine.
    
    This class handles the conversion of CircuitNet's circuit analysis
    results into breadboard layouts, managing coordinate transformations,
    component mapping, and connection routing.
    
    Attributes:
        use_gpt_enhancement: Whether to use GPT-4 Vision enhancement
        gpt_analyzer: GPT-4 Vision analyzer instance
        layout: Current breadboard layout
    
    Example:
        >>> bridge = CircuitNetBridge()
        >>> result = bridge.process_schematic("schematic.png")
        >>> print(f"Layout saved to {result['breadboard_image']}")
    """
    
    # Component type mapping from CircuitNet to breadboard
    COMPONENT_MAP = {
        "resistor": "resistor",
        "capacitor": "capacitor",
        "inductor": "inductor",
        "voltage_source": "power",
        "current_source": "power",
        "led": "led",
        "ic": "ic",
        "transistor": "transistor",
    }
    
    # Default component pin counts
    DEFAULT_PINS = {
        "resistor": 2,
        "capacitor": 2,
        "inductor": 2,
        "led": 2,
        "transistor": 3,
        "ic": 8,  # Default to 8-pin IC
        "power": 2,
    }
    
    def __init__(
        self,
        use_gpt_enhancement: bool = False,
        gpt_analyzer: Optional[Any] = None
    ):
        """Initialize the CircuitNet bridge.
        
        Args:
            use_gpt_enhancement: Enable GPT-4 Vision enhancement
            gpt_analyzer: SchematicAnalyzer instance (required if use_gpt_enhancement)
        """
        self.use_gpt_enhancement = use_gpt_enhancement
        self.gpt_analyzer = gpt_analyzer
        self.layout: Optional[BreadboardLayout] = None
        
        if use_gpt_enhancement and gpt_analyzer is None:
            logger.warning(
                "GPT enhancement requested but no analyzer provided. "
                "Continuing without GPT enhancement."
            )
            self.use_gpt_enhancement = False
    
    def process_schematic(
        self,
        image_path: str,
        output_dir: str = "output"
    ) -> Dict[str, Any]:
        """Process a schematic image end-to-end.
        
        This method handles the complete workflow from schematic image to
        breadboard layout, visualization, and instructions.
        
        Args:
            image_path: Path to schematic image
            output_dir: Output directory for generated files
        
        Returns:
            Dictionary containing:
                - breadboard_image: Path to breadboard visualization
                - instructions_html: Path to HTML instructions
                - instructions_markdown: Path to Markdown instructions
                - bom: Bill of materials
                - statistics: Layout statistics
        """
        logger.info(f"Processing schematic: {image_path}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Analyze schematic
        circuit_data = self._analyze_schematic(image_path)
        
        # Step 2: Convert to breadboard layout
        self.layout = self.convert_to_breadboard(circuit_data)
        
        # Step 3: Generate visualization
        breadboard_image = os.path.join(output_dir, "breadboard_layout.png")
        self._generate_visualization(breadboard_image)
        
        # Step 4: Generate instructions
        instructions_html = os.path.join(output_dir, "instructions.html")
        instructions_md = os.path.join(output_dir, "instructions.md")
        bom = self._generate_instructions(instructions_html, instructions_md)
        
        # Collect statistics
        stats = self.layout.get_statistics()
        
        logger.info("Processing complete")
        
        return {
            "breadboard_image": breadboard_image,
            "instructions_html": instructions_html,
            "instructions_markdown": instructions_md,
            "bom": bom,
            "statistics": stats
        }
    
    def _analyze_schematic(self, image_path: str) -> Dict[str, Any]:
        """Analyze schematic using CircuitNet or GPT-4 Vision.
        
        Args:
            image_path: Path to schematic image
        
        Returns:
            Dictionary with components and connections
        """
        if self.use_gpt_enhancement and self.gpt_analyzer:
            logger.info("Using GPT-4 Vision for schematic analysis")
            try:
                result = self.gpt_analyzer.analyze_schematic(image_path)
                return result
            except Exception as e:
                logger.error(f"GPT-4 Vision analysis failed: {e}")
                logger.info("Falling back to placeholder data")
        
        # TODO: Integrate with actual CircuitNet notebooks
        # For now, return placeholder data
        logger.info("Using placeholder circuit data")
        return self._get_placeholder_circuit_data()
    
    def _get_placeholder_circuit_data(self) -> Dict[str, Any]:
        """Get placeholder circuit data for testing.
        
        Returns:
            Dictionary with sample components and connections
        """
        return {
            "components": [
                {
                    "id": "R1",
                    "type": "resistor",
                    "value": "220",
                    "unit": "Ω",
                    "position": {"x": 10, "y": 10}
                },
                {
                    "id": "LED1",
                    "type": "led",
                    "value": "red",
                    "position": {"x": 20, "y": 10}
                }
            ],
            "connections": [
                {"from": "R1", "to": "LED1", "type": "signal"},
                {"from": "LED1", "to": "GND", "type": "ground"}
            ],
            "power_supply": {"voltage": "5V", "type": "DC"}
        }
    
    def convert_to_breadboard(
        self,
        circuitnet_data: Dict[str, Any]
    ) -> BreadboardLayout:
        """Convert CircuitNet output to breadboard layout.
        
        Args:
            circuitnet_data: CircuitNet analysis results
        
        Returns:
            Generated breadboard layout
        """
        logger.info("Converting circuit to breadboard layout")
        
        # Create new breadboard layout
        layout = BreadboardLayout()
        
        # Extract components and connections
        components = circuitnet_data.get("components", [])
        connections = circuitnet_data.get("connections", [])
        
        # Component placement
        component_map = {}  # Maps component IDs to breadboard positions
        
        for i, comp_data in enumerate(components):
            component = self._create_component(comp_data)
            
            # Calculate breadboard position
            position = self._calculate_position(comp_data, i, len(components))
            
            try:
                layout.place_component(component, position)
                component_map[comp_data.get("id", f"comp_{i}")] = {
                    "component": component,
                    "positions": component.get_occupied_positions()
                }
                logger.info(f"Placed {component} at {position}")
            except (ValueError, ComponentConflictError) as e:
                logger.error(f"Failed to place component {component}: {e}")
        
        # Connection routing
        for conn_data in connections:
            try:
                self._route_connection(layout, conn_data, component_map)
            except RoutingError as e:
                logger.error(f"Failed to route connection: {e}")
        
        return layout
    
    def _create_component(self, comp_data: Dict[str, Any]) -> Component:
        """Create a Component object from CircuitNet data.
        
        Args:
            comp_data: Component data dictionary
        
        Returns:
            Component object
        """
        comp_type = comp_data.get("type", "unknown")
        breadboard_type = self.COMPONENT_MAP.get(comp_type, comp_type)
        
        # Extract value and unit
        value_str = comp_data.get("value", "")
        value = None
        unit = None
        
        # Try to parse numeric value
        try:
            # Handle cases like "220Ω", "10µF", etc.
            import re
            match = re.match(r"([\d.]+)\s*(\w+)?", str(value_str))
            if match:
                value = float(match.group(1))
                unit = match.group(2) if match.group(2) else None
        except:
            pass
        
        # Get pin count
        pins = self.DEFAULT_PINS.get(breadboard_type, 2)
        
        return Component(
            type=breadboard_type,
            value=value,
            unit=unit,
            pins=pins,
            metadata={"original_data": comp_data}
        )
    
    def _calculate_position(
        self,
        comp_data: Dict[str, Any],
        index: int,
        total_components: int
    ) -> Tuple[int, int]:
        """Calculate breadboard position for a component.
        
        This uses a simple left-to-right, top-to-bottom placement strategy.
        
        Args:
            comp_data: Component data
            index: Component index
            total_components: Total number of components
        
        Returns:
            Tuple of (row, column) coordinates
        """
        # Start placing components in the middle area of the breadboard
        # avoiding power rails (top and bottom 4 rows)
        start_row = 10
        start_col = 5
        
        # Simple grid layout: 5 components per row
        components_per_row = 5
        spacing = 10  # Columns between components
        
        row_offset = (index // components_per_row) * 5
        col_offset = (index % components_per_row) * spacing
        
        row = start_row + row_offset
        col = start_col + col_offset
        
        return (row, col)
    
    def _route_connection(
        self,
        layout: BreadboardLayout,
        conn_data: Dict[str, Any],
        component_map: Dict[str, Dict]
    ) -> None:
        """Route a connection between components.
        
        Args:
            layout: Breadboard layout
            conn_data: Connection data
            component_map: Mapping of component IDs to positions
        """
        from_id = conn_data.get("from")
        to_id = conn_data.get("to")
        conn_type = conn_data.get("type", "signal")
        
        # Get component positions
        from_comp = component_map.get(from_id)
        to_comp = component_map.get(to_id)
        
        if not from_comp or not to_comp:
            logger.warning(f"Cannot route connection: component not found")
            return
        
        # Get end positions (last pin of each component)
        from_positions = from_comp["positions"]
        to_positions = to_comp["positions"]
        
        if not from_positions or not to_positions:
            return
        
        start = from_positions[-1]  # Last pin
        end = to_positions[0]  # First pin
        
        # Determine wire color based on connection type
        if conn_type == "power":
            color = "red"
        elif conn_type == "ground":
            color = "black"
        else:
            color = "auto"
        
        # Route the connection
        layout.route_connection(start, end, color=color)
        logger.info(f"Routed {conn_type} connection from {start} to {end}")
    
    def _generate_visualization(self, output_path: str) -> None:
        """Generate breadboard visualization.
        
        Args:
            output_path: Output file path
        """
        logger.info("Generating breadboard visualization")
        
        visualizer = BreadboardVisualizer(self.layout, dpi=300)
        visualizer.draw()
        visualizer.save(output_path, format="png")
        
        logger.info(f"Visualization saved to {output_path}")
    
    def _generate_instructions(
        self,
        html_path: str,
        markdown_path: str
    ) -> Any:
        """Generate assembly instructions.
        
        Args:
            html_path: Output path for HTML instructions
            markdown_path: Output path for Markdown instructions
        
        Returns:
            Bill of materials
        """
        logger.info("Generating assembly instructions")
        
        generator = InstructionGenerator(self.layout, difficulty_level="beginner")
        
        # Generate instructions
        instructions = generator.generate_instructions()
        logger.info(f"Generated {len(instructions)} instruction steps")
        
        # Generate BOM
        bom = generator.generate_bom(include_prices=False)
        logger.info(f"Generated BOM with {len(bom.items)} items")
        
        # Export to files
        generator.export_html(html_path)
        generator.export_markdown(markdown_path)
        
        logger.info(f"Instructions saved to {html_path} and {markdown_path}")
        
        return bom
    
    def pixel_to_grid(
        self,
        x: int,
        y: int,
        image_width: int,
        image_height: int
    ) -> Tuple[int, int]:
        """Convert pixel coordinates to breadboard grid coordinates.
        
        Args:
            x: X coordinate in pixels
            y: Y coordinate in pixels
            image_width: Image width in pixels
            image_height: Image height in pixels
        
        Returns:
            Tuple of (row, column) grid coordinates
        """
        # Normalize to 0-1 range
        norm_x = x / image_width
        norm_y = y / image_height
        
        # Map to breadboard grid
        col = int(norm_x * self.layout.columns)
        row = int(norm_y * self.layout.rows)
        
        # Ensure within bounds
        col = max(0, min(col, self.layout.columns - 1))
        row = max(0, min(row, self.layout.rows - 1))
        
        return (row, col)
    
    def get_layout_statistics(self) -> Optional[Dict[str, Any]]:
        """Get statistics about the current layout.
        
        Returns:
            Dictionary of statistics, or None if no layout exists
        """
        if self.layout:
            return self.layout.get_statistics()
        return None
