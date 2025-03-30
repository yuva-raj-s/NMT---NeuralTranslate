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
    
    // Add glass morphism elements
    addFuturisticElements();
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
        
        // Display the translation result with evaluation metrics
        displayTranslation(data.translation, data.metrics, data.percentages);
        
        // Show model info
        showModelInfo('Using mBART neural model with industry-standard metrics', 'var(--bs-info)');
        
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

// Function to display the translation result with evaluation metrics
function displayTranslation(translation, metrics, percentages) {
    translationResult.textContent = translation;
    translationResult.classList.add('show');
    
    // Highlight translation result briefly
    translationResult.style.backgroundColor = 'rgba(66, 133, 244, 0.1)';
    setTimeout(() => {
        translationResult.style.backgroundColor = '';
    }, 300);
    
    // Display evaluation metrics if provided
    if (metrics && percentages) {
        const metricsElement = document.createElement('div');
        metricsElement.className = 'metrics-container';
        metricsElement.style.marginTop = '15px';
        
        // Create evaluation metrics visualization
        const getMetricColor = (value) => {
            if (value >= 0.7) return 'var(--bs-success)';
            if (value >= 0.4) return 'var(--bs-info)';
            if (value >= 0.2) return 'var(--bs-warning)';
            return 'var(--bs-danger)';
        };
        
        const getMetricLabel = (value) => {
            if (value >= 0.7) return 'Excellent';
            if (value >= 0.4) return 'Good';
            if (value >= 0.2) return 'Fair';
            return 'Poor';
        };
        
        // Create metrics visualization
        metricsElement.innerHTML = `
            <h6 class="metrics-title mb-2" style="font-size: 0.9rem; font-weight: 600; color: var(--bs-secondary);">
                Translation Quality Metrics
            </h6>
            
            <div class="row g-2">
                <div class="col-4">
                    <div class="metric-card p-2 text-center" style="border-radius: 6px; border: 1px solid rgba(0,0,0,0.1);">
                        <div class="metric-name" style="font-size: 0.75rem; color: var(--bs-secondary);">BLEU</div>
                        <div class="metric-value" style="font-size: 1.1rem; font-weight: 600; color: ${getMetricColor(metrics.bleu)};">
                            ${percentages.bleu}%
                        </div>
                        <div class="metric-label" style="font-size: 0.7rem; color: ${getMetricColor(metrics.bleu)};">
                            ${getMetricLabel(metrics.bleu)}
                        </div>
                        <div class="progress mt-1" style="height: 3px;">
                            <div class="progress-bar" role="progressbar" 
                                style="width: ${percentages.bleu}%; background-color: ${getMetricColor(metrics.bleu)};" 
                                aria-valuenow="${percentages.bleu}" aria-valuemin="0" aria-valuemax="100">
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-4">
                    <div class="metric-card p-2 text-center" style="border-radius: 6px; border: 1px solid rgba(0,0,0,0.1);">
                        <div class="metric-name" style="font-size: 0.75rem; color: var(--bs-secondary);">ROUGE</div>
                        <div class="metric-value" style="font-size: 1.1rem; font-weight: 600; color: ${getMetricColor(metrics.rouge)};">
                            ${percentages.rouge}%
                        </div>
                        <div class="metric-label" style="font-size: 0.7rem; color: ${getMetricColor(metrics.rouge)};">
                            ${getMetricLabel(metrics.rouge)}
                        </div>
                        <div class="progress mt-1" style="height: 3px;">
                            <div class="progress-bar" role="progressbar" 
                                style="width: ${percentages.rouge}%; background-color: ${getMetricColor(metrics.rouge)};" 
                                aria-valuenow="${percentages.rouge}" aria-valuemin="0" aria-valuemax="100">
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-4">
                    <div class="metric-card p-2 text-center" style="border-radius: 6px; border: 1px solid rgba(0,0,0,0.1);">
                        <div class="metric-name" style="font-size: 0.75rem; color: var(--bs-secondary);">METEOR</div>
                        <div class="metric-value" style="font-size: 1.1rem; font-weight: 600; color: ${getMetricColor(metrics.meteor)};">
                            ${percentages.meteor}%
                        </div>
                        <div class="metric-label" style="font-size: 0.7rem; color: ${getMetricColor(metrics.meteor)};">
                            ${getMetricLabel(metrics.meteor)}
                        </div>
                        <div class="progress mt-1" style="height: 3px;">
                            <div class="progress-bar" role="progressbar" 
                                style="width: ${percentages.meteor}%; background-color: ${getMetricColor(metrics.meteor)};" 
                                aria-valuenow="${percentages.meteor}" aria-valuemin="0" aria-valuemax="100">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="overall-quality mt-3">
                <div class="d-flex justify-content-between align-items-center">
                    <span style="font-size: 0.8rem; color: var(--bs-secondary);">Overall Quality</span>
                    <span style="font-size: 0.8rem; font-weight: 500; color: ${getMetricColor(metrics.quality)};">
                        ${getMetricLabel(metrics.quality)} (${percentages.quality}%)
                    </span>
                </div>
                <div class="progress mt-1" style="height: 6px;">
                    <div class="progress-bar" role="progressbar" 
                        style="width: ${percentages.quality}%; background-color: ${getMetricColor(metrics.quality)};" 
                        aria-valuenow="${percentages.quality}" aria-valuemin="0" aria-valuemax="100">
                    </div>
                </div>
            </div>
            
            <div class="metrics-info mt-2" style="font-size: 0.7rem; color: var(--bs-secondary); font-style: italic;">
                BLEU, ROUGE, and METEOR are industry-standard metrics for evaluating translation quality
            </div>
        `;
        
        // Replace any existing metrics container
        const existingMetrics = document.querySelector('.metrics-container');
        if (existingMetrics) {
            existingMetrics.remove();
        }
        
        // Replace any existing confidence indicator (from previous version)
        const existingConfidence = document.querySelector('.confidence-indicator');
        if (existingConfidence) {
            existingConfidence.remove();
        }
        
        // Add after translation result
        translationResult.parentNode.appendChild(metricsElement);
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
    
    // Clear confidence indicator if present (legacy)
    const confidenceIndicator = document.querySelector('.confidence-indicator');
    if (confidenceIndicator) {
        confidenceIndicator.remove();
    }
    
    // Clear metrics container if present
    const metricsContainer = document.querySelector('.metrics-container');
    if (metricsContainer) {
        metricsContainer.remove();
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

// Function to add futuristic UI elements
function addFuturisticElements() {
    // Add background particles
    createParticles();
    
    // Add glow effects to translator container
    addGlowEffects();
    
    // Apply glass morphism to metric cards dynamically
    document.addEventListener('DOMNodeInserted', function(e) {
        if (e.target.classList && e.target.classList.contains('metrics-container')) {
            applyGlassToMetrics(e.target);
        }
    });
}

// Create floating background particles
function createParticles() {
    const colors = [
        'rgba(66, 133, 244, 0.4)',  // Blue
        'rgba(156, 39, 176, 0.3)',  // Purple
        'rgba(0, 188, 212, 0.3)',   // Teal
        'rgba(233, 30, 99, 0.2)'    // Pink
    ];
    
    const sizes = [4, 6, 8, 10, 12];
    const count = 15; // Number of particles
    
    for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random properties
        const size = sizes[Math.floor(Math.random() * sizes.length)];
        const color = colors[Math.floor(Math.random() * colors.length)];
        const left = Math.random() * 100;
        const delay = Math.random() * 5;
        const duration = 15 + Math.random() * 10;
        
        // Apply styles
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        particle.style.backgroundColor = color;
        particle.style.left = `${left}vw`;
        particle.style.top = `${Math.random() * 100}vh`;
        particle.style.animationDelay = `${delay}s`;
        particle.style.animationDuration = `${duration}s`;
        
        // Add to body
        document.body.appendChild(particle);
    }
}

// Add ambient glow effects
function addGlowEffects() {
    const translatorContainer = document.querySelector('.translator-container');
    if (!translatorContainer) return;
    
    // Add glow elements
    const glow1 = document.createElement('div');
    glow1.className = 'glow glow-1';
    
    const glow2 = document.createElement('div');
    glow2.className = 'glow glow-2';
    
    translatorContainer.appendChild(glow1);
    translatorContainer.appendChild(glow2);
}

// Apply glass morphism to metric cards
function applyGlassToMetrics(metricsContainer) {
    // Get all metric cards
    const metricCards = metricsContainer.querySelectorAll('.metric-card');
    
    metricCards.forEach(card => {
        // Apply glass morphism
        card.style.background = 'rgba(40, 40, 40, 0.4)';
        card.style.backdropFilter = 'blur(8px)';
        card.style.WebkitBackdropFilter = 'blur(8px)';
        card.style.border = '1px solid rgba(255, 255, 255, 0.08)';
        card.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.1)';
        card.style.transition = 'all 0.3s ease';
        
        // Add hover effect
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-5px)';
            card.style.boxShadow = '0 12px 32px rgba(0, 0, 0, 0.15)';
            card.style.border = '1px solid rgba(255, 255, 255, 0.12)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0)';
            card.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.1)';
            card.style.border = '1px solid rgba(255, 255, 255, 0.08)';
        });
    });
    
    // Style the overall quality section
    const overallQuality = metricsContainer.querySelector('.overall-quality');
    if (overallQuality) {
        overallQuality.style.background = 'rgba(30, 30, 30, 0.3)';
        overallQuality.style.padding = '10px';
        overallQuality.style.borderRadius = '8px';
        overallQuality.style.marginTop = '15px';
        overallQuality.style.backdropFilter = 'blur(5px)';
        overallQuality.style.WebkitBackdropFilter = 'blur(5px)';
        overallQuality.style.border = '1px solid rgba(255, 255, 255, 0.05)';
    }
}
