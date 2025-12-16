document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const clearBtn = document.getElementById('clear-btn');
    const statusText = document.getElementById('status-text');

    // Result elements
    const verdictText = document.getElementById('verdict-text');
    const verdictIcon = document.getElementById('verdict-icon');
    const confidenceBadge = document.getElementById('confidence-badge');

    // Drag & Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.style.borderColor = '#0066cc';
            dropZone.style.backgroundColor = '#f0f8ff';
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.style.borderColor = '#999';
            dropZone.style.backgroundColor = 'white';
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        handleFiles(files);
    }, false);

    // File Input
    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    // Clear Button
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
        dropZone.style.display = 'block';
        previewContainer.style.display = 'none';
        imagePreview.src = '';
        fileInput.value = '';

        statusText.textContent = "Ready";
        verdictText.textContent = "Waiting for image...";
        verdictIcon.textContent = "❓";
        confidenceBadge.textContent = "--%";
    }

    async function uploadAndAnalyze(file) {
        statusText.textContent = "Analyzing...";
        verdictText.textContent = "Please wait...";
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
                const isAI = data.is_ai;
                const confidence = data.confidence.toFixed(1);

                if (isAI) {
                    verdictText.textContent = "AI Generated";
                    verdictText.style.color = "#cc0000";
                    verdictIcon.textContent = "🤖";
                } else {
                    verdictText.textContent = "Real Image";
                    verdictText.style.color = "#009900";
                    verdictIcon.textContent = "📸";
                }

                confidenceBadge.textContent = confidence + "% confidence";
                statusText.textContent = "Done!";

            } else {
                throw new Error(data.error || "Analysis failed");
            }

        } catch (error) {
            console.error('Error:', error);
            statusText.textContent = "Error occurred";
            verdictText.textContent = "Error";
            verdictIcon.textContent = "⚠️";
        }
    }
});
