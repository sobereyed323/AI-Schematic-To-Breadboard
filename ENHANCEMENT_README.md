# CircuitNet Enhanced: AI-Powered Breadboard Conversion

## 🎯 Project Vision

CircuitNet Enhanced extends the original CircuitNet project to not only convert hand-drawn circuit sketches into professional circuit diagrams, but also generate practical breadboard layouts with step-by-step wiring instructions. This enhancement bridges the gap between circuit design and physical implementation, making electronics projects more accessible to students, hobbyists, and educators.

## 🌟 Key Goals

1. **Automated Breadboard Layout Generation**: Convert electronic schematics into optimized breadboard layouts
2. **Step-by-Step Instructions**: Generate clear, beginner-friendly wiring instructions
3. **AI-Enhanced Analysis**: Leverage GPT-4 Vision API for improved component recognition
4. **Visual Output**: Create detailed breadboard diagrams with component placement and wire routing
5. **Bill of Materials**: Automatically generate parts lists with specifications
6. **Web Interface**: Provide an intuitive web application for easy access

## 📋 New Features Overview

### Breadboard Conversion Engine
- **Smart Component Placement**: Intelligent algorithm for placing components on a standard 830-point breadboard
- **Connection Routing**: Optimized wire routing with minimal crossings
- **Conflict Detection**: Automatic detection and resolution of overlapping components
- **Multi-Format Export**: Generate layouts in PNG, SVG, PDF, and HTML formats

### AI Enhancement
- **GPT-4 Vision Integration**: Advanced schematic analysis using OpenAI's GPT-4 Vision API
- **Improved Classification**: Enhanced component recognition with confidence scoring
- **Fallback Mechanisms**: Automatic fallback to AI when confidence is low
- **Support for Extended Component Library**: Recognizes resistors, capacitors, LEDs, ICs, transistors, and more

### Output Generation
- **Visual Breadboard Diagrams**: High-quality breadboard visualizations with color-coded wires
- **Step-by-Step Instructions**: Numbered instructions for assembly
- **Bill of Materials**: Complete parts list with quantities and specifications
- **Multiple Formats**: Export to PDF, HTML, Markdown, PNG, and SVG

### Web Interface
- **File Upload**: Easy upload of schematic images
- **Live Preview**: Real-time visualization of uploaded schematics
- **One-Click Conversion**: Simple interface to trigger breadboard conversion
- **Download Options**: Multiple download formats for outputs

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sobereyed323/AI-Schematic-To-Breadboard.git
   cd AI-Schematic-To-Breadboard
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install base dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install enhanced dependencies**:
   ```bash
   pip install -r requirements-enhanced.txt
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

6. **Extract the dataset** (for training/testing):
   ```bash
   cd dataset/
   tar -xzvf circuit_dataset.tar.gz
   cd ..
   ```

## ⚡ Quick Start

### Basic Usage

#### Command Line Interface
```python
from integration.circuit_to_breadboard import CircuitNetBridge
from breadboard.layout_engine import BreadboardLayout
from breadboard.visualizer import BreadboardVisualizer
from breadboard.instructions import InstructionGenerator

# Initialize the bridge
bridge = CircuitNetBridge()

# Load and process schematic
schematic_path = "examples/schematics/led_circuit.png"
breadboard_data = bridge.process_schematic(schematic_path)

# Generate layout
layout = BreadboardLayout()
layout.place_components(breadboard_data['components'])
layout.route_connections(breadboard_data['connections'])

# Visualize
visualizer = BreadboardVisualizer(layout)
visualizer.draw()
visualizer.save("output/breadboard_layout.png")

# Generate instructions
generator = InstructionGenerator(layout)
instructions = generator.generate_instructions()
generator.export_pdf("output/instructions.pdf")
```

#### Web Interface
```bash
cd web_app
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

### Example Projects

We include several example circuits in the `examples/schematics/` directory:
- **Simple LED Circuit**: Basic LED with resistor
- **555 Timer Circuit**: Classic timer IC circuit
- More examples coming soon!

See `examples/README.md` for detailed information about each example.

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[ROADMAP.md](docs/ROADMAP.md)**: Development phases and timeline
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: System architecture and design
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)**: Contribution guidelines
- **[API.md](docs/API.md)**: API reference and usage examples

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on:
- Code style and conventions
- Pull request process
- Issue reporting
- Development workflow

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-enhanced.txt
pip install pytest pytest-cov black flake8

# Run tests
pytest tests/

# Run linter
flake8 breadboard/ ai_enhancement/ integration/

# Format code
black breadboard/ ai_enhancement/ integration/
```

## 🧪 Testing

Run the test suite:
```bash
# All tests
pytest

# Specific test file
pytest tests/test_breadboard.py

# With coverage
pytest --cov=breadboard --cov=ai_enhancement --cov=integration
```

## 📦 Project Structure

```
AI-Schematic-To-Breadboard/
├── breadboard/              # Breadboard layout engine
│   ├── __init__.py
│   ├── layout_engine.py    # Component placement and routing
│   ├── visualizer.py       # Breadboard visualization
│   └── instructions.py     # Instruction generation
├── ai_enhancement/          # AI-powered enhancements
│   ├── __init__.py
│   ├── gpt_vision.py       # GPT-4 Vision integration
│   └── improved_classifier.py
├── integration/             # Integration modules
│   └── circuit_to_breadboard.py
├── web_app/                 # Streamlit web interface
│   ├── app.py
│   └── README.md
├── examples/                # Example circuits
│   ├── README.md
│   └── schematics/
├── tests/                   # Test suite
│   └── test_breadboard.py
├── docs/                    # Documentation
│   ├── ROADMAP.md
│   ├── ARCHITECTURE.md
│   ├── CONTRIBUTING.md
│   └── API.md
├── notebooks/               # Original Jupyter notebooks
├── dataset/                 # Training dataset
├── requirements.txt         # Base dependencies
├── requirements-enhanced.txt # Enhanced dependencies
├── .env.example            # Environment variables template
└── README.md               # Original CircuitNet README
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4-vision-preview

# Optional: Custom settings
MAX_RETRIES=3
TIMEOUT=30
LOG_LEVEL=INFO
```

### Breadboard Settings

Default breadboard configuration can be customized in your code:
```python
from breadboard.layout_engine import BreadboardLayout

layout = BreadboardLayout(
    rows=30,
    columns=63,
    power_rail_rows=4,
    component_spacing=3
)
```

## 🎓 Learning Resources

- **Original CircuitNet Paper**: [Link to paper if available]
- **Breadboard Tutorial**: Coming soon
- **API Documentation**: See `docs/API.md`
- **Video Tutorials**: Coming soon

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- **Original CircuitNet**: Created by aaanthonyyy
- **Dr. Akash Pooransingh**: Project supervisor for original CircuitNet
- **OpenAI**: For GPT-4 Vision API
- **Community Contributors**: Thank you to all contributors!

## 📧 Contact

For questions, issues, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Join our community discussions

## 🗺️ Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for detailed development plans and upcoming features.

Current Status: **Phase 1 - Foundation Complete**

Next Up:
- Enhanced AI integration
- Advanced routing algorithms
- Multi-layer breadboard support
- Component library expansion

---

**Note**: This is an enhanced version of CircuitNet. The original circuit diagram generation features remain fully functional.
