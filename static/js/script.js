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
    
    // Add event listeners
    translateBtn.addEventListener('click', translateText);
    clearBtn.addEventListener('click', clearText);
    sourceText.addEventListener('input', handleSourceTextInput);
    copySourceBtn.addEventListener('click', () => copyText(sourceText.value));
    copyTranslationBtn.addEventListener('click', () => copyText(translationResult.textContent));
    swapBtn.addEventListener('click', swapLanguages);
    
    // Initialize the UI state
    updateUIState();
    
    // Auto-trigger translation when language changes
    targetLang.addEventListener('change', () => {
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
                target_lang: lang
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
        
        // Display the translation result
        displayTranslation(data.translation);
        
    } catch (error) {
        showLoading(false);
        showError('An error occurred. Please try again later.');
        console.error('Translation error:', error);
    }
}

// Function to display the translation result
function displayTranslation(translation) {
    translationResult.textContent = translation;
    translationResult.classList.add('show');
    
    // Highlight translation result briefly
    translationResult.style.backgroundColor = 'rgba(66, 133, 244, 0.1)';
    setTimeout(() => {
        translationResult.style.backgroundColor = '';
    }, 300);
}

// Function to clear the text and results
function clearText() {
    sourceText.value = '';
    translationResult.textContent = '';
    translationResult.classList.remove('show');
    hideError();
    sourceCharCount.textContent = `0/${MAX_CHARS}`;
    sourceCharCount.style.color = '#888';
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
