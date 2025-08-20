import streamlit as st
import subprocess
import os
import shutil
from pathlib import Path
import uuid

# Set page config for better appearance
st.set_page_config(page_title="Image to Video Converter", page_icon="🎥", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 8px; }
    .stButton>button:hover { background-color: #45a049; }
    .stFileUploader { background-color: white; padding: 10px; border-radius: 8px; }
    .stSelectbox { margin-bottom: 20px; }
    .success-message { color: #2e7d32; font-weight: bold; }
    .error-message { color: #d32f2f; font-weight: bold; }
    .preview-container { border: 1px solid #ddd; padding: 10px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

def check_ffmpeg():
    """Check if FFmpeg is installed and available in PATH."""
    return shutil.which("ffmpeg") is not None

def convert_image_to_video(image_path, audio_path, output_path, bitrate="192k"):
    """Run FFmpeg command to combine image and audio into video."""
    try:
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", image_path,
            "-i", audio_path, "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", bitrate, "-pix_fmt", "yuv420p",
            "-shortest", output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True, "Video created successfully!"
    except subprocess.CalledProcessError as e:
        return False, f"FFmpeg Error: {e.stderr}"
    except FileNotFoundError:
        return False, "FFmpeg not found. Please ensure FFmpeg is installed and added to your system PATH."

# Create a temporary directory for file handling
if not os.path.exists("temp"):
    os.makedirs("temp")

# Streamlit UI
st.title("🎥 Image to Video Converter")
st.markdown("Combine an image (PNG/JPG) and audio (MP3) file to create a video using FFmpeg.")

# Help section for FFmpeg installation
with st.expander("ℹ️ How to Install FFmpeg", expanded=False):
    st.markdown("""
    **FFmpeg is required to run this application.**  
    If you encounter an error, follow these steps to install FFmpeg on Windows:
    1. Download FFmpeg from [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/) (choose a release like `ffmpeg-release-essentials.zip`).
    2. Extract the zip file to a folder (e.g., `C:\\ffmpeg`).
    3. Add the FFmpeg `bin` folder to your system PATH:
       - Right-click 'This PC' > Properties > Advanced system settings > Environment Variables.
       - Under 'System variables' or 'User variables,' find `Path`, edit, and add the path to the `bin` folder (e.g., `C:\\ffmpeg\\bin`).
    4. Verify installation by opening a Command Prompt and running `ffmpeg -version`.
    If installed correctly, you'll see FFmpeg version information.
    """)

# Check FFmpeg availability
if not check_ffmpeg():
    st.markdown('<p class="error-message">FFmpeg is not installed or not found in your system PATH. Please install FFmpeg following the instructions above.</p>', unsafe_allow_html=True)

# File uploaders
col1, col2 = st.columns(2)
with col1:
    image_file = st.file_uploader("Upload Image (PNG/JPG)", type=["png", "jpg", "jpeg"], key="image")
    if image_file:
        st.markdown("**Image Preview**")
        st.image(image_file, use_container_width=True, caption="Uploaded Image", output_format="auto")
with col2:
    audio_file = st.file_uploader("Upload Audio (MP3)", type=["mp3", "mpeg"], key="audio")
    if audio_file:
        st.markdown("**Audio Preview**")
        st.audio(audio_file, format="audio/mpeg")

# Audio bitrate selection
bitrate = st.selectbox("Select Audio Bitrate", ["128k", "192k", "256k", "320k"], index=1)

# Generate button
if st.button("Generate Video", key="generate"):
    if image_file is None or audio_file is None:
        st.markdown('<p class="error-message">Please upload both an image (PNG/JPG) and an audio (MP3) file.</p>', unsafe_allow_html=True)
    elif not check_ffmpeg():
        st.markdown('<p class="error-message">Cannot proceed: FFmpeg is not installed. Please follow the installation instructions above.</p>', unsafe_allow_html=True)
    else:
        # Validate file extensions
        image_ext = os.path.splitext(image_file.name)[1].lower()
        audio_ext = os.path.splitext(audio_file.name)[1].lower()
        if image_ext not in [".png", ".jpg", ".jpeg"]:
            st.markdown('<p class="error-message">Invalid image file. Please upload a PNG or JPG file.</p>', unsafe_allow_html=True)
        elif audio_ext not in [".mp3", ".mpeg"]:
            st.markdown('<p class="error-message">Invalid audio file. Please upload an MP3 file.</p>', unsafe_allow_html=True)
        else:
            progress_bar = st.progress(0)
            with st.spinner("Processing..."):
                # Save uploaded files temporarily
                unique_id = str(uuid.uuid4())
                temp_image_path = f"temp/{unique_id}_{image_file.name}"
                temp_audio_path = f"temp/{unique_id}_{audio_file.name}"
                output_path = f"temp/output_{unique_id}.mp4"

                with open(temp_image_path, "wb") as f:
                    f.write(image_file.getbuffer())
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_file.getbuffer())

                # Update progress
                progress_bar.progress(50)

                # Run FFmpeg conversion
                success, message = convert_image_to_video(temp_image_path, temp_audio_path, output_path, bitrate)

                # Complete progress
                progress_bar.progress(100)

                if success:
                    st.markdown('<p class="success-message">Video created successfully!</p>', unsafe_allow_html=True)
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="Download Video",
                            data=f,
                            file_name="output.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.markdown(f'<p class="error-message">{message}</p>', unsafe_allow_html=True)

                # Clean up temporary files
                for path in [temp_image_path, temp_audio_path, output_path]:
                    if os.path.exists(path):
                        os.remove(path)

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and FFmpeg | © 2025")