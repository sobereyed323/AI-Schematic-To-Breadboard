"""
CircuitNet to Breadboard Web Application

A Streamlit-based web interface for converting electronic schematics
into breadboard layouts with step-by-step instructions.
"""

import streamlit as st
import os
import sys
from pathlib import Path
from PIL import Image
import tempfile
import base64

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from integration.circuit_to_breadboard import CircuitNetBridge
    from ai_enhancement.gpt_vision import SchematicAnalyzer
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Make sure all dependencies are installed: pip install -r requirements-enhanced.txt")
    st.stop()


# Page configuration
st.set_page_config(
    page_title="CircuitNet to Breadboard",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #4A90E2;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)


def get_binary_file_downloader_html(file_path, file_label, button_text):
    """Generate a download link for a file."""
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    
    # Determine file extension
    ext = Path(file_path).suffix
    mime_types = {
        '.png': 'image/png',
        '.html': 'text/html',
        '.md': 'text/markdown',
        '.pdf': 'application/pdf'
    }
    mime = mime_types.get(ext, 'application/octet-stream')
    
    return f'<a href="data:{mime};base64,{b64}" download="{file_label}" class="download-button">{button_text}</a>'


def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">🔌 CircuitNet to Breadboard</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Convert electronic schematics into breadboard layouts with AI-powered guidance</p>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key input
        use_gpt = st.checkbox("Enable GPT-4 Vision Enhancement", value=False)
        
        api_key = None
        if use_gpt:
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key for GPT-4 Vision enhancement"
            )
            if not api_key:
                st.warning("API key required for GPT-4 Vision")
        
        st.markdown("---")
        
        # Output settings
        st.subheader("Output Settings")
        output_dpi = st.slider("Image DPI", 150, 600, 300, 50)
        show_labels = st.checkbox("Show Component Labels", value=True)
        difficulty = st.selectbox(
            "Instruction Difficulty",
            ["beginner", "intermediate", "advanced"],
            index=0
        )
        
        st.markdown("---")
        
        # Help
        with st.expander("ℹ️ How to Use"):
            st.markdown("""
                1. **Upload** a schematic image (PNG, JPEG, or SVG)
                2. **Preview** the uploaded schematic
                3. **Convert** to breadboard layout
                4. **Download** results (images and instructions)
                
                **Tips:**
                - Use clear, high-contrast images
                - Ensure component labels are visible
                - Standard electronic symbols work best
            """)
        
        with st.expander("📚 Examples"):
            st.markdown("""
                Check out our example schematics:
                - Simple LED Circuit
                - 555 Timer Circuit
                - Voltage Divider
                - Transistor Switch
                
                Find them in `examples/schematics/`
            """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Schematic")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a schematic image",
            type=['png', 'jpg', 'jpeg', 'svg'],
            help="Upload a clear image of your electronic schematic"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            st.subheader("Uploaded Schematic")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
            
            # Image info
            st.info(f"📐 Dimensions: {image.size[0]} x {image.size[1]} pixels")
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                image.save(tmp_file.name)
                temp_image_path = tmp_file.name
        else:
            st.markdown("""
                <div class="info-box">
                    <h4>👆 Upload a schematic to get started</h4>
                    <p>Supported formats: PNG, JPEG, SVG</p>
                    <p>For best results, use high-resolution images with clear component labels.</p>
                </div>
            """, unsafe_allow_html=True)
            temp_image_path = None
    
    with col2:
        st.header("🎯 Results")
        
        if temp_image_path:
            # Convert button
            if st.button("🚀 Convert to Breadboard", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing schematic..."):
                    try:
                        # Initialize components
                        gpt_analyzer = None
                        if use_gpt and api_key:
                            try:
                                gpt_analyzer = SchematicAnalyzer(api_key=api_key)
                            except Exception as e:
                                st.error(f"Failed to initialize GPT-4 Vision: {e}")
                        
                        bridge = CircuitNetBridge(
                            use_gpt_enhancement=use_gpt and gpt_analyzer is not None,
                            gpt_analyzer=gpt_analyzer
                        )
                        
                        # Create output directory
                        output_dir = tempfile.mkdtemp()
                        
                        # Process schematic
                        result = bridge.process_schematic(
                            temp_image_path,
                            output_dir=output_dir
                        )
                        
                        # Success message
                        st.markdown("""
                            <div class="success-box">
                                ✅ <strong>Conversion successful!</strong>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Display breadboard layout
                        st.subheader("Breadboard Layout")
                        if os.path.exists(result['breadboard_image']):
                            st.image(result['breadboard_image'], use_column_width=True)
                        
                        # Statistics
                        st.subheader("📊 Layout Statistics")
                        stats = result['statistics']
                        
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Components", stats['total_components'])
                        with col_b:
                            st.metric("Connections", stats['total_connections'])
                        with col_c:
                            st.metric("Grid Usage", f"{stats['grid_utilization']:.1%}")
                        
                        # BOM
                        st.subheader("📋 Bill of Materials")
                        bom = result['bom']
                        for item in bom.items:
                            st.write(f"- {item.quantity}x {item.component_type} ({item.value})")
                        
                        # Download buttons
                        st.subheader("💾 Download Files")
                        
                        col_dl1, col_dl2 = st.columns(2)
                        
                        with col_dl1:
                            if os.path.exists(result['breadboard_image']):
                                with open(result['breadboard_image'], 'rb') as f:
                                    st.download_button(
                                        label="📥 Download Layout (PNG)",
                                        data=f.read(),
                                        file_name="breadboard_layout.png",
                                        mime="image/png"
                                    )
                        
                        with col_dl2:
                            if os.path.exists(result['instructions_html']):
                                with open(result['instructions_html'], 'rb') as f:
                                    st.download_button(
                                        label="📥 Download Instructions (HTML)",
                                        data=f.read(),
                                        file_name="instructions.html",
                                        mime="text/html"
                                    )
                        
                        # Preview instructions
                        with st.expander("📖 Preview Instructions"):
                            if os.path.exists(result['instructions_markdown']):
                                with open(result['instructions_markdown'], 'r') as f:
                                    st.markdown(f.read())
                        
                    except Exception as e:
                        st.error(f"❌ Error during conversion: {str(e)}")
                        st.exception(e)
        else:
            st.markdown("""
                <div class="info-box">
                    <h4>📊 Results will appear here</h4>
                    <p>Upload a schematic and click "Convert to Breadboard" to see:</p>
                    <ul>
                        <li>Visual breadboard layout</li>
                        <li>Component placement</li>
                        <li>Wire routing</li>
                        <li>Step-by-step instructions</li>
                        <li>Bill of materials</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 2rem;">
            <p>CircuitNet Enhanced - AI-Powered Schematic to Breadboard Conversion</p>
            <p>Built with Streamlit • Powered by GPT-4 Vision</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
