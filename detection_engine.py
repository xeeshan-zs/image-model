"""
AI Image Detection Engine
Uses Hugging Face transformers for high-accuracy AI image detection.
"""

from transformers import pipeline
from PIL import Image
import torch


class AIImageDetector:
    """
    Wrapper for Hugging Face AI image detection model.
    """
    
    def __init__(self, model_name="umm-maybe/AI-image-detector"):
        """
        Initialize the AI image detector.
        
        Args:
            model_name (str): Hugging Face model identifier
        """
        self.model_name = model_name
        self.classifier = None
        self._load_model()
    
    def _load_model(self):
        """Load the transformer model and create the pipeline."""
        try:
            print(f"Loading model: {self.model_name}...")
            
            # Determine device
            device = 0 if torch.cuda.is_available() else -1
            
            # Create image classification pipeline
            self.classifier = pipeline(
                "image-classification",
                model=self.model_name,
                device=device
            )
            
            print("Model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Attempting alternative models...")
            
            # Try multiple fallback models in order of preference
            fallback_models = [
                "Organika/sdxl-detector",
                "saltacc/anime-ai-detect",
                "google/vit-base-patch16-224"
            ]
            
            for fallback_model in fallback_models:
                try:
                    print(f"Trying fallback: {fallback_model}...")
                    self.model_name = fallback_model
                    device = 0 if torch.cuda.is_available() else -1
                    self.classifier = pipeline(
                        "image-classification",
                        model=self.model_name,
                        device=device
                    )
                    print(f"Loaded fallback model: {self.model_name}")
                    return
                except Exception as fallback_error:
                    print(f"Fallback {fallback_model} failed: {fallback_error}")
                    continue
            
            # If all models fail, raise error
            raise RuntimeError("Failed to load any detection model")

    
    def detect(self, image_path):
        """
        Detect if an image is AI-generated or real.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Detection results with format:
                {
                    'label': 'artificial' or 'real',
                    'confidence': float (0-100),
                    'all_scores': list of all predictions
                }
        """
        if self.classifier is None:
            raise RuntimeError("Model not loaded")
        
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Run inference
        results = self.classifier(image)
        
        # Parse results - handle different model output formats
        top_result = results[0]
        label_text = top_result['label'].lower()
        
        # Comprehensive label mapping
        ai_keywords = ['artificial', 'fake', 'ai', 'generated', 'synthetic', 'diffusion', 'gan', 'stable']
        real_keywords = ['real', 'natural', 'photo', 'authentic', 'human']
        
        # Check if label indicates AI-generated
        is_ai = any(keyword in label_text for keyword in ai_keywords)
        is_real = any(keyword in label_text for keyword in real_keywords)
        
        # If unclear, check all results for better confidence
        if not is_ai and not is_real and len(results) > 1:
            # Look at second prediction
            for result in results:
                r_label = result['label'].lower()
                if any(keyword in r_label for keyword in ai_keywords):
                    top_result = result
                    is_ai = True
                    break
        
        # Final label determination
        if is_ai:
            label = 'artificial'
        elif is_real:
            label = 'real'
        else:
            # If still unclear, use label as-is but mark as uncertain
            label = 'real' if 'not' not in label_text else 'artificial'
        
        # Convert score to percentage
        confidence = top_result['score'] * 100
        
        return {
            'label': label,
            'confidence': confidence,
            'all_scores': results,
            'model_used': self.model_name
        }
    
    def get_formatted_result(self, image_path):
        """
        Get a user-friendly formatted detection result.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Formatted result string (e.g., "98% Artificial")
        """
        result = self.detect(image_path)
        label = result['label'].capitalize()
        confidence = result['confidence']
        
        return f"{confidence:.1f}% {label}"
