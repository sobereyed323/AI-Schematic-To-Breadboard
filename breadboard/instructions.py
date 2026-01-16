"""
Instruction Generator

This module provides functionality for generating step-by-step assembly
instructions and bill of materials for breadboard layouts.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from collections import defaultdict
import datetime

from breadboard.layout_engine import BreadboardLayout, Component, Connection


@dataclass
class InstructionStep:
    """Represents a single assembly instruction step.
    
    Attributes:
        number: Step number
        description: Step description
        component: Associated component (if any)
        connection: Associated connection (if any)
        notes: Additional notes or warnings
        image_ref: Reference to associated diagram (optional)
    """
    number: int
    description: str
    component: Optional[Component] = None
    connection: Optional[Connection] = None
    notes: List[str] = field(default_factory=list)
    image_ref: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the instruction step."""
        text = f"Step {self.number}: {self.description}"
        if self.notes:
            text += "\n  Notes: " + "; ".join(self.notes)
        return text


@dataclass
class BOMItem:
    """Represents an item in the bill of materials.
    
    Attributes:
        component_type: Type of component
        value: Component value/rating
        quantity: Number needed
        description: Detailed description
        part_number: Manufacturer part number (optional)
        estimated_price: Estimated unit price (optional)
    """
    component_type: str
    value: str
    quantity: int
    description: str
    part_number: Optional[str] = None
    estimated_price: Optional[float] = None
    
    def __str__(self) -> str:
        """String representation of BOM item."""
        text = f"{self.quantity}x {self.component_type} {self.value} - {self.description}"
        if self.part_number:
            text += f" (Part #: {self.part_number})"
        if self.estimated_price:
            text += f" [~${self.estimated_price:.2f} ea]"
        return text


@dataclass
class BillOfMaterials:
    """Bill of materials for a breadboard layout.
    
    Attributes:
        items: List of BOM items
        total_cost: Total estimated cost (optional)
        notes: Additional notes
    """
    items: List[BOMItem] = field(default_factory=list)
    total_cost: Optional[float] = None
    notes: List[str] = field(default_factory=list)
    
    def add_item(self, item: BOMItem) -> None:
        """Add an item to the BOM."""
        self.items.append(item)
    
    def calculate_total_cost(self) -> float:
        """Calculate total cost from item prices.
        
        Returns:
            Total cost, or 0.0 if prices not available
        """
        total = 0.0
        for item in self.items:
            if item.estimated_price:
                total += item.estimated_price * item.quantity
        self.total_cost = total
        return total


