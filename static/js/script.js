// DOM Elements
let translateBtn;
let clearBtn;
let sourceText;
let targetLang;
let translationResult;
let loadingSpinner;
let errorContainer;
let sourceCharCount;
let copySourceBtn;
let copyTranslationBtn;
let swapBtn;
let useMbartSwitch;

// Constants
const MAX_CHARS = 5000;

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    translateBtn = document.getElementById('translate-btn');
    clearBtn = document.getElementById('clear-btn');
    sourceText = document.getElementById('source-text');
    targetLang = document.getElementById('target-lang');
    translationResult = document.getElementById('translation-result');
    loadingSpinner = document.getElementById('loading-spinner');
    errorContainer = document.getElementById('error-container');
    sourceCharCount = document.getElementById('source-char-count');
    copySourceBtn = document.getElementById('copy-source-btn');
    copyTranslationBtn = document.getElementById('copy-translation-btn');
    swapBtn = document.getElementById('swap-btn');
    useMbartSwitch = document.getElementById('use-mbart');
    
    // Add event listeners
    translateBtn.addEventListener('click', translateText);
    clearBtn.addEventListener('click', clearText);
    sourceText.addEventListener('input', handleSourceTextInput);
    copySourceBtn.addEventListener('click', () => copyText(sourceText.value));
    copyTranslationBtn.addEventListener('click', () => copyText(translationResult.textContent));
    swapBtn.addEventListener('click', swapLanguages);
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize the UI state
    updateUIState();
    
    // Auto-trigger translation when language changes
    targetLang.addEventListener('change', () => {
        if (sourceText.value.trim()) {
            translateText();
        }
    });
    
    // Auto-trigger translation when model option changes
    useMbartSwitch.addEventListener('change', () => {
        if (sourceText.value.trim()) {
            translateText();
        }
    });
});

// Function to handle source text input
function handleSourceTextInput() {
    // Update character count
    const textLength = sourceText.value.length;
    sourceCharCount.textContent = `${textLength}/${MAX_CHARS}`;
    
    // Validate max length
    if (textLength > MAX_CHARS) {
        sourceText.value = sourceText.value.substring(0, MAX_CHARS);
        sourceCharCount.textContent = `${MAX_CHARS}/${MAX_CHARS}`;
        sourceCharCount.style.color = '#f44336';
    } else {
        sourceCharCount.style.color = textLength > MAX_CHARS * 0.9 ? '#f4b400' : '#888';
    }
    
    // Update UI state
    updateUIState();
    
    // Auto-translate if text length is reasonable
    if (textLength > 0 && textLength <= 100) {
        // Use debounce to avoid too many requests
        clearTimeout(window.translateTimeout);
        window.translateTimeout = setTimeout(() => {
            translateText();
        }, 1000);
    }
}

// Function to handle the translation
async function translateText() {
    try {
        // Get the text and target language
        const text = sourceText.value.trim();
        const lang = targetLang.value;
        const useMbart = useMbartSwitch ? useMbartSwitch.checked : false;
        
        // Validate input
        if (!text) {
            showError('Please enter some text to translate.');
            return;
        }
        
        // Show loading state and hide any previous results or errors
        showLoading(true);
        hideError();
        
        // Send the translation request to the backend
        const response = await fetch('/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                target_lang: lang,
                use_mbart: useMbart
            })
        });
        
        // Parse the response
        const data = await response.json();
        
        // Hide loading state
        showLoading(false);
        
        // Check for errors
        if (!response.ok || data.error) {
            showError(data.error || 'Translation failed. Please try again.');
            return;
        }
        
        // Display the translation result with confidence score
        displayTranslation(data.translation, data.confidence);
        
        // Show model info
        if (data.model === 'mbart') {
            showModelInfo('Using mBART neural model', 'var(--bs-info)');
        } else {
            showModelInfo('Using legacy translation model', 'var(--bs-secondary)');
        }
        
    } catch (error) {
        showLoading(false);
        showError('An error occurred. Please try again later.');
        console.error('Translation error:', error);
    }
}

// Function to show which model was used
function showModelInfo(message, color) {
    const modelInfo = document.createElement('div');
    modelInfo.className = 'model-info';
    modelInfo.textContent = message;
    modelInfo.style.fontSize = '0.8rem';
    modelInfo.style.color = color;
    modelInfo.style.textAlign = 'right';
    modelInfo.style.marginTop = '5px';
    modelInfo.style.fontStyle = 'italic';
    
    // Replace any existing model info
    const existingInfo = document.querySelector('.model-info');
    if (existingInfo) {
        existingInfo.remove();
    }
    
    // Append after translation result
    translationResult.parentNode.appendChild(modelInfo);
    
    // Fade out after 5 seconds
    setTimeout(() => {
        modelInfo.style.opacity = '0.5';
    }, 5000);
}

