/**
 * Arecanut Disease Predictor - Client-side interactions
 */

document.addEventListener('DOMContentLoaded', function () {
  const dropzone = document.getElementById('upload-dropzone');
  const fileInput = document.getElementById('image-upload-input');
  const previewContainer = document.getElementById('preview-container');
  const previewImage = document.getElementById('preview-image');
  const previewInfo = document.getElementById('preview-info');
  const uploadForm = document.getElementById('disease-upload-form');
  const submitBtn = document.getElementById('submit-btn');

  if (!dropzone || !fileInput) return;

  // Highlight dropzone on dragover
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    }, false);
  });

  // Handle dropped files
  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      fileInput.files = files;
      handleFileSelected(files[0]);
    }
  });

  // Handle regular file selection
  fileInput.addEventListener('change', function () {
    if (this.files.length > 0) {
      handleFileSelected(this.files[0]);
    }
  });

  function handleFileSelected(file) {
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    const maxSizeBytes = 10 * 1024 * 1024; // 10 MB

    if (!allowedTypes.includes(file.type.toLowerCase()) && 
        !file.name.match(/\.(jpg|jpeg|png)$/i)) {
      alert('Unsupported file type. Please select a valid JPG, JPEG, or PNG image.');
      fileInput.value = '';
      if (previewContainer) previewContainer.style.display = 'none';
      return;
    }

    if (file.size > maxSizeBytes) {
      alert(`File is too large (${(file.size / (1024 * 1024)).toFixed(2)} MB). Maximum allowed size is 10 MB.`);
      fileInput.value = '';
      if (previewContainer) previewContainer.style.display = 'none';
      return;
    }

    // Display image preview
    const reader = new FileReader();
    reader.onload = function (e) {
      if (previewImage && previewContainer) {
        previewImage.src = e.target.result;
        previewContainer.style.display = 'block';
        if (previewInfo) {
          const sizeKb = (file.size / 1024).toFixed(1);
          previewInfo.textContent = `${file.name} (${sizeKb} KB)`;
        }
      }
    };
    reader.readAsDataURL(file);
  }

  // Handle Form Submission State
  if (uploadForm && submitBtn) {
    uploadForm.addEventListener('submit', function (e) {
      if (!fileInput.files || fileInput.files.length === 0) {
        e.preventDefault();
        alert('Please choose an arecanut image before submitting.');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <svg class="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="animation: spin 1s linear infinite; display: inline-block; vertical-align: middle; margin-right: 8px;">
          <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
          <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"></path>
        </svg>
        Analyzing Image with ResNet-50...
      `;
    });
  }
});

// Inject keyframe animation for loading spinner
const styleSheet = document.createElement('style');
styleSheet.innerHTML = `@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`;
document.head.appendChild(styleSheet);
