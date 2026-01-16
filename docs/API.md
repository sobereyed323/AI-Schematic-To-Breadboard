# API Documentation

## Overview

This document provides comprehensive API documentation for the CircuitNet Enhanced project, including the breadboard engine, AI enhancement, and integration modules.

---

## Table of Contents

1. [Breadboard Module](#breadboard-module)
   - [BreadboardLayout](#breadboardlayout)
   - [BreadboardVisualizer](#breadboardvisualizer)
   - [InstructionGenerator](#instructiongenerator)
2. [AI Enhancement Module](#ai-enhancement-module)
   - [SchematicAnalyzer](#schematicanalyzer)
   - [ImprovedClassifier](#improvedclassifier)
3. [Integration Module](#integration-module)
   - [CircuitNetBridge](#circuitnetbridge)
4. [Data Models](#data-models)
5. [Usage Examples](#usage-examples)
6. [Error Handling](#error-handling)

---

## Breadboard Module

### BreadboardLayout

Main class for managing breadboard layout and component placement.

#### Constructor

```python
BreadboardLayout(
    rows: int = 30,
    columns: int = 63,
    power_rail_rows: int = 4,
    hole_spacing: float = 2.54
)
```

**Parameters:**
- `rows` (int): Number of rows in the breadboard grid. Default: 30
- `columns` (int): Number of columns in the breadboard grid. Default: 63
- `power_rail_rows` (int): Number of rows for power rails. Default: 4
- `hole_spacing` (float): Spacing between holes in mm. Default: 2.54 (0.1")

**Example:**
```python
layout = BreadboardLayout(rows=30, columns=63)
```

#### Methods

##### place_component()

```python
place_component(
    component: Component,
    position: Tuple[int, int],
    orientation: str = "horizontal"
) -> bool
```

Place a component at the specified position on the breadboard.

**Parameters:**
- `component` (Component): The component to place
- `position` (Tuple[int, int]): Grid coordinates (row, column)
- `orientation` (str): Component orientation ("horizontal" or "vertical")

**Returns:**
- `bool`: True if placement successful, False otherwise

**Raises:**
- `ValueError`: If position is out of bounds
- `ComponentConflictError`: If position is already occupied

**Example:**
```python
from breadboard.components import Resistor

resistor = Resistor(value=220, unit="Ω")
success = layout.place_component(resistor, (10, 15), orientation="horizontal")
```

##### route_connection()

```python
route_connection(
    start: Tuple[int, int],
    end: Tuple[int, int],
    color: str = "auto",
    priority: int = 0
) -> Optional[List[Tuple[int, int]]]
```

Route a wire connection between two points on the breadboard.

**Parameters:**
- `start` (Tuple[int, int]): Starting position (row, column)
- `end` (Tuple[int, int]): Ending position (row, column)
- `color` (str): Wire color. Use "auto" for automatic assignment
- `priority` (int): Routing priority (higher = routed first)

**Returns:**
- `Optional[List[Tuple[int, int]]]`: List of positions forming the wire path, or None if routing fails

**Example:**
```python
path = layout.route_connection(
    start=(10, 15),
    end=(20, 30),
    color="red",
    priority=1
)
```

##### get_components()

```python
get_components() -> List[Component]
```

Get all placed components.

**Returns:**
- `List[Component]`: List of all components on the breadboard

##### get_connections()

```python
get_connections() -> List[Connection]
```

Get all routed connections.

**Returns:**
- `List[Connection]`: List of all wire connections

##### clear()

```python
clear() -> None
```

Clear all components and connections from the breadboard.

##### optimize_layout()

```python
optimize_layout(iterations: int = 100) -> float
```

Optimize the component layout to minimize wire crossings.

**Parameters:**
- `iterations` (int): Number of optimization iterations

**Returns:**
- `float`: Optimization score (lower is better)

**Example:**
```python
score = layout.optimize_layout(iterations=100)
print(f"Optimization score: {score}")
```

---

### BreadboardVisualizer

Class for visualizing breadboard layouts.

#### Constructor

```python
BreadboardVisualizer(
    layout: BreadboardLayout,
    dpi: int = 300,
    show_labels: bool = True
)
```

**Parameters:**
- `layout` (BreadboardLayout): The breadboard layout to visualize
- `dpi` (int): Output resolution in DPI. Default: 300
- `show_labels` (bool): Whether to show component labels. Default: True

**Example:**
```python
visualizer = BreadboardVisualizer(layout, dpi=300)
```

#### Methods

##### draw()

```python
draw() -> None
```

Generate the breadboard visualization.

**Example:**
```python
visualizer.draw()
```

##### save()

```python
save(
    filename: str,
    format: str = "png",
    transparent: bool = False
) -> None
```

Save the visualization to a file.

**Parameters:**
- `filename` (str): Output file path
- `format` (str): Output format ("png", "svg", "pdf")
- `transparent` (bool): Use transparent background

**Example:**
```python
visualizer.save("output/breadboard.png", format="png")
visualizer.save("output/breadboard.svg", format="svg")
```

##### show()

```python
show() -> None
```

Display the visualization in a window (requires GUI environment).

**Example:**
```python
visualizer.show()
```

##### set_wire_color()

```python
set_wire_color(connection_id: str, color: str) -> None
```

Change the color of a specific wire connection.

**Parameters:**
- `connection_id` (str): ID of the connection
- `color` (str): New color (hex or name)

##### highlight_component()

```python
highlight_component(component: Component, color: str = "yellow") -> None
```

Highlight a specific component in the visualization.

**Parameters:**
- `component` (Component): Component to highlight
- `color` (str): Highlight color

---

### InstructionGenerator

Class for generating assembly instructions and bill of materials.

#### Constructor

```python
InstructionGenerator(
    layout: BreadboardLayout,
    include_images: bool = True,
    difficulty_level: str = "beginner"
)
```

**Parameters:**
- `layout` (BreadboardLayout): The breadboard layout
- `include_images` (bool): Include diagrams in instructions. Default: True
- `difficulty_level` (str): Target audience ("beginner", "intermediate", "advanced")

**Example:**
```python
generator = InstructionGenerator(layout, difficulty_level="beginner")
```

#### Methods

##### generate_instructions()

```python
generate_instructions() -> List[InstructionStep]
```

Generate step-by-step assembly instructions.

**Returns:**
- `List[InstructionStep]`: Ordered list of instruction steps

**Example:**
```python
instructions = generator.generate_instructions()
for i, step in enumerate(instructions, 1):
    print(f"Step {i}: {step.description}")
```

##### generate_bom()

```python
generate_bom(include_prices: bool = False) -> BillOfMaterials
```

Generate bill of materials.

**Parameters:**
- `include_prices` (bool): Include estimated prices (requires internet)

**Returns:**
- `BillOfMaterials`: Complete list of required components

**Example:**
```python
bom = generator.generate_bom()
print(f"Total components: {len(bom.items)}")
```

##### export_pdf()

```python
export_pdf(
    filename: str,
    include_bom: bool = True,
    include_diagrams: bool = True
) -> None
```

Export instructions to PDF format.

**Parameters:**
- `filename` (str): Output file path
- `include_bom` (bool): Include bill of materials
- `include_diagrams` (bool): Include breadboard diagrams

**Example:**
```python
generator.export_pdf("instructions.pdf", include_bom=True)
```

##### export_html()

```python
export_html(
    filename: str,
    theme: str = "light"
) -> None
```

Export instructions to HTML format.

**Parameters:**
- `filename` (str): Output file path
- `theme` (str): Visual theme ("light" or "dark")

##### export_markdown()

```python
export_markdown(filename: str) -> None
```

Export instructions to Markdown format.

**Parameters:**
- `filename` (str): Output file path

---

## AI Enhancement Module

### SchematicAnalyzer

Class for analyzing schematics using GPT-4 Vision API.

#### Constructor

```python
SchematicAnalyzer(
    api_key: str,
    model: str = "gpt-4-vision-preview",
    max_retries: int = 3,
    timeout: int = 30
)
```

**Parameters:**
- `api_key` (str): OpenAI API key
- `model` (str): Model name. Default: "gpt-4-vision-preview"
- `max_retries` (int): Maximum number of retry attempts
- `timeout` (int): Request timeout in seconds

**Example:**
```python
import os
analyzer = SchematicAnalyzer(api_key=os.getenv("OPENAI_API_KEY"))
```

#### Methods

##### analyze_schematic()

```python
analyze_schematic(
    image: Union[str, Image.Image],
    detail: str = "high"
) -> Dict[str, Any]
```

Analyze a schematic image and extract components and connections.

**Parameters:**
- `image` (Union[str, Image.Image]): Image file path or PIL Image object
- `detail` (str): Analysis detail level ("low", "high")

**Returns:**
- `Dict[str, Any]`: Analysis results containing components, connections, and metadata

**Example:**
```python
result = analyzer.analyze_schematic("schematic.png")
print(f"Found {len(result['components'])} components")
```

##### identify_components()

```python
identify_components(image: Union[str, Image.Image]) -> List[Component]
```

Identify individual components in the schematic.

**Returns:**
- `List[Component]`: List of identified components

##### extract_connections()

```python
extract_connections(image: Union[str, Image.Image]) -> List[Connection]
```

Extract connection information from the schematic.

**Returns:**
- `List[Connection]`: List of connections between components

##### validate_circuit()

```python
validate_circuit(
    components: List[Component],
    connections: List[Connection]
) -> ValidationResult
```

Validate the circuit for correctness and safety.

**Returns:**
- `ValidationResult`: Validation result with any warnings or errors

---

### ImprovedClassifier

Enhanced component classifier combining CNN and GPT-4 Vision.

#### Constructor

```python
ImprovedClassifier(
    cnn_model_path: str,
    gpt_analyzer: Optional[SchematicAnalyzer] = None,
    confidence_threshold: float = 0.85
)
```

**Parameters:**
- `cnn_model_path` (str): Path to trained CNN model
- `gpt_analyzer` (Optional[SchematicAnalyzer]): GPT-4 Vision analyzer for fallback
- `confidence_threshold` (float): Minimum confidence for CNN-only classification

**Example:**
```python
classifier = ImprovedClassifier(
    cnn_model_path="models/classifier.h5",
    gpt_analyzer=analyzer,
    confidence_threshold=0.85
)
```

#### Methods

##### classify()

```python
classify(image: Image.Image) -> ClassificationResult
```

Classify a component image.

**Parameters:**
- `image` (Image.Image): Component image

**Returns:**
- `ClassificationResult`: Classification result with type and confidence

**Example:**
```python
result = classifier.classify(component_image)
print(f"Component: {result.type}, Confidence: {result.confidence:.2%}")
```

##### batch_classify()

```python
batch_classify(images: List[Image.Image]) -> List[ClassificationResult]
```

Classify multiple component images.

**Parameters:**
- `images` (List[Image.Image]): List of component images

**Returns:**
- `List[ClassificationResult]`: List of classification results

---

## Integration Module

### CircuitNetBridge

Bridge between CircuitNet output and Breadboard Engine input.

#### Constructor

```python
CircuitNetBridge(
    use_gpt_enhancement: bool = False,
    gpt_analyzer: Optional[SchematicAnalyzer] = None
)
```

**Parameters:**
- `use_gpt_enhancement` (bool): Enable GPT-4 Vision enhancement
- `gpt_analyzer` (Optional[SchematicAnalyzer]): GPT-4 Vision analyzer instance

**Example:**
```python
bridge = CircuitNetBridge(use_gpt_enhancement=True, gpt_analyzer=analyzer)
```

#### Methods

##### process_schematic()

```python
process_schematic(
    image_path: str,
    output_dir: str = "output"
) -> Dict[str, Any]
```

Process a schematic image end-to-end.

**Parameters:**
- `image_path` (str): Path to schematic image
- `output_dir` (str): Output directory for generated files

**Returns:**
- `Dict[str, Any]`: Processing results including layout and file paths

**Example:**
```python
result = bridge.process_schematic("schematic.png", output_dir="output")
print(f"Breadboard layout: {result['breadboard_image']}")
print(f"Instructions: {result['instructions_pdf']}")
```

##### convert_to_breadboard()

```python
convert_to_breadboard(
    circuitnet_data: Dict[str, Any]
) -> BreadboardLayout
```

Convert CircuitNet output to breadboard layout.

**Parameters:**
- `circuitnet_data` (Dict[str, Any]): CircuitNet analysis results

**Returns:**
- `BreadboardLayout`: Generated breadboard layout

---

## Data Models

### Component

```python
@dataclass
class Component:
    type: str
    value: Optional[Union[int, float]]
    unit: Optional[str]
    position: Optional[Tuple[int, int]]
    orientation: str = "horizontal"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
```

### Connection

```python
@dataclass
class Connection:
    start: Tuple[int, int]
    end: Tuple[int, int]
    color: str = "black"
    wire_type: str = "signal"  # "signal", "power", "ground"
    path: Optional[List[Tuple[int, int]]] = None
```

### InstructionStep

```python
@dataclass
class InstructionStep:
    number: int
    description: str
    component: Optional[Component]
    image: Optional[str]
    notes: List[str] = field(default_factory=list)
```

### BillOfMaterials

```python
@dataclass
class BillOfMaterials:
    items: List[BOMItem]
    total_cost: Optional[float] = None
    
@dataclass
class BOMItem:
    component_type: str
    value: str
    quantity: int
    description: str
    part_number: Optional[str] = None
    estimated_price: Optional[float] = None
```

---

## Usage Examples

### Complete Workflow Example

```python
import os
from integration.circuit_to_breadboard import CircuitNetBridge
from ai_enhancement.gpt_vision import SchematicAnalyzer

# Initialize with GPT-4 Vision enhancement
analyzer = SchematicAnalyzer(api_key=os.getenv("OPENAI_API_KEY"))
bridge = CircuitNetBridge(use_gpt_enhancement=True, gpt_analyzer=analyzer)

# Process schematic
result = bridge.process_schematic(
    image_path="examples/schematics/led_circuit.png",
    output_dir="output"
)

# Output files are automatically generated:
# - output/breadboard_layout.png
# - output/instructions.pdf
# - output/bom.html
```

### Manual Workflow Example

```python
from breadboard.layout_engine import BreadboardLayout
from breadboard.visualizer import BreadboardVisualizer
from breadboard.instructions import InstructionGenerator
from breadboard.components import Resistor, LED

# Create layout
layout = BreadboardLayout()

# Place components
led = LED(color="red", voltage=2.0)
resistor = Resistor(value=220, unit="Ω")

layout.place_component(led, (15, 30))
layout.place_component(resistor, (15, 25))

# Route connections
layout.route_connection((15, 25), (15, 30), color="red")

# Visualize
visualizer = BreadboardVisualizer(layout)
visualizer.draw()
visualizer.save("breadboard.png")

# Generate instructions
generator = InstructionGenerator(layout)
generator.export_pdf("instructions.pdf")
```

---

## Error Handling

### Common Exceptions

#### ComponentConflictError

Raised when trying to place a component in an occupied position.

```python
from breadboard.exceptions import ComponentConflictError

try:
    layout.place_component(component, (10, 15))
except ComponentConflictError as e:
    print(f"Placement conflict: {e}")
    # Try alternative position
```

#### RoutingError

Raised when wire routing fails.

```python
from breadboard.exceptions import RoutingError

try:
    path = layout.route_connection((10, 15), (20, 30))
except RoutingError as e:
    print(f"Routing failed: {e}")
```

#### APIError

Raised when GPT-4 Vision API calls fail.

```python
from ai_enhancement.exceptions import APIError

try:
    result = analyzer.analyze_schematic("schematic.png")
except APIError as e:
    print(f"API error: {e}")
    # Fall back to CNN-only approach
```

### Error Handling Best Practices

```python
from breadboard.exceptions import BreadboardError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    result = bridge.process_schematic("schematic.png")
except BreadboardError as e:
    logger.error(f"Breadboard processing failed: {e}")
    # Implement fallback or user notification
except Exception as e:
    logger.exception("Unexpected error occurred")
    raise
```

---

## Additional Resources

- **Source Code**: [GitHub Repository](https://github.com/sobereyed323/AI-Schematic-To-Breadboard)
- **Examples**: See `examples/` directory
- **Contributing**: See `docs/CONTRIBUTING.md`
- **Architecture**: See `docs/ARCHITECTURE.md`

---

**Version**: 1.0  
**Last Updated**: January 2026