// Function to display the translation result
function displayTranslation(translation, confidence) {
    translationResult.textContent = translation;
    translationResult.classList.add('show');
    
    // Highlight translation result briefly
    translationResult.style.backgroundColor = 'rgba(66, 133, 244, 0.1)';
    setTimeout(() => {
        translationResult.style.backgroundColor = '';
    }, 300);
    
    // Display confidence indicator if provided
    if (confidence !== undefined) {
        const confidenceElement = document.createElement('div');
        confidenceElement.className = 'confidence-indicator';
        
        // Determine confidence color and label
        let confidenceColor, confidenceLabel;
        if (confidence >= 0.85) {
            confidenceColor = 'var(--bs-success)';
            confidenceLabel = 'High';
        } else if (confidence >= 0.65) {
            confidenceColor = 'var(--bs-info)';
            confidenceLabel = 'Medium';
        } else {
            confidenceColor = 'var(--bs-warning)';
            confidenceLabel = 'Low';
        }
        
        // Create a progress bar for the confidence score
        const confidenceValue = Math.round(confidence * 100);
        confidenceElement.innerHTML = `
            <div class="confidence-text" style="margin-top: 15px; font-size: 0.85rem;">
                <span style="color: ${confidenceColor}; font-weight: 500;">
                    ${confidenceLabel} confidence (${confidenceValue}%)
                </span>
            </div>
            <div class="progress mt-1" style="height: 4px; width: 100%;">
                <div class="progress-bar" role="progressbar" 
                    style="width: ${confidenceValue}%; background-color: ${confidenceColor};" 
                    aria-valuenow="${confidenceValue}" aria-valuemin="0" aria-valuemax="100">
                </div>
            </div>
        `;
        
        // Replace any existing confidence indicator
        const existingConfidence = document.querySelector('.confidence-indicator');
        if (existingConfidence) {
            existingConfidence.remove();
        }
        
        // Add after translation result
        translationResult.parentNode.appendChild(confidenceElement);
    }
}

// Function to clear the text and results
function clearText() {
    sourceText.value = '';
    translationResult.textContent = '';
    translationResult.classList.remove('show');
    hideError();
    sourceCharCount.textContent = `0/${MAX_CHARS}`;
    sourceCharCount.style.color = '#888';
    
    // Clear model info if present
    const modelInfo = document.querySelector('.model-info');
    if (modelInfo) {
        modelInfo.remove();
    }
    
    // Clear confidence indicator if present
    const confidenceIndicator = document.querySelector('.confidence-indicator');
    if (confidenceIndicator) {
        confidenceIndicator.remove();
    }
    
    updateUIState();
}

// Function to show/hide loading state
function showLoading(isLoading) {
    if (isLoading) {
        loadingSpinner.style.display = 'block';
        translateBtn.disabled = true;
    } else {
        loadingSpinner.style.display = 'none';
        translateBtn.disabled = false;
    }
}

// Function to show error message
function showError(message) {
    errorContainer.textContent = message;
    errorContainer.style.display = 'block';
    
    // Auto-hide error after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

// Function to hide error message
function hideError() {
    errorContainer.style.display = 'none';
}

// Function to update UI state based on input
function updateUIState() {
    const text = sourceText.value.trim();
    translateBtn.disabled = !text;
    clearBtn.disabled = !text && !translationResult.textContent;
    copySourceBtn.style.display = text ? 'block' : 'none';
    copyTranslationBtn.style.display = translationResult.textContent ? 'block' : 'none';
}

// Function to copy text to clipboard
function copyText(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show brief success feedback
        const successMessage = document.createElement('div');
        successMessage.innerText = 'Copied!';
        successMessage.className = 'copy-success';
        successMessage.style.position = 'fixed';
        successMessage.style.top = '10%';
        successMessage.style.left = '50%';
        successMessage.style.transform = 'translateX(-50%)';
        successMessage.style.backgroundColor = 'rgba(15, 157, 88, 0.9)';
        successMessage.style.color = 'white';
        successMessage.style.padding = '10px 20px';
        successMessage.style.borderRadius = '4px';
        successMessage.style.zIndex = '1000';
        document.body.appendChild(successMessage);
        
        setTimeout(() => {
            document.body.removeChild(successMessage);
        }, 1500);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

// Function to swap languages
function swapLanguages() {
    // Currently we can only translate from English to other languages
    // This animation is just for show until we implement bi-directional translation
    swapBtn.classList.add('rotating');
    
    setTimeout(() => {
        swapBtn.classList.remove('rotating');
    }, 500);
}

// Add animation CSS
const style = document.createElement('style');
style.innerHTML = `
.rotating {
  animation: rotate-animation 0.5s ease;
}

@keyframes rotate-animation {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(180deg); }
}

#translation-result {
  opacity: 0;
  transition: opacity 0.3s ease;
}

#translation-result.show {
  opacity: 1;
}
`;
document.head.appendChild(style);
