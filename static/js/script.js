// DOM Elements
let translateBtn;
let clearBtn;
let sourceText;
let targetLang;
let translationResult;
let loadingSpinner;
let translationContainer;
let errorContainer;

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    translateBtn = document.getElementById('translate-btn');
    clearBtn = document.getElementById('clear-btn');
    sourceText = document.getElementById('source-text');
    targetLang = document.getElementById('target-lang');
    translationResult = document.getElementById('translation-result');
    loadingSpinner = document.getElementById('loading-spinner');
    translationContainer = document.getElementById('translation-container');
    errorContainer = document.getElementById('error-container');
    
    // Add event listeners
    translateBtn.addEventListener('click', translateText);
    clearBtn.addEventListener('click', clearText);
    sourceText.addEventListener('input', checkInputLength);
    
    // Initialize the UI state
    updateUIState();
});

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
    translationContainer.style.display = 'block';
}

// Function to clear the text and results
function clearText() {
    sourceText.value = '';
    translationResult.textContent = '';
    translationContainer.style.display = 'none';
    hideError();
    updateUIState();
}

// Function to show/hide loading state
function showLoading(isLoading) {
    if (isLoading) {
        loadingSpinner.style.display = 'inline-block';
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
}

// Function to hide error message
function hideError() {
    errorContainer.style.display = 'none';
}

// Function to check input length and update UI state
function checkInputLength() {
    updateUIState();
}

// Function to update UI state based on input
function updateUIState() {
    const text = sourceText.value.trim();
    translateBtn.disabled = !text;
    clearBtn.disabled = !text && translationContainer.style.display === 'none';
}