class InstructionGenerator:
    """Class for generating assembly instructions and bill of materials.
    
    This class analyzes a breadboard layout and generates comprehensive
    assembly instructions with proper ordering, warnings, and tips.
    
    Attributes:
        layout: The breadboard layout
        include_images: Whether to include diagram references
        difficulty_level: Target audience level
    
    Example:
        >>> generator = InstructionGenerator(layout)
        >>> instructions = generator.generate_instructions()
        >>> generator.export_pdf("instructions.pdf")
    """
    
    # Component placement order (ICs first, then passives)
    COMPONENT_PRIORITY = {
        "ic": 1,
        "transistor": 2,
        "led": 3,
        "capacitor": 4,
        "resistor": 5,
    }
    
    # Wire routing order (power first)
    WIRE_PRIORITY = {
        "power": 1,
        "ground": 2,
        "signal": 3,
    }
    
    def __init__(
        self,
        layout: BreadboardLayout,
        include_images: bool = True,
        difficulty_level: str = "beginner"
    ):
        """Initialize the instruction generator.
        
        Args:
            layout: The breadboard layout
            include_images: Include diagram references (default: True)
            difficulty_level: Target audience ("beginner", "intermediate", "advanced")
        """
        self.layout = layout
        self.include_images = include_images
        self.difficulty_level = difficulty_level
        
        # Generated instructions
        self.instructions: List[InstructionStep] = []
        self.bom: Optional[BillOfMaterials] = None
    
    def generate_instructions(self) -> List[InstructionStep]:
        """Generate step-by-step assembly instructions.
        
        Returns:
            Ordered list of instruction steps
        """
        self.instructions = []
        step_number = 1
        
        # Introduction step
        intro_step = InstructionStep(
            number=step_number,
            description="Gather all components and ensure your breadboard is clean and ready.",
            notes=["Check the bill of materials to ensure you have all parts."]
        )
        self.instructions.append(intro_step)
        step_number += 1
        
        # Sort components by placement priority
        sorted_components = sorted(
            self.layout.components,
            key=lambda c: self.COMPONENT_PRIORITY.get(c.type, 99)
        )
        
        # Component placement steps
        for component in sorted_components:
            step = self._create_component_step(step_number, component)
            self.instructions.append(step)
            step_number += 1
        
        # Sort connections by wire type priority
        sorted_connections = sorted(
            self.layout.connections,
            key=lambda c: self.WIRE_PRIORITY.get(c.wire_type, 99)
        )
        
        # Wire connection steps
        for connection in sorted_connections:
            step = self._create_connection_step(step_number, connection)
            self.instructions.append(step)
            step_number += 1
        
        # Final verification step
        final_step = InstructionStep(
            number=step_number,
            description="Double-check all connections before applying power.",
            notes=[
                "Verify component polarities (LEDs, electrolytic capacitors, etc.)",
                "Ensure no short circuits between power and ground",
                "Check that all components are firmly seated"
            ]
        )
        self.instructions.append(final_step)
        
        return self.instructions
    
    def _create_component_step(
        self,
        step_number: int,
        component: Component
    ) -> InstructionStep:
        """Create an instruction step for placing a component.
        
        Args:
            step_number: Step number
            component: Component to place
        
        Returns:
            Instruction step
        """
        if not component.position:
            return InstructionStep(
                step_number,
                f"Place {component} (position not specified)"
            )
        
        row, col = component.position
        
        # Convert to human-readable position (use letter for columns)
        col_letter = self._column_to_letter(col)
        
        description = (
            f"Place {component} {component.orientation}ly at position "
            f"{col_letter}{row + 1}"
        )
        
        notes = []
        
        # Add component-specific notes
        if component.type == "ic":
            notes.append(
                "Ensure the IC is oriented correctly - look for the notch or dot marking pin 1"
            )
            notes.append("Press firmly but gently to avoid bending pins")
        elif component.type == "led":
            notes.append(
                "LEDs have polarity! The longer lead (anode) is positive, "
                "shorter lead (cathode) is negative"
            )
        elif component.type == "transistor":
            notes.append("Match the transistor orientation to the diagram")
        
        # Add beginner-level notes
        if self.difficulty_level == "beginner":
            notes.append(
                f"Component spans {component.pins} holes "
                f"({component.orientation}ly)"
            )
        
        return InstructionStep(
            number=step_number,
            description=description,
            component=component,
            notes=notes
        )
    
    def _create_connection_step(
        self,
        step_number: int,
        connection: Connection
    ) -> InstructionStep:
        """Create an instruction step for making a wire connection.
        
        Args:
            step_number: Step number
            connection: Connection to make
        
        Returns:
            Instruction step
        """
        start_row, start_col = connection.start
        end_row, end_col = connection.end
        
        start_pos = f"{self._column_to_letter(start_col)}{start_row + 1}"
        end_pos = f"{self._column_to_letter(end_col)}{end_row + 1}"
        
        wire_type_desc = ""
        if connection.wire_type == "power":
            wire_type_desc = " (power)"
        elif connection.wire_type == "ground":
            wire_type_desc = " (ground)"
        
        description = (
            f"Connect a {connection.color} wire{wire_type_desc} "
            f"from {start_pos} to {end_pos}"
        )
        
        notes = []
        
        # Add wire-specific notes
        if connection.wire_type == "power":
            notes.append("Use red wire for power connections (conventional)")
        elif connection.wire_type == "ground":
            notes.append("Use black wire for ground connections (conventional)")
        
        # Calculate wire length hint
        if connection.path:
            length = len(connection.path)
            if self.difficulty_level == "beginner":
                notes.append(
                    f"You'll need a wire approximately {length} holes long"
                )
        
        return InstructionStep(
            number=step_number,
            description=description,
            connection=connection,
            notes=notes
        )
    
    def generate_bom(self, include_prices: bool = False) -> BillOfMaterials:
        """Generate bill of materials.
        
        Args:
            include_prices: Include estimated prices (requires internet)
        
        Returns:
            Complete bill of materials
        """
        self.bom = BillOfMaterials()
        
        # Count components by type and value
        component_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        for component in self.layout.components:
            key = f"{component.value}{component.unit}" if component.value else "standard"
            component_counts[component.type][key] += 1
        
        # Create BOM items
        for comp_type, values in component_counts.items():
            for value, quantity in values.items():
                description = self._get_component_description(comp_type, value)
                
                # TODO: Add part number lookup
                part_number = None
                
                # TODO: Add price lookup if requested
                estimated_price = None
                if include_prices:
                    # Placeholder for price lookup
                    pass
                
                item = BOMItem(
                    component_type=comp_type,
                    value=value,
                    quantity=quantity,
                    description=description,
                    part_number=part_number,
                    estimated_price=estimated_price
                )
                self.bom.add_item(item)
        
        # Add breadboard itself
        breadboard_item = BOMItem(
            component_type="breadboard",
            value="830-point",
            quantity=1,
            description="Standard 830-point solderless breadboard",
            estimated_price=4.00 if include_prices else None
        )
        self.bom.add_item(breadboard_item)
        
        # Count wires by color
        wire_counts: Dict[str, int] = defaultdict(int)
        for connection in self.layout.connections:
            wire_counts[connection.color] += 1
        
        # Add wire items
        for color, quantity in wire_counts.items():
            wire_item = BOMItem(
                component_type="jumper wire",
                value=color,
                quantity=quantity,
                description=f"{color.capitalize()} jumper wires (22 AWG)",
                estimated_price=0.10 if include_prices else None
            )
            self.bom.add_item(wire_item)
        
        # Calculate total cost if prices included
        if include_prices:
            self.bom.calculate_total_cost()
        
        # Add general notes
        self.bom.notes = [
            "All resistors should be 1/4W or greater",
            "Capacitor voltage ratings should exceed circuit voltage by at least 50%",
            "Wire gauge: 22 AWG is standard for breadboard work"
        ]
        
        return self.bom
    
    def _get_component_description(self, comp_type: str, value: str) -> str:
        """Get detailed component description.
        
        Args:
            comp_type: Component type
            value: Component value
        
        Returns:
            Detailed description string
        """
        descriptions = {
            "resistor": f"{value} resistor, 1/4W, 5% tolerance",
            "capacitor": f"{value} capacitor, ceramic or film",
            "led": f"{value} LED, 5mm through-hole",
            "ic": f"{value} integrated circuit",
            "transistor": f"{value} transistor, TO-92 package",
        }
        return descriptions.get(comp_type, f"{comp_type} ({value})")
    
    def _column_to_letter(self, col: int) -> str:
        """Convert column number to letter (A, B, C, ...).
        
        Args:
            col: Column number (0-indexed)
        
        Returns:
            Column letter
        """
        # For breadboards, columns are typically A-J for one half
        letters = "ABCDEFGHIJ"
        if col < len(letters):
            return letters[col]
        # For larger breadboards, use numeric
        return str(col + 1)
    
    def export_markdown(self, filename: str) -> None:
        """Export instructions to Markdown format.
        
        Args:
            filename: Output file path
        """
        with open(filename, 'w') as f:
            # Header
            f.write("# Breadboard Assembly Instructions\n\n")
            f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            # Bill of Materials
            if not self.bom:
                self.generate_bom()
            
            f.write("## Bill of Materials\n\n")
            f.write("| Quantity | Component | Value | Description |\n")
            f.write("|----------|-----------|-------|-------------|\n")
            for item in self.bom.items:
                f.write(f"| {item.quantity} | {item.component_type} | {item.value} | {item.description} |\n")
            
            if self.bom.total_cost:
                f.write(f"\n**Estimated Total Cost:** ${self.bom.total_cost:.2f}\n")
            
            # Instructions
            f.write("\n## Assembly Instructions\n\n")
            
            if not self.instructions:
                self.generate_instructions()
            
            for step in self.instructions:
                f.write(f"### {step}\n\n")
                if step.notes:
                    for note in step.notes:
                        f.write(f"- ⚠️ {note}\n")
                    f.write("\n")
    
    def export_html(self, filename: str, theme: str = "light") -> None:
        """Export instructions to HTML format.
        
        Args:
            filename: Output file path
            theme: Visual theme ("light" or "dark")
        """
        # Generate instructions and BOM if not already done
        if not self.instructions:
            self.generate_instructions()
        if not self.bom:
            self.generate_bom()
        
        # Simple HTML template
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Breadboard Assembly Instructions</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: {'#f5f5f5' if theme == 'light' else '#2c2c2c'};
            color: {'#333' if theme == 'light' else '#e0e0e0'};
        }}
        h1, h2 {{ color: {'#2c3e50' if theme == 'light' else '#4a90e2'}; }}
        .step {{ 
            background: {'white' if theme == 'light' else '#3c3c3c'};
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #4a90e2;
        }}
        .note {{
            background: {'#fff3cd' if theme == 'light' else '#5c4d00'};
            padding: 10px;
            margin: 5px 0;
            border-radius: 3px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid {'#ddd' if theme == 'light' else '#555'};
        }}
        th {{
            background-color: {'#4a90e2' if theme == 'light' else '#1a5490'};
            color: white;
        }}
    </style>
