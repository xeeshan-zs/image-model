document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const clearBtn = document.getElementById('clear-btn');
    const loader = document.getElementById('loader');
    const statusText = document.getElementById('status-text');

    // Result elements
    const verdictText = document.getElementById('verdict-text');
    const verdictIcon = document.getElementById('verdict-icon');
    const confidenceBadge = document.getElementById('confidence-badge');
    const spectrumImg = document.getElementById('spectrum-img');
    const analysisText = document.getElementById('analysis-text');

    // Drag & Drop Handlers
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    // File Input Handler
    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    // Clear Button Handler
    clearBtn.addEventListener('click', () => {
        resetUI();
    });

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                displayPreview(file);
                uploadAndAnalyze(file);
            } else {
                alert('Please upload an image file.');
            }
        }
    }

    function displayPreview(file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreview.src = e.target.result;
            dropZone.style.display = 'none';
            previewContainer.style.display = 'block';
        }
        reader.readAsDataURL(file);
    }

    function resetUI() {
        dropZone.style.display = 'flex';
        previewContainer.style.display = 'none';
        imagePreview.src = '';
        fileInput.value = '';

        statusText.textContent = "Ready to analyze";
        statusText.style.color = "#a0a0a0";
        loader.style.display = 'none';

        verdictText.textContent = "Waiting for image...";
        verdictText.style.color = "#a0a0a0";
        verdictIcon.textContent = "❓";
        confidenceBadge.textContent = "--%";

        spectrumImg.src = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMmIyYjJiIi8+PC9zdmc+";
        analysisText.textContent = "Upload an image to see spectral analysis.";
    }

    async function uploadAndAnalyze(file) {
        // Update UI to loading state
        statusText.textContent = "Analyzing image...";
        statusText.style.color = "#3b82f6";
        loader.style.display = 'inline-block';
        verdictText.textContent = "Analyzing...";
        verdictText.style.color = "#eab308"; // yellow
        verdictIcon.textContent = "⏳";

        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // Formatting Verdict
                const isAI = data.is_ai;
                const confidence = data.confidence.toFixed(1);

                if (isAI) {
                    verdictText.textContent = "AI Generated";
                    verdictText.style.color = "#ef4444"; // red
                    verdictIcon.textContent = "🤖";
                } else {
                    verdictText.textContent = "Real Image";
                    verdictText.style.color = "#22c55e"; // green
                    verdictIcon.textContent = "📸";
                }

                confidenceBadge.textContent = `${confidence}% Confidence`;

                // Update Spectrum
                if (data.spectrum_image) {
                    spectrumImg.src = data.spectrum_image;
                }

                // Update Analysis Text
                if (data.analysis) {
                    analysisText.textContent = data.analysis;
                }

                statusText.textContent = "Analysis Complete";
                statusText.style.color = "#22c55e";

            } else {
                throw new Error(data.error || "Analysis failed");
            }

        } catch (error) {
            console.error('Error:', error);
            statusText.textContent = "Error: " + error.message;
            statusText.style.color = "#ef4444";
            verdictText.textContent = "Error";
            verdictIcon.textContent = "⚠️";
        } finally {
            loader.style.display = 'none';
        }
    }
});
