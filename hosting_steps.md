# Hosting Steps for AI Image Detector Web App

This guide covers multiple hosting options for deploying your Flask-based AI Image Detector.

## Important Considerations

> [!WARNING]
> **Model Size**: The AI detection model is ~350MB. Many free hosting tiers have storage/memory limits that may not support this size.

> [!NOTE]
> **Best Options**: For this application, consider platforms with generous free tiers or GPU support:
> - **Hugging Face Spaces** (RECOMMENDED - Free GPU, designed for ML apps)
> - **Railway** (Free tier with good limits)
> - **Render** (Free tier available)

---

## Option 1: Hugging Face Spaces (RECOMMENDED)

**Pros**: Free GPU, designed for ML/AI apps, handles large models well  
**Cons**: Requires HF account

### Steps:

1. **Create Account**
   - Sign up at [huggingface.co](https://huggingface.co)

2. **Create New Space**
   - Go to Spaces → Create New Space
   - Choose **Gradio** framework (or Custom)
   - Select **Public** or **Private**

3. **Prepare Your App for Gradio** (Alternative to Flask)
   
   Create `app_gradio.py`:
   ```python
   import gradio as gr
   from detection_engine import AIImageDetector
   from spectral_analysis import compute_spectral_fingerprint_web, analyze_spectrum_patterns
   import matplotlib.pyplot as plt
   
   # Load model
   detector = AIImageDetector()
   
   def analyze_image(image):
       # Save temp file
       temp_path = "temp_image.jpg"
       image.save(temp_path)
       
       # Get detection
       result = detector.get_formatted_result(temp_path)
       
       # Get spectrum
       fig = compute_spectral_fingerprint_web(temp_path)
       analysis = analyze_spectrum_patterns(temp_path)
       
       return result, fig, analysis
   
   # Create Gradio interface
   demo = gr.Interface(
       fn=analyze_image,
       inputs=gr.Image(type="pil"),
       outputs=[
           gr.Textbox(label="Detection Result"),
           gr.Plot(label="Spectral Fingerprint"),
           gr.Textbox(label="Analysis")
       ],
       title="🔍 AI Image Detector",
       description="Upload an image to detect if it's AI-generated or real"
   )
   
   demo.launch()
   ```

4. **Push to Space**
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
   cd YOUR_SPACE_NAME
   
   # Copy your files
   cp detection_engine.py YOUR_SPACE_NAME/
   cp spectral_analysis.py YOUR_SPACE_NAME/
   cp app_gradio.py YOUR_SPACE_NAME/app.py
   cp requirements.txt YOUR_SPACE_NAME/
   
   # Commit and push
   git add .
   git commit -m "Initial commit"
   git push
   ```

---

## Option 2: Railway

**Pros**: Easy deployment, generous free tier  
**Cons**: May sleep after inactivity

### Steps:

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

3. **Create `Procfile`** (in your project root)
   ```
   web: gunicorn app:app
   ```

4. **Update `requirements.txt`**
   Add:
   ```
   gunicorn>=21.0.0
   ```

5. **Deploy**
   ```bash
   railway init
   railway up
   ```

6. **Set Environment Variables** (Optional)
   ```bash
   railway variables set FLASK_ENV=production
   ```

---

## Option 3: Render

**Pros**: Free tier, automatic deploys from GitHub  
**Cons**: Limited free tier resources

### Steps:

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Create `render.yaml`**
   ```yaml
   services:
     - type: web
       name: ai-image-detector
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: gunicorn app:app
       envVars:
         - key: PYTHON_VERSION
           value: 3.10.0
   ```

3. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - New → Web Service
   - Connect your GitHub repo
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`

---

## Option 4: Google Cloud Run

**Pros**: Scalable, pay-as-you-go  
**Cons**: Requires billing account

### Steps:

1. **Create `Dockerfile`**
   ```dockerfile
   FROM python:3.10-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8080
   
   CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 app:app
   ```

2. **Deploy**
   ```bash
   gcloud run deploy ai-detector \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

---

## Option 5: AWS EC2 (Manual Setup)

**Pros**: Full control  
**Cons**: More complex, paid

### Steps:

1. **Launch EC2 Instance**
   - Ubuntu Server 22.04
   - t2.medium or larger (for model size)

2. **SSH into Instance**
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-ip
   ```

3. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx -y
   ```

4. **Clone and Setup**
   ```bash
   git clone YOUR_REPO_URL
   cd image-model
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

5. **Run with Gunicorn**
   ```bash
   gunicorn --bind 0.0.0.0:5000 app:app
   ```

6. **Configure Nginx** (optional, for production)
   Create `/etc/nginx/sites-available/ai-detector`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## Common Configuration Files

### `.gitignore`
```
.venv/
__pycache__/
*.pyc
temp_uploads/
.env
```

### `runtime.txt` (for some platforms)
```
python-3.10.0
```

---

## Performance Tips

1. **Use Gunicorn** instead of Flask's built-in server
   ```bash
   pip install gunicorn
   gunicorn --workers 2 --timeout 120 app:app
   ```

2. **Optimize Model Loading**
   - Cache model on first request
   - Consider using smaller models for faster loading

3. **Set Upload Limits** (already configured in `app.py`)
   ```python
   app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
   ```

---

## Troubleshooting

### "Out of Memory" Error
- Upgrade to a larger instance
- Reduce worker count in Gunicorn
- Use model quantization

### "Module Not Found" Error
- Ensure `requirements.txt` is complete
- Check platform-specific build logs

### Slow Model Loading
- This is normal on first request (~1-2 minutes)
- Consider pre-warming on deployment with a startup script

---

## Cost Estimates

| Platform | Free Tier | Paid Plans Start At |
|----------|-----------|---------------------|
| Hugging Face Spaces | ✅ Free GPU | N/A (community focused) |
| Railway | 500 hrs/month | $5/month |
| Render | 750 hrs/month | $7/month |
| Google Cloud Run | Limited free | Pay per use |
| AWS EC2 | 12 months free tier | ~$10-30/month |

---

## Recommended Approach

For quick deployment and testing:
1. **Start with Hugging Face Spaces** - Best for ML apps
2. If you prefer Flask, try **Railway** - Easy and generous free tier
3. For production with custom domain, use **AWS EC2** or **Google Cloud Run**
