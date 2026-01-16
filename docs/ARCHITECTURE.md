# System Architecture - CircuitNet to Breadboard Enhancement

## 🏗️ Architecture Overview

This document describes the system architecture for the enhanced CircuitNet project, which extends the original circuit diagram generation capabilities with breadboard layout generation and AI-powered enhancements.

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface Layer                      │
│  ┌──────────────────┐              ┌──────────────────────────┐ │
│  │  Web Application │              │   Command Line Interface │ │
│  │   (Streamlit)    │              │        (Python)          │ │
│  └──────────────────┘              └──────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     Integration Layer                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            CircuitNetBridge                                 │ │
│  │  - Format conversion                                        │ │
│  │  - Data transformation                                      │ │
│  │  - Workflow orchestration                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────┬───────────────────────────────┬────────────────┘
                 │                               │
     ┌───────────▼─────────┐         ┌──────────▼───────────────┐
     │  Original CircuitNet│         │  Breadboard Engine       │
     │     Components      │         │     (New)                │
     └───────────┬─────────┘         └──────────┬───────────────┘
                 │                               │
     ┌───────────▼──────────┐       ┌───────────▼───────────────┐
     │ • Component Detection│       │ • Layout Engine           │
     │ • CNN Classification │       │ • Visualizer              │
     │ • Circuit Generation │       │ • Instruction Generator   │
     └──────────────────────┘       └───────────────────────────┘
                 │                               │
                 └───────────┬───────────────────┘
                             │
                 ┌───────────▼──────────────────┐
                 │   AI Enhancement Layer       │
                 │  - GPT-4 Vision API          │
                 │  - Enhanced Classifier       │
                 └──────────────────────────────┘
```

---

## 2. Current CircuitNet Architecture

### 2.1 Component Detection Module
**Location**: `notebooks/object_detection.ipynb`

**Purpose**: Detect and segment individual circuit components from hand-drawn schematics

**Key Techniques**:
- Traditional image processing (thresholding, contour detection)
- Connected component analysis
- Bounding box extraction

**Inputs**: Hand-drawn schematic images
**Outputs**: List of component bounding boxes and cropped component images

### 2.2 Component Classification Module
**Location**: `notebooks/neural_network.ipynb`

**Purpose**: Classify detected components using deep learning

**Architecture**:
- Convolutional Neural Network (CNN)
- 5 output classes: resistor, capacitor, inductor, voltage source, current source
- 96.5% accuracy on test set

**Inputs**: Cropped component images (normalized)
**Outputs**: Component type predictions with confidence scores

### 2.3 Circuit Generation Module
**Location**: `notebooks/circuit_generation.ipynb`

**Purpose**: Generate professional circuit diagrams from detected and classified components

**Process**:
1. Process component spatial relationships
2. Generate netlist (JSON format)
3. Render SVG circuit diagram
4. Export to PNG

**Inputs**: Component types and positions
**Outputs**: Circuit diagram (SVG/PNG), netlist (JSON)

---

## 3. New Breadboard Engine Architecture

### 3.1 Module Structure

```
breadboard/
├── __init__.py              # Package initialization, exports
├── layout_engine.py         # Core layout algorithms
├── visualizer.py            # Breadboard visualization
└── instructions.py          # Instruction generation
```

### 3.2 BreadboardLayout Class (`layout_engine.py`)

**Responsibilities**:
- Represent breadboard grid structure
- Place components on breadboard
- Route wire connections
- Detect and resolve conflicts
- Optimize layout

**Key Data Structures**:
```python
class BreadboardLayout:
    grid: np.ndarray              # 2D array representing breadboard
    components: List[Component]    # Placed components
    connections: List[Connection]  # Wire connections
    power_rails: Dict[str, List]   # Power and ground rails
    occupied_positions: Set[Tuple] # Track used holes
