# Example Schematics

This directory contains example electronic schematics that can be used to test and demonstrate the breadboard conversion capabilities of CircuitNet Enhanced.

## Available Examples

### 1. Simple LED Circuit

**File**: `led_circuit.txt` (description placeholder)

**Description**: A basic LED circuit with a current-limiting resistor, powered by a 5V supply.

**Components**:
- 1x Red LED (5mm)
- 1x 220Ω Resistor (1/4W)
- 1x 5V Power Supply
- Jumper wires

**Difficulty**: Beginner

**Expected Output**:
- Breadboard layout showing LED and resistor placement
- Step-by-step wiring instructions
- Warning about LED polarity

**Learning Objectives**:
- Understanding LED polarity
- Current-limiting resistor calculation
- Basic breadboard usage

---

### 2. 555 Timer Circuit

**File**: `555_timer_circuit.txt` (description placeholder)

**Description**: Classic astable 555 timer circuit for LED blinking at approximately 1Hz.

**Components**:
- 1x 555 Timer IC
- 2x Capacitors (10µF, 100nF)
- 2x Resistors (10kΩ, 100kΩ)
- 1x LED
- 1x 220Ω Resistor (for LED)
- 1x 9V Power Supply
- Jumper wires

**Difficulty**: Intermediate

**Expected Output**:
- Breadboard layout with proper IC orientation
- Detailed pin-by-pin connections
- Circuit explanation and timing calculations
- Testing procedures

**Learning Objectives**:
- IC placement and orientation
- Astable multivibrator operation
- Capacitor and resistor timing calculations
- Power supply decoupling

---

### 3. Voltage Divider

**File**: `voltage_divider.txt` (description placeholder - TODO)

**Description**: Simple voltage divider circuit for reducing voltage levels.

**Components**:
- 2x Resistors (values TBD)
- Jumper wires

**Difficulty**: Beginner

---

### 4. Transistor Switch

**File**: `transistor_switch.txt` (description placeholder - TODO)

**Description**: NPN transistor used as a switch to control an LED.

**Components**:
- 1x NPN Transistor (2N2222 or similar)
- 1x LED
- 2x Resistors (values TBD)
- Jumper wires

**Difficulty**: Intermediate

---

## How to Use Examples

### Method 1: Command Line

```python
from integration.circuit_to_breadboard import CircuitNetBridge

bridge = CircuitNetBridge()
result = bridge.process_schematic(
    "examples/schematics/led_circuit.png",  # You'll need to add actual images
    output_dir="examples/output"
)

print(f"Breadboard layout: {result['breadboard_image']}")
print(f"Instructions: {result['instructions_html']}")
```

### Method 2: Web Interface

1. Start the web application:
   ```bash
   cd web_app
   streamlit run app.py
   ```

2. Upload an example schematic image
3. Click "Convert to Breadboard"
4. Download results

### Method 3: Jupyter Notebook

See `notebooks/breadboard_demo.ipynb` (TODO) for interactive examples.

---

## Adding Your Own Examples

To add a new example:

1. Create a clear, hand-drawn or digital schematic
2. Save as PNG or JPEG in this directory
3. Add a description file (`.txt`) with the same name
4. Update this README with:
   - Component list
   - Difficulty level
   - Learning objectives
   - Expected output

### Description File Format

```
Title: Your Circuit Name
Difficulty: Beginner/Intermediate/Advanced

Description:
Brief description of what the circuit does

Components:
- Component 1
- Component 2
...

Notes:
- Any special considerations
- Safety warnings
- Tips for success
```

---

## Testing Your Examples

To test an example:

```bash
# Run the test suite
pytest tests/test_examples.py

# Test specific example
pytest tests/test_examples.py -k "led_circuit"
```

---

## Image Requirements

For best results, schematic images should:
- Be clear and high-contrast
- Show component labels (R1, C1, IC1, etc.)
- Include component values when possible
- Use standard electronic symbols
- Be at least 800x600 pixels
- Be in PNG, JPEG, or SVG format

---

## Example Output Structure

For each processed example, you'll get:

```
examples/output/
├── led_circuit/
│   ├── breadboard_layout.png      # Visual breadboard diagram
│   ├── instructions.html          # Interactive HTML instructions
│   ├── instructions.md            # Markdown instructions
│   └── bom.txt                    # Bill of materials
```

---

## Contributing Examples

We welcome contributions of new example circuits! Please:

1. Ensure the circuit is safe and educational
2. Test the circuit physically if possible
3. Provide clear, accurate schematics
4. Include detailed component specifications
5. Add appropriate difficulty level
6. Follow the format above

See [CONTRIBUTING.md](../../docs/CONTRIBUTING.md) for more details.

---

## Troubleshooting

### Common Issues

**Issue**: Component not recognized
- **Solution**: Ensure components use standard symbols
- Check that component labels are clear
- Try enhancing image contrast

**Issue**: Poor layout quality
- **Solution**: Use higher resolution images
- Ensure adequate spacing between components
- Check that all connections are visible

**Issue**: Incorrect connections
- **Solution**: Verify schematic is correct
- Check for wire crossings or overlaps
- Ensure net labels are clear

---

## Resources

- **Electronics Tutorials**: [All About Circuits](https://www.allaboutcircuits.com/)
- **Breadboard Guide**: [SparkFun Tutorial](https://learn.sparkfun.com/tutorials/how-to-use-a-breadboard)
- **Circuit Symbols**: [Standard Schematic Symbols](https://www.electronics-tutorials.ws/resources/basic-schematic-symbols.html)

---

**Note**: This directory currently contains placeholder descriptions. Actual schematic images need to be added for full functionality.

To get started, you can:
1. Draw your own schematics using tools like KiCad, Fritzing, or CircuitLab
2. Use schematics from open-source electronics projects
3. Scan hand-drawn schematics

**Last Updated**: January 2026
