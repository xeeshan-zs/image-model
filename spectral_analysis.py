"""
Spectral Fingerprint Analysis Module
Implements DFT-based artifact detection for AI-generated images.
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PIL import Image

def compute_spectral_fingerprint_web(image_path):
    """
    Compute spectral fingerprint and return the matplotlib Figure object.
    Optimized for web usage (headless).
    
    Args:
        image_path (str): Path to image
        
    Returns:
        matplotlib.figure.Figure: The figure object
    """
    # Load and convert image to grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Perform 2D Discrete Fourier Transform
    f_transform = np.fft.fft2(img)
    f_transform_shifted = np.fft.fftshift(f_transform)
    magnitude_spectrum = np.abs(f_transform_shifted)
    magnitude_spectrum_log = np.log1p(magnitude_spectrum)
    
    # Create figure with dark theme
    fig = Figure(figsize=(6, 6), facecolor='#1a1a1a')
    ax = fig.add_subplot(111)
    
    # Plot
    im = ax.imshow(magnitude_spectrum_log, cmap='magma', interpolation='nearest')
    ax.set_title('Frequency Domain Analysis', color='white', fontsize=14, pad=15)
    ax.axis('off')
    
    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Magnitude (log scale)', color='#aaaaaa', fontsize=10)
    cbar.ax.tick_params(colors='#aaaaaa', labelsize=8)
    cbar.outline.set_visible(False)
    
    fig.tight_layout()
    return fig

def compute_spectral_fingerprint(image_path):
    """Legacy function for GUI compatibility"""
    return compute_spectral_fingerprint_web(image_path)


def analyze_spectrum_patterns(image_path):
    """
    Analyze spectral patterns to detect AI artifacts.
    
    Returns a textual description of findings.
    """
    # Load and convert image to grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        return "Could not analyze image"
    
    # Perform DFT
    f_transform = np.fft.fft2(img)
    f_transform_shifted = np.fft.fftshift(f_transform)
    magnitude_spectrum = np.abs(f_transform_shifted)
    
    # Analyze central region (exclude DC component)
    center_y, center_x = magnitude_spectrum.shape[0] // 2, magnitude_spectrum.shape[1] // 2
    radius = min(center_y, center_x) // 4
    
    # Create mask excluding center
    y, x = np.ogrid[:magnitude_spectrum.shape[0], :magnitude_spectrum.shape[1]]
    mask = ((y - center_y)**2 + (x - center_x)**2) > (radius**2)
    
    # Get statistics
    spectrum_std = np.std(magnitude_spectrum[mask])
    spectrum_max = np.max(magnitude_spectrum[mask])
    spectrum_mean = np.mean(magnitude_spectrum[mask])
    
    # Detect high-frequency anomalies
    anomaly_threshold = spectrum_mean + 3 * spectrum_std
    anomalies = np.sum(magnitude_spectrum[mask] > anomaly_threshold)
    
    analysis = []
    
    if anomalies > 100:
        analysis.append("⚠ High number of spectral anomalies detected.")
        analysis.append("This is a common characteristic of GAN/Diffusion generation.")
    else:
        analysis.append("✓ Spectral pattern appears natural.")
        analysis.append("No significant high-frequency artifacts found.")
    
    return "\n".join(analysis)