</head>
<body>
    <h1>Breadboard Assembly Instructions</h1>
    <p>Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    
    <h2>Bill of Materials</h2>
    <table>
        <thead>
            <tr>
                <th>Quantity</th>
                <th>Component</th>
                <th>Value</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for item in self.bom.items:
            html += f"""            <tr>
                <td>{item.quantity}</td>
                <td>{item.component_type}</td>
                <td>{item.value}</td>
                <td>{item.description}</td>
            </tr>
"""
        
        html += """        </tbody>
    </table>
    
"""
        
        if self.bom.total_cost:
            html += f"    <p><strong>Estimated Total Cost:</strong> ${self.bom.total_cost:.2f}</p>\n\n"
        
        html += "    <h2>Assembly Instructions</h2>\n\n"
        
        for step in self.instructions:
            html += f"""    <div class="step">
        <h3>Step {step.number}</h3>
        <p>{step.description}</p>
"""
            if step.notes:
                for note in step.notes:
                    html += f'        <div class="note">⚠️ {note}</div>\n'
            html += "    </div>\n\n"
        
        html += """</body>
</html>"""
        
        with open(filename, 'w') as f:
            f.write(html)
    
    def export_pdf(
        self,
        filename: str,
        include_bom: bool = True,
        include_diagrams: bool = True
    ) -> None:
        """Export instructions to PDF format.
        
        Note: This is a placeholder. Full implementation requires reportlab.
        
        Args:
            filename: Output file path
            include_bom: Include bill of materials
            include_diagrams: Include breadboard diagrams
        """
        # TODO: Implement PDF generation with reportlab
        # For now, generate HTML and suggest conversion
        html_filename = filename.replace('.pdf', '.html')
        self.export_html(html_filename)
        
        print(f"PDF export not yet implemented. HTML version saved to {html_filename}")
        print("You can convert to PDF using a browser or wkhtmltopdf tool.")
