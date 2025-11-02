const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const detectBtn = document.getElementById('detectBtn');
const previewSection = document.getElementById('previewSection');
const previewImage = document.getElementById('previewImage');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

let selectedFile = null;

// Upload box click
uploadBox.addEventListener('click', () => {
    fileInput.click();
});

// File input change
fileInput.addEventListener('change', (e) => {
    handleFileSelect(e.target.files[0]);
});

// Drag and drop
uploadBox.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadBox.classList.add('dragover');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('dragover');
});

uploadBox.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
    handleFileSelect(e.dataTransfer.files[0]);
});

function handleFileSelect(file) {
    if (!file || !file.type.startsWith('image/')) {
        alert('Please select a valid image file');
        return;
    }

    selectedFile = file;
    detectBtn.disabled = false;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewSection.style.display = 'block';
        resultsSection.style.display = 'none';
        errorSection.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

// Detect button click
detectBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    // Hide previous results
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    loading.style.display = 'block';
    detectBtn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        const response = await fetch('/detect', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || data.error || 'Detection failed');
        }

        // Display results
        displayResults(data);

    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to detect plant. Please try again.');
    } finally {
        loading.style.display = 'none';
        detectBtn.disabled = false;
    }
});

function displayResults(data) {
    // Set plant name and confidence
    document.getElementById('plantName').textContent = data.detected_plant || 'Unknown Plant';
    document.getElementById('confidenceBadge').textContent = `${Math.round(data.confidence * 100)}%`;

    // Set result image
    document.getElementById('resultImage').src = data.image;

    // Set scientific name
    document.getElementById('scientificName').textContent = data.scientific_name || 'Unknown';

    // Set benefits
    const benefitsList = document.getElementById('benefitsList');
    benefitsList.innerHTML = '';
    if (data.benefits && data.benefits.length > 0) {
        data.benefits.forEach(benefit => {
            const li = document.createElement('li');
            li.textContent = benefit;
            benefitsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'Information not available';
        benefitsList.appendChild(li);
    }

    // Set cautions
    const cautionsList = document.getElementById('cautionsList');
    cautionsList.innerHTML = '';
    if (data.cautions && data.cautions.length > 0) {
        data.cautions.forEach(caution => {
            const li = document.createElement('li');
            li.textContent = caution;
            cautionsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'Please consult a healthcare professional';
        cautionsList.appendChild(li);
    }

    // Show results
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    errorSection.style.display = 'block';
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function resetUpload() {
    selectedFile = null;
    fileInput.value = '';
    detectBtn.disabled = true;
    previewSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

