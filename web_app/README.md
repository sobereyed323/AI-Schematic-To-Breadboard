# Web Application - CircuitNet to Breadboard

This directory contains the Streamlit-based web interface for converting electronic schematics into breadboard layouts.

## 🚀 Quick Start

### 1. Installation

Make sure you have all dependencies installed:

```bash
# From the project root directory
pip install -r requirements.txt
pip install -r requirements-enhanced.txt
```

### 2. Running the Application

```bash
cd web_app
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### 3. Using the Application

1. **Upload a Schematic**: Click "Browse files" and select your schematic image (PNG, JPEG, or SVG)
2. **Configure Settings** (optional):
   - Enable GPT-4 Vision enhancement
   - Adjust output DPI
   - Set instruction difficulty level
3. **Convert**: Click the "Convert to Breadboard" button
4. **Download Results**: Download the breadboard layout image and instructions

## 📋 Features

### Core Features
- 📤 **File Upload**: Support for PNG, JPEG, and SVG images
- 🎨 **Visual Preview**: Preview uploaded schematics
- 🔄 **Real-time Conversion**: Convert schematics to breadboard layouts
- 📊 **Statistics Display**: View component counts and layout metrics
- 💾 **Multiple Downloads**: Download layouts and instructions in various formats

### Optional Features
- 🤖 **GPT-4 Vision Integration**: Enhanced component recognition (requires API key)
- ⚙️ **Customizable Settings**: Adjust DPI, labels, and difficulty level
- 📖 **Instruction Preview**: View instructions before downloading
- 📋 **Bill of Materials**: Auto-generated parts list

## 🎛️ Configuration

### Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```env
OPENAI_API_KEY=your_api_key_here
STREAMLIT_SERVER_PORT=8501
MAX_UPLOAD_SIZE_MB=10
```

### Streamlit Configuration

Create `.streamlit/config.toml` for advanced settings:

```toml
[server]
port = 8501
maxUploadSize = 10

[theme]
primaryColor = "#4A90E2"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## 🖼️ Screenshots

### Main Interface
The main interface provides a clean, two-column layout:
- **Left**: Upload and preview schematic
- **Right**: Results and downloads

### Upload Section
Users can drag-and-drop or browse for schematic files. Uploaded images are displayed with dimension information.

### Results Section
After conversion, results include:
- Visual breadboard layout
- Component statistics
- Bill of materials
- Download buttons for all outputs

### Settings Sidebar
The sidebar includes:
- GPT-4 Vision toggle and API key input
- Output format settings (DPI, labels)
- Instruction difficulty level
- Help and examples

## 💡 Usage Tips

### For Best Results

1. **Image Quality**:
   - Use high-resolution images (minimum 800x600)
   - Ensure good contrast between components and background
   - Make sure component labels are legible

2. **Schematic Format**:
   - Use standard electronic symbols
   - Label components clearly (R1, C1, LED1, etc.)
   - Include component values when possible
   - Show all connections clearly

3. **GPT-4 Vision**:
   - Enable for complex or hand-drawn schematics
   - Provides better component recognition
   - Requires OpenAI API key (costs apply)

### Troubleshooting

**Issue**: Application won't start
- **Solution**: Ensure all dependencies are installed
  ```bash
  pip install -r requirements-enhanced.txt
  ```

**Issue**: Upload button not appearing
- **Solution**: Check file size limit in `.streamlit/config.toml`

**Issue**: Conversion takes too long
- **Solution**: 
  - Reduce image resolution
  - Disable GPT-4 Vision for simple circuits
  - Check internet connection if using GPT-4

**Issue**: "Import error" messages
- **Solution**: Verify all modules are in correct directories
  ```bash
  python -c "from integration.circuit_to_breadboard import CircuitNetBridge"
  ```

## 🔧 Development

### Project Structure

```
web_app/
├── app.py              # Main Streamlit application
├── README.md           # This file
└── .streamlit/         # Streamlit configuration (optional)
    └── config.toml
```

### Running in Development Mode

```bash
# Enable debug mode
streamlit run app.py --logger.level=debug

# Custom port
streamlit run app.py --server.port=8080

# Watch for file changes
streamlit run app.py --server.fileWatcherType=poll
```

### Adding New Features

1. **New Output Format**:
   - Add export method in `breadboard/instructions.py`
   - Update download buttons in `app.py`

2. **Custom Visualization**:
   - Modify `breadboard/visualizer.py`
   - Update display settings in sidebar

3. **Additional Settings**:
   - Add new inputs in sidebar
   - Pass parameters to CircuitNetBridge

## 📚 API Reference

### Key Functions

#### `main()`
Main application entry point. Sets up the Streamlit interface and handles user interactions.

#### `get_binary_file_downloader_html(file_path, file_label, button_text)`
Generates HTML for file download links.

**Parameters:**
- `file_path`: Path to file to download
- `file_label`: Filename for downloaded file
- `button_text`: Text to display on button

**Returns:**
- HTML string with download link

## 🎨 Customization

### Changing Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF4B4B"        # Red theme
backgroundColor = "#0E1117"      # Dark mode
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

### Custom CSS

Modify the CSS in `app.py`:

```python
st.markdown("""
    <style>
    .custom-class {
        /* Your styles here */
    }
    </style>
""", unsafe_allow_html=True)
```

### Adding Logo

```python
from PIL import Image

logo = Image.open("path/to/logo.png")
st.image(logo, width=200)
```

## 🚀 Deployment

### Local Deployment

Already covered in Quick Start section above.

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy!

**Note**: Add secrets in Streamlit Cloud dashboard for API keys.

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements-enhanced.txt ./
RUN pip install -r requirements.txt -r requirements-enhanced.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "web_app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t circuitnet-breadboard .
docker run -p 8501:8501 circuitnet-breadboard
```

### Heroku Deployment

Create `Procfile`:

```
web: streamlit run web_app/app.py --server.port=$PORT --server.address=0.0.0.0
```

Deploy:

```bash
heroku create your-app-name
git push heroku main
```

## 🔒 Security

### API Key Handling

- Never commit API keys to version control
- Use environment variables or Streamlit secrets
- Implement rate limiting for public deployments

### Input Validation

The app validates:
- File types (only images allowed)
- File sizes (configurable limit)
- API key format (basic check)

### Production Considerations

For production deployments:
1. Add user authentication
2. Implement request throttling
3. Set up monitoring and logging
4. Use HTTPS
5. Configure CORS appropriately

## 📊 Monitoring

### Streamlit Metrics

Enable metrics in config:

```toml
[server]
enableCORS = true
enableXsrfProtection = true

[browser]
gatherUsageStats = true
```

### Custom Analytics

Add analytics tracking:

```python
import streamlit as st

# Google Analytics
st.markdown("""
    <!-- Google Analytics code -->
""", unsafe_allow_html=True)
```

## 🤝 Contributing

See main project [CONTRIBUTING.md](../docs/CONTRIBUTING.md) for guidelines.

### Web App Specific Guidelines

- Follow Streamlit best practices
- Keep UI responsive and fast
- Add loading spinners for long operations
- Provide clear error messages
- Test on different screen sizes

## 📝 License

Same as main project (MIT License).

## 📞 Support

- **Issues**: Open issue on GitHub
- **Documentation**: Check main project docs
- **Community**: GitHub Discussions

---

**Happy Breadboarding! 🎉**

Last Updated: January 2026
