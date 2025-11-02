// DOM Elements
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const detectBtn = document.getElementById('detectBtn');
const previewSection = document.getElementById('previewSection');
const previewImage = document.getElementById('previewImage');
const loading = document.getElementById('loading');
const resultsSection = document.getElementById('resultsSection');
const plantNameElement = document.getElementById('plantName');
const scientificNameElement = document.getElementById('scientificName');
const confidenceBadge = document.getElementById('confidenceBadge');
const resultImage = document.getElementById('resultImage');
const benefitsList = document.getElementById('benefitsList');
const cautionsList = document.getElementById('cautionsList');
const errorSection = document.getElementById('errorSection');

let selectedFile = null;

// Animation for loading
const loadingMessages = [
    'Examining plant features... 🌱',
    'Consulting our herbal database... 📚',
    'Identifying plant species... 🔍',
    'Almost there... ✨'
];

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
    
    // Show loading state
    loading.style.display = 'flex';
    previewSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    
    // Update loading message every 2 seconds
    let messageIndex = 0;
    const loadingText = loading.querySelector('p');
    const loadingInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % loadingMessages.length;
        loadingText.textContent = loadingMessages[messageIndex];
    }, 2000);
    
    try {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await fetch('/detect', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to detect plant');
        }
        
        // Display results
        displayResults(data);
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to detect plant. Please try again.');
    } finally {
        clearInterval(loadingInterval);
        loading.style.display = 'none';
    }

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
        clearInterval(loadingInterval);
        loading.style.display = 'none';
    }
});

function displayResults(data) {
    // Update plant information
    const plantInfo = data.plant_info;
    plantNameElement.textContent = plantInfo.common_name || 'Unknown Plant';
    scientificNameElement.textContent = `Scientific Name: ${plantInfo.scientific_name || 'N/A'}`;
    confidenceBadge.textContent = `${data.confidence}%`;
    
    // Update image
    resultImage.src = data.image;
    
    // Update benefits
    benefitsList.innerHTML = '';
    if (plantInfo.benefits && plantInfo.benefits.length > 0) {
        plantInfo.benefits.forEach(benefit => {
            const li = document.createElement('li');
            li.innerHTML = `✅ ${benefit}`;
            benefitsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No benefits information available';
        benefitsList.appendChild(li);
    }
    
    // Update cautions
    cautionsList.innerHTML = '';
    if (plantInfo.cautions && plantInfo.cautions.length > 0) {
        plantInfo.cautions.forEach(caution => {
            const li = document.createElement('li');
            li.innerHTML = `⚠️ ${caution}`;
            cautionsList.appendChild(li);
        });
    } else {
        const li = document.createElement('li');
        li.textContent = 'No specific cautions available';
        cautionsList.appendChild(li);
    }
    
    // Show results section
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function showError(message) {
    errorSection.innerHTML = `
        <div class="error-message">
            <span class="error-icon">❌</span>
            <p>${message}</p>
            <button onclick="this.parentElement.style.display='none'" class="close-btn">&times;</button>
        </div>
    `;
    errorSection.style.display = 'block';
    resultsSection.style.display = 'none';
    
    // Scroll to error
    errorSection.scrollIntoView({ behavior: 'smooth' });
}

// Reset upload section
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

