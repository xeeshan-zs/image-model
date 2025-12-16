"""
AI Image Detector GUI
Simple interface for AI image detection.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
import os

from detection_engine import AIImageDetector




class AIDetectorApp(tk.Tk):
    """Main GUI application for AI image detection."""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("AI Image Detector")
        self.geometry("800x600")
        self.configure(bg='#f0f0f0')
        
        # Initialize detector (will be loaded in background)
        self.detector = None
        self.current_image_path = None
        self.is_processing = False
        
        # Create UI
        self._create_layout()
        
        # Load model in background
        self._load_model_async()
    
    def _create_layout(self):
        """Create the main UI layout."""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = tk.Label(
            self,
            text="AI Image Detector",
            font=("Arial", 20, "bold"),
            bg='#f0f0f0',
            fg='#333'
        )
        header.grid(row=0, column=0, columnspan=2, pady=15, padx=20, sticky="w")
        
        subtitle = tk.Label(
            self,
            text="Check if your image is AI-generated or real",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#666'
        )
        subtitle.grid(row=0, column=0, columnspan=2, pady=(45, 5), padx=20, sticky="w")
        
        # Left Panel - Image Upload
        self._create_left_panel()
        
        # Right Panel - Results
        self._create_right_panel()
    
    def _create_left_panel(self):
        """Create the left panel for image upload."""
        
        left_frame = tk.Frame(self, bg='#fafafa', relief=tk.SOLID, bd=1)
        left_frame.grid(row=1, column=0, padx=(20, 10), pady=(10, 20), sticky="nsew")
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = tk.Label(
            left_frame,
            text="Upload Image",
            font=("Arial", 14, "bold"),
            bg='#fafafa',
            fg='#333'
        )
        title.grid(row=0, column=0, pady=10, padx=15, sticky="w")
        
        # Image display area
        self.image_frame = tk.Frame(left_frame, bg='white', relief=tk.SOLID, bd=1)
        self.image_frame.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="nsew")
        
        self.image_label = tk.Label(
            self.image_frame,
            text="No image uploaded\n\nClick Upload button",
            font=("Arial", 11),
            bg='white',
            fg='#666'
        )
        self.image_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Upload button
        self.upload_btn = tk.Button(
            left_frame,
            text="Choose File",
            command=self._upload_image,
            bg='#0066cc',
            fg='white',
            font=("Arial", 11),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=8
        )
        self.upload_btn.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")
        
        # Status label
        self.status_label = tk.Label(
            left_frame,
            text="Ready",
            font=("Arial", 10),
            bg='#fafafa',
            fg='#666'
        )
        self.status_label.grid(row=3, column=0, padx=15, pady=(0, 10))
    
    def _create_right_panel(self):
        """Create the right panel for results display."""
        
        right_frame = tk.Frame(self, bg='#fafafa', relief=tk.SOLID, bd=1)
        right_frame.grid(row=1, column=1, padx=(10, 20), pady=(10, 20), sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Detection Result Section
        result_title = tk.Label(
            right_frame,
            text="Detection Result",
            font=("Arial", 14, "bold"),
            bg='#fafafa',
            fg='#333'
        )
        result_title.grid(row=0, column=0, pady=10, padx=15, sticky="w")
        
        self.result_frame = tk.Frame(right_frame, bg='white', relief=tk.SOLID, bd=1)
        self.result_frame.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="nsew")
        
        self.result_icon = tk.Label(
            self.result_frame,
            text="❓",
            font=("Arial", 50),
            bg='white'
        )
        self.result_icon.pack(pady=(30, 10))
        
        self.result_label = tk.Label(
            self.result_frame,
            text="Waiting for image...",
            font=("Arial", 18, "bold"),
            bg='white',
            fg='#333'
        )
        self.result_label.pack(pady=5)
        
        self.confidence_label = tk.Label(
            self.result_frame,
            text="--% confidence",
            font=("Arial", 12),
            bg='white',
            fg='#666'
        )
        self.confidence_label.pack(pady=(0, 30))
    
    def _load_model_async(self):
        """Load the AI detection model in a background thread."""
        
        def load():
            try:
                self.status_label.configure(text="Loading model...")
                self.detector = AIImageDetector()
                self.status_label.configure(text="Ready", fg="#009900")
            except Exception as e:
                self.status_label.configure(
                    text=f"Error: {str(e)[:30]}...",
                    fg="#cc0000"
                )
        
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
    
    def _upload_image(self):
        """Handle image upload via file dialog."""
        
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self._process_image(file_path)
    
    def _process_image(self, image_path):
        """Process the selected image."""
        
        if self.is_processing:
            return
        
        if self.detector is None:
            self.status_label.configure(
                text="Please wait for model to load...",
                fg="#ff8800"
            )
            return
        
        self.current_image_path = image_path
        self.is_processing = True
        
        # Display the uploaded image
        self._display_image(image_path)
        
        # Reset results
        self.result_icon.configure(text="⏳")
        self.result_label.configure(text="Analyzing...", fg="#666")
        self.confidence_label.configure(text="Please wait...")
        self.status_label.configure(text="Analyzing...")
        
        # Run analysis in background thread
        thread = threading.Thread(
            target=self._analyze_image,
            args=(image_path,),
            daemon=True
        )
        thread.start()
    
    def _display_image(self, image_path):
        """Display the uploaded image."""
        
        try:
            # Load and resize image
            img = Image.open(image_path)
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Update label
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"Error displaying image: {e}")
    
    def _analyze_image(self, image_path):
        """Run AI detection (background thread)."""
        
        try:
            # Run AI detection
            detection_data = self.detector.detect(image_path)
            confidence = detection_data['confidence']
            
            # Determine result
            if 'artificial' in detection_data['label'].lower():
                result_text = "AI Generated"
                icon_text = "🤖"
                color = "#cc0000"  # Red for AI
            else:
                result_text = "Real Image"
                icon_text = "📸"
                color = "#009900"  # Green for Real
            
            # Update result on main thread
            self.after(0, self._update_result, result_text, icon_text, color, confidence)
            
            # Update status
            self.after(0, lambda: self.status_label.configure(
                text="Done!",
                fg="#009900"
            ))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.after(0, lambda: self.result_label.configure(
                text=error_msg,
                fg="#cc0000"
            ))
            self.after(0, lambda: self.status_label.configure(
                text="Analysis failed",
                fg="#cc0000"
            ))
        
        finally:
            self.is_processing = False
    
    def _update_result(self, result_text, icon_text, color, confidence):
        """Update the detection result display (must run on main thread)."""
        self.result_icon.configure(text=icon_text)
        self.result_label.configure(text=result_text, fg=color)
        self.confidence_label.configure(text=f"{confidence:.1f}% confidence")


def main():
    """Run the application."""
    app = AIDetectorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
