"""
AI Image Detector GUI
Modern dark-themed interface for AI image detection with spectral fingerprinting.
"""

import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

from detection_engine import AIImageDetector
from spectral_analysis import compute_spectral_fingerprint, analyze_spectrum_patterns


# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AIDetectorApp(ctk.CTk):
    """Main GUI application for AI image detection."""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("AI Image Detector")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
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
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            self,
            text="🔍 AI Image Detector",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        header.grid(row=0, column=0, columnspan=2, pady=20, padx=20, sticky="w")
        
        # Left Panel - Image Upload
        self._create_left_panel()
        
        # Right Panel - Results
        self._create_right_panel()
    
    def _create_left_panel(self):
        """Create the left panel for image upload."""
        
        left_frame = ctk.CTkFrame(self, corner_radius=10)
        left_frame.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            left_frame,
            text="Upload Image",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.grid(row=0, column=0, pady=15, padx=20, sticky="w")
        
        # Image display area
        self.image_frame = ctk.CTkFrame(left_frame, corner_radius=8)
        self.image_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        
        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="📁\n\nDrag & Drop\nor\nClick Upload",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        self.image_label.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Upload button
        self.upload_btn = ctk.CTkButton(
            left_frame,
            text="📤 Upload Image",
            command=self._upload_image,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8
        )
        self.upload_btn.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        # Status label
        self.status_label = ctk.CTkLabel(
            left_frame,
            text="Ready to analyze",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.grid(row=3, column=0, padx=20, pady=(0, 15))
    
    def _create_right_panel(self):
        """Create the right panel for results display."""
        
        right_frame = ctk.CTkFrame(self, corner_radius=10)
        right_frame.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Detection Result Section
        result_title = ctk.CTkLabel(
            right_frame,
            text="🎯 Primary Detection",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        result_title.grid(row=0, column=0, pady=(15, 5), padx=20, sticky="w")
        
        self.result_frame = ctk.CTkFrame(right_frame, corner_radius=8, fg_color="#1a1a1a")
        self.result_frame.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        
        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="No image analyzed yet",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="gray"
        )
        self.result_label.pack(pady=30)
        
        # Spectral Fingerprint Section
        spectrum_title = ctk.CTkLabel(
            right_frame,
            text="🔬 Spectral Fingerprint Analysis",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        spectrum_title.grid(row=2, column=0, pady=(10, 5), padx=20, sticky="nw")
        
        self.spectrum_frame = ctk.CTkFrame(right_frame, corner_radius=8, fg_color="#1a1a1a")
        self.spectrum_frame.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="nsew")
        
        self.spectrum_label = ctk.CTkLabel(
            self.spectrum_frame,
            text="Frequency domain analysis will appear here",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.spectrum_label.pack(expand=True, fill="both", pady=20)
        
        # Explanation
        explanation = ctk.CTkLabel(
            right_frame,
            text="💡 Unnatural bright spots or grid patterns in the spectrum\noften indicate AI generation (GAN/Diffusion artifacts)",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            justify="left"
        )
        explanation.grid(row=4, column=0, padx=20, pady=(0, 15), sticky="w")
    
    def _load_model_async(self):
        """Load the AI detection model in a background thread."""
        
        def load():
            try:
                self.status_label.configure(text="Loading AI model...")
                self.detector = AIImageDetector()
                self.status_label.configure(text="Model loaded - Ready to analyze")
            except Exception as e:
                self.status_label.configure(
                    text=f"Error loading model: {str(e)[:50]}...",
                    text_color="red"
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
                text_color="orange"
            )
            return
        
        self.current_image_path = image_path
        self.is_processing = True
        
        # Display the uploaded image
        self._display_image(image_path)
        
        # Reset results
        self.result_label.configure(text="Analyzing...", text_color="yellow")
        self.status_label.configure(text="Running analysis...")
        
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
        """Run AI detection and spectral analysis (background thread)."""
        
        try:
            # Run AI detection
            result = self.detector.get_formatted_result(image_path)
            detection_data = self.detector.detect(image_path)
            
            # Determine color based on result
            if 'artificial' in detection_data['label'].lower():
                color = "#ff4444"  # Red for AI
            else:
                color = "#44ff44"  # Green for Real
            
            # Update result on main thread
            self.after(0, self._update_result, result, color)
            
            # Run spectral analysis
            spectrum_fig = compute_spectral_fingerprint(image_path)
            spectrum_analysis = analyze_spectrum_patterns(image_path)
            
            # Update spectrum on main thread
            self.after(0, self._update_spectrum, spectrum_fig, spectrum_analysis)
            
            # Update status
            self.after(0, lambda: self.status_label.configure(
                text="Analysis complete",
                text_color="green"
            ))
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.after(0, lambda: self.result_label.configure(
                text=error_msg,
                text_color="red"
            ))
            self.after(0, lambda: self.status_label.configure(
                text="Analysis failed",
                text_color="red"
            ))
        
        finally:
            self.is_processing = False
    
    def _update_result(self, result_text, color):
        """Update the detection result display (must run on main thread)."""
        self.result_label.configure(text=result_text, text_color=color)
    
    def _update_spectrum(self, figure, analysis_text):
        """Update the spectrum display (must run on main thread)."""
        
        # Clear previous content
        for widget in self.spectrum_frame.winfo_children():
            widget.destroy()
        
        # Create canvas for matplotlib figure
        canvas = FigureCanvasTkAgg(figure, master=self.spectrum_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add analysis text
        analysis_label = ctk.CTkLabel(
            self.spectrum_frame,
            text=analysis_text,
            font=ctk.CTkFont(size=11),
            text_color="#aaaaaa",
            justify="left"
        )
        analysis_label.pack(pady=(0, 10), padx=10)


def main():
    """Run the application."""
    app = AIDetectorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
