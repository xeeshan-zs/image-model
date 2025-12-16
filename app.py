import os
import io
import base64
import numpy as np
import cv2
from flask import Flask, render_template, request, jsonify
from PIL import Image
from detection_engine import AIImageDetector
from spectral_analysis import compute_spectral_fingerprint_web, analyze_spectrum_patterns

# Initialize Flask App
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['UPLOAD_FOLDER'] = 'temp_uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global model instance
detector = None

def get_detector():
    """Lazy loading of the detector."""
    global detector
    if detector is None:
        try:
            print("Loading AI Model...")
            detector = AIImageDetector()
            print("AI Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    return detector

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        # Save temp file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # 1. AI Detection
        model = get_detector()
        if model:
            detection_result = model.get_formatted_result(file_path)
            raw_result = model.detect(file_path)
        else:
            detection_result = "Model unavailable"
            raw_result = {'label': 'unknown', 'confidence': 0}

        # 2. Spectral Analysis
        spectrum_fig = compute_spectral_fingerprint_web(file_path)
        
        # Convert figure to base64
        buf = io.BytesIO()
        spectrum_fig.savefig(buf, format='png', bbox_inches='tight', facecolor='#2b2b2b')
        buf.seek(0)
        spectrum_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close(spectrum_fig)
        
        # 3. Pattern Analysis
        analysis_text = analyze_spectrum_patterns(file_path)
        
        # Clean up
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'detection': detection_result,
            'is_ai': 'artificial' in raw_result['label'].lower(),
            'confidence': raw_result['confidence'],
            'spectrum_image': f"data:image/png;base64,{spectrum_b64}",
            'analysis': analysis_text
        })
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    # Pre-load model on start (optional, can be lazy loaded too)
    get_detector()
    app.run(debug=True, port=5000)
