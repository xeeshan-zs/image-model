# AI Image Detector GUI

A modern, dark-themed desktop application that combines deep learning-based AI image detection with spectral fingerprinting analysis to determine if an image is AI-generated or real.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

- **🎯 High-Accuracy AI Detection**: Uses Hugging Face transformers (umm-maybe/AI-image-detector) for state-of-the-art classification
- **🔬 Spectral Fingerprinting**: Visualizes frequency domain artifacts using DFT analysis
- **🎨 Modern Dark UI**: Built with customtkinter for a sleek, professional interface
- **⚡ Non-Blocking**: Threaded processing keeps the UI responsive
- **📁 Multi-Format Support**: Handles JPG, PNG, and WEBP images

## Requirements

- Python 3.8 or higher
- CUDA-compatible GPU (optional, for faster inference)

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:

```bash
python ai_detector_gui.py
```

### How to Use

1. **Launch the app** - Wait for the model to load (status shown in UI)
2. **Upload an image** - Click "Upload Image" or drag & drop
3. **View results**:
   - **Primary Detection**: Shows confidence percentage (e.g., "98% Artificial")
   - **Spectral Fingerprint**: Displays frequency domain analysis
   - Bright spots or grid patterns in the spectrum indicate AI generation

## How It Works

### Primary Detection
Uses a fine-tuned vision transformer model to classify images:
- **Model**: umm-maybe/AI-image-detector (with fallback to Organika/sdxl-detector)
- **Method**: Image classification pipeline from Hugging Face transformers
- **Output**: Confidence score for "Artificial" vs "Real"

### Spectral Fingerprinting
Analyzes frequency domain characteristics:
1. Convert image to grayscale
2. Apply 2D Discrete Fourier Transform (DFT)
3. Visualize magnitude spectrum
4. Look for GAN/Diffusion artifacts (unnatural patterns, grid structures)

## Project Structure

```
image model/
├── ai_detector_gui.py      # Main GUI application
├── detection_engine.py     # Hugging Face model wrapper
├── spectral_analysis.py    # DFT-based fingerprinting
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Technical Details

- **GUI Framework**: customtkinter (modern, theme-aware widgets)
- **Deep Learning**: PyTorch + Hugging Face transformers
- **Image Processing**: OpenCV, PIL, NumPy
- **Visualization**: Matplotlib embedded in Tkinter

## Troubleshooting

**Model loading fails**:
- Check your internet connection (models download on first run)
- Ensure you have enough disk space (~1-2GB for models)

**Slow inference**:
- Install CUDA-compatible PyTorch for GPU acceleration
- First run is slower due to model download and initialization

**Image won't load**:
- Ensure the file format is supported (JPG, PNG, WEBP)
- Check file permissions

## License

MIT License - Feel free to use and modify for your projects.

## Credits

- **Models**: Hugging Face community (umm-maybe, Organika)
- **Framework**: customtkinter by Tom Schimansky
- **Analysis**: DFT-based artifact detection methodology