```

**Key Algorithms**:
1. **Component Placement**
   - Grid-based positioning
   - Orientation optimization
   - Spacing management
   - Left-to-right, top-to-bottom heuristic

2. **Connection Routing**
   - A* pathfinding algorithm
   - Manhattan distance heuristic
   - Wire crossing minimization
   - Power rail utilization

3. **Conflict Detection**
   - Overlapping component detection
   - Invalid connection identification
   - Boundary checking

**Algorithm Complexity**:
- Placement: O(n) where n = number of components
- Routing: O(m * log(k)) where m = connections, k = grid size
- Conflict detection: O(n²) worst case

### 3.3 BreadboardVisualizer Class (`visualizer.py`)

**Responsibilities**:
- Render breadboard grid
- Draw components at specified positions
- Draw wire connections with colors
- Add labels and annotations
- Export to multiple formats

**Rendering Pipeline**:
```
1. Initialize canvas (matplotlib figure or PIL image)
2. Draw breadboard base (grid, power rails)
3. Draw components (with correct symbols)
4. Draw wires (color-coded, anti-aliased)
5. Add labels (component IDs, values)
6. Export to file (PNG/SVG)
```

**Component Library**:
- Resistor (with color bands)
- Capacitor (electrolytic and ceramic)
- LED (with polarity indication)
- IC (with pin numbering)
- Transistor (with pin labels)
- Jumper wires (various colors)

**Visual Standards**:
- Standard breadboard dimensions (830-point)
- Color coding for wires (red=power, black=ground, etc.)
- Clear component orientation indicators
- High-resolution output (300+ DPI for PNG)

### 3.4 InstructionGenerator Class (`instructions.py`)

**Responsibilities**:
- Generate step-by-step assembly instructions
- Create bill of materials (BOM)
- Export to multiple formats
- Include helpful tips

**Instruction Algorithm**:
```
1. Determine component placement order
   - Power components first
   - ICs next (they're largest)
   - Passive components last
2. Generate numbered steps
   - Clear, concise language
   - Position references (e.g., "row 15, column J")
   - Component orientation warnings
3. Add wiring steps
   - Group by color
   - Minimize wire crossings
   - Power connections first
4. Include testing checkpoints
```

**Output Formats**:
- **PDF**: Professional layout with images
- **HTML**: Interactive, web-friendly
- **Markdown**: Easy to edit and version control

---

## 4. AI Enhancement Integration

### 4.1 Module Structure

```
ai_enhancement/
├── __init__.py                 # Package initialization
├── gpt_vision.py              # GPT-4 Vision API integration
└── improved_classifier.py     # Enhanced classification
```

### 4.2 SchematicAnalyzer Class (`gpt_vision.py`)

**Purpose**: Leverage GPT-4 Vision for advanced schematic understanding

**Architecture**:
```python
class SchematicAnalyzer:
    def __init__(self, api_key: str)
    def analyze_schematic(self, image: Image) -> Dict
    def identify_components(self, image: Image) -> List[Component]
    def extract_connections(self, image: Image) -> List[Connection]
    def validate_circuit(self, components, connections) -> ValidationResult
```

**Integration Points**:
- **Input**: Schematic image (preprocessed)
- **Output**: Component list, connection list, validation report
- **Fallback**: If API fails, use CNN-only approach

**API Request Flow**:
```
1. Preprocess image (resize, enhance contrast)
2. Construct prompt with circuit analysis instructions
3. Send request to OpenAI API
4. Parse JSON response
5. Validate and format results
6. Return structured data
```

**Error Handling**:
- Rate limiting (exponential backoff)
- Timeout handling (30s default)
- API error recovery
- Response validation

**Cost Optimization**:
- Image compression before upload
- Caching of results
- Batch processing where possible
- Only use for complex circuits or low-confidence CNN predictions

### 4.3 ImprovedClassifier Class (`improved_classifier.py`)

**Purpose**: Combine CNN and GPT-4 Vision for better accuracy

**Architecture**:
```python
class ImprovedClassifier:
    def __init__(self, cnn_model, gpt_analyzer)
    def classify(self, component_image: Image) -> ClassificationResult
    def get_confidence(self) -> float
    def should_fallback_to_gpt(self, confidence: float) -> bool
```

**Classification Pipeline**:
```
1. Run CNN classification
2. Get confidence score
3. If confidence > threshold (e.g., 0.85):
   - Use CNN result
4. If confidence < threshold:
   - Fallback to GPT-4 Vision
   - Combine predictions
5. Return final classification with confidence
```

**Confidence Threshold Tuning**:
- Default: 0.85
- Adjustable based on use case
- Higher threshold = more GPT-4 calls = higher cost but better accuracy
- Lower threshold = fewer GPT-4 calls = lower cost but potentially lower accuracy

---

## 5. Integration Architecture

### 5.1 CircuitNetBridge Class (`integration/circuit_to_breadboard.py`)

**Purpose**: Bridge between CircuitNet output and Breadboard Engine input

**Responsibilities**:
- Format conversion
- Coordinate transformation
- Component type mapping
- Connection extraction

**Data Flow**:
```
CircuitNet Output          Bridge Processing         Breadboard Input
─────────────────          ─────────────────         ────────────────
Component List      →      Type Mapping       →      Component Objects
 - Type                     - Resistor → Resistor    - Type
 - Position (x,y)           - Capacitor → Capacitor  - Grid Position (row,col)
 - Bounding Box             etc.                     - Orientation
                                                      - Value/Rating
Netlist JSON        →      Connection Parsing →      Connection Objects
 - Nodes                    - Extract net info       - Start Point
 - Components               - Map to grid coords     - End Point
 - Connections              - Determine routing      - Wire Color
                                                      - Priority
```

**Transformation Functions**:
```python
def pixel_to_grid(x: int, y: int) -> Tuple[int, int]
    """Convert pixel coordinates to breadboard grid coordinates"""

def map_component_type(circuit_type: str) -> BreadboardComponent
    """Map CircuitNet component types to breadboard components"""

def extract_connections(netlist: Dict) -> List[Connection]
    """Extract connection information from netlist"""

def optimize_layout(components: List) -> List
    """Optimize component arrangement for breadboard"""
```

---

## 6. Data Flow Diagrams

### 6.1 End-to-End Processing Flow

```
┌─────────────┐
│   Upload    │
│  Schematic  │
│    Image    │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Object Detection   │
│  (Original CircuitNet)
│  - Segment components
│  - Extract regions   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Classification    │
│  (CNN + GPT-4)      │
│  - Identify types   │
│  - Get confidence   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Circuit Generation │
│  (Original CircuitNet)
│  - Create netlist   │
│  - Generate diagram │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  CircuitNet Bridge  │
│  - Convert formats  │
│  - Extract connections
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Breadboard Layout  │
│  - Place components │
│  - Route connections│
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Visualization     │
│  - Draw breadboard  │
│  - Export images    │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│    Instructions     │
│  - Generate steps   │
│  - Create BOM       │
│  - Export documents │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│   Output    │
│   Files     │
└─────────────┘
```

### 6.2 Component Placement Algorithm Flow

```
Input: List of components from CircuitNet

1. Sort components by size (ICs first, then passives)
2. Initialize breadboard grid (all positions free)
3. For each component:
   a. Find available space on grid
   b. Calculate optimal position (minimize wire length)
   c. Check for conflicts with placed components
   d. If conflict, try alternative positions
   e. Place component and mark grid positions as occupied
   f. Record placement in layout
4. Return completed layout

Output: BreadboardLayout with all components placed
```

### 6.3 Wire Routing Algorithm Flow

```
Input: List of connections, BreadboardLayout

1. Sort connections by priority (power first, then signals)
2. For each connection:
   a. Get start and end positions from component pins
   b. Check if direct connection is possible
   c. If not, run A* pathfinding:
      - Avoid occupied positions
      - Prefer straight lines (Manhattan routing)
      - Minimize crossings
   d. If path found:
      - Mark grid positions as occupied by wire
      - Add wire to layout
   e. If no path found:
      - Try alternative routing strategies
      - Report if impossible
3. Optimize wire colors for clarity
4. Return layout with all connections routed

Output: BreadboardLayout with routed connections
```

---

## 7. Module Dependencies

### 7.1 Dependency Graph

```
web_app/app.py
    │
    ├─→ integration/circuit_to_breadboard.py
    │       │
    │       ├─→ breadboard/layout_engine.py
    │       │       │
    │       │       └─→ breadboard/visualizer.py
    │       │
    │       └─→ ai_enhancement/improved_classifier.py
    │               │
    │               └─→ ai_enhancement/gpt_vision.py
    │
    └─→ breadboard/instructions.py
            │
            └─→ breadboard/layout_engine.py
```

### 7.2 External Dependencies

**Core Libraries**:
- `numpy`: Numerical operations, grid representation
- `matplotlib`: Visualization, plotting
- `PIL/Pillow`: Image processing
- `opencv-python`: Image preprocessing (inherited from CircuitNet)

**AI/ML Libraries**:
- `tensorflow`: CNN model (inherited from CircuitNet)
- `openai`: GPT-4 Vision API integration

**Web Framework**:
- `streamlit`: Web application interface
- `flask`: Alternative REST API (optional)

**Document Generation**:
- `reportlab`: PDF generation
- `markdown`: Markdown export

**Utilities**:
- `python-dotenv`: Environment variable management
- `pytest`: Testing framework

---

## 8. Configuration and Settings

### 8.1 Environment Variables

```env
# API Configuration
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4-vision-preview
MAX_RETRIES=3
TIMEOUT=30

# Breadboard Settings
BREADBOARD_ROWS=30
BREADBOARD_COLUMNS=63
POWER_RAIL_ROWS=4
DEFAULT_SPACING=3

# Routing Settings
WIRE_CROSSING_PENALTY=10
ROUTING_MAX_ITERATIONS=1000

# Output Settings
OUTPUT_DPI=300
DEFAULT_WIRE_WIDTH=2
COMPONENT_LABEL_SIZE=8

# Logging
LOG_LEVEL=INFO
LOG_FILE=breadboard.log
```

### 8.2 Configuration Files

**breadboard/config.py**:
```python
class BreadboardConfig:
    ROWS = 30
    COLUMNS = 63
    HOLE_DIAMETER = 1.8  # mm
    HOLE_SPACING = 2.54  # mm (0.1 inch)
    
class VisualizationConfig:
    DPI = 300
    WIRE_COLORS = {
        'power': '#FF0000',
        'ground': '#000000',
        'signal': ['#0000FF', '#00FF00', '#FFA500', ...]
    }
```

---

## 9. Scalability and Performance

### 9.1 Performance Considerations

**Component Placement**:
- Time Complexity: O(n) where n = number of components
- Space Complexity: O(r × c) for grid, where r = rows, c = columns
- Expected: <1 second for typical circuits (< 20 components)

**Wire Routing**:
- Time Complexity: O(m × k log k) where m = connections, k = grid size
- Space Complexity: O(k) for pathfinding
- Expected: <5 seconds for typical circuits (< 30 connections)

**Visualization**:
- Time Complexity: O(n + m) for rendering
- Memory: ~10MB for high-res PNG
- Expected: <2 seconds for rendering

**Total Processing Time**: <10 seconds for typical circuit

### 9.2 Scalability Strategies

**For Larger Circuits**:
1. **Grid Partitioning**: Divide breadboard into regions
2. **Parallel Processing**: Process independent components in parallel
3. **Caching**: Cache component placements and routes
4. **Progressive Rendering**: Show partial results while processing

**For High Traffic** (Web App):
1. **Queue System**: Process requests asynchronously
2. **Result Caching**: Cache results for identical inputs
3. **Load Balancing**: Distribute across multiple servers
4. **Rate Limiting**: Prevent API abuse

---

## 10. Security Considerations

### 10.1 API Key Management
- Store keys in environment variables, never in code
- Use key rotation policies
- Implement usage monitoring and alerting

### 10.2 Input Validation
- Validate uploaded image files (type, size, content)
- Sanitize user inputs (component names, values)
- Prevent path traversal attacks

### 10.3 Rate Limiting
- Limit API calls per user/IP
- Implement exponential backoff
- Monitor for unusual patterns

### 10.4 Output Security
- Sanitize generated HTML/Markdown
- Prevent XSS in web interface
- Validate PDF generation inputs

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Test each class and method independently
- Mock external dependencies (API calls)
- Achieve >80% code coverage

### 11.2 Integration Tests
- Test module interactions
- End-to-end workflow tests
- Validate data transformations

### 11.3 Performance Tests
- Benchmark processing times
- Memory usage profiling
- Load testing for web interface

### 11.4 Visual Tests
- Validate breadboard renderings
- Check component placements
- Verify instruction accuracy

---

## 12. Future Architecture Enhancements

### 12.1 Microservices Architecture
- Separate services for detection, classification, layout, visualization
- API gateway for routing
- Independent scaling

### 12.2 Database Integration
- Store user projects
- Cache API results
- Track usage analytics

### 12.3 Real-time Collaboration
- WebSocket connections
- Shared editing sessions
- Version control

### 12.4 Mobile Support
- Responsive web design
- Mobile-optimized interface
- Camera integration for direct capture

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Authors**: CircuitNet Enhancement Team
