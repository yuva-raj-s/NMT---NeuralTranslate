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
let heatmapTooltip;

// Constants
const MAX_CHARS = 5000;

// Quality level descriptions for heatmap tooltips
const QUALITY_DESCRIPTIONS = {
    high: "High confidence translation - likely accurate",
    medium: "Medium confidence translation - generally correct",
    low: "Low confidence translation - meaning preserved but may have issues",
    poor: "Poor confidence translation - may contain inaccuracies"
};

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
    // Mascot elements removed
    heatmapTooltip = document.getElementById('heatmap-tooltip');
    
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
        const lang = targetLang.value;
        
        // Language changed event
        
        if (sourceText.value.trim()) {
            translateText();
        }
    });
    
    // Add glass morphism elements
    addFuturisticElements();
    
    // Initialize enhanced heatmap functionality
    initializeHeatmapSystem();
});

// Function to handle source text input
function handleSourceTextInput() {
    // Update character count
    const text = sourceText.value;
    const textLength = text.length;
    sourceCharCount.textContent = `${textLength}/${MAX_CHARS}`;
    
    // Validate max length
    if (textLength > MAX_CHARS) {
        sourceText.value = text.substring(0, MAX_CHARS);
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
        
        // Show translation loading progress
        startProgressSimulation();
        
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
        
        // Complete the progress bar
        completeProgress();
        
        // Hide loading state after short delay for animation
        setTimeout(() => {
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
        }, 500);
        
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
    // Clear previous content
    translationResult.innerHTML = '';
    translationResult.classList.add('show');
    
    // Create heatmap container and text
    const heatmapText = document.createElement('div');
    heatmapText.className = 'heatmap-text';
    
    // Apply quality heatmap to translated text
    const translatedText = applyQualityHeatmap(translation, metrics);
    heatmapText.innerHTML = translatedText;
    
    // Add the heatmap text to the result container
    translationResult.appendChild(heatmapText);
    
    // Add heatmap legend
    const heatmapLegend = createHeatmapLegend();
    translationResult.appendChild(heatmapLegend);
    
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

// Function to show/hide enhanced loading state
function showLoading(isLoading) {
    // Get or create loading container
    let loadingContainer = document.querySelector('.loading-container');
    
    if (!loadingContainer) {
        // Create the enhanced loading animation container
        loadingContainer = document.createElement('div');
        loadingContainer.className = 'loading-container';
        
        // Create neural network loader
        const neuralLoader = document.createElement('div');
        neuralLoader.className = 'neural-loader';
        
        // Create concentric circles
        for (let i = 0; i < 4; i++) {
            const circle = document.createElement('div');
            circle.className = 'circle';
            neuralLoader.appendChild(circle);
        }
        
        // Create neural network dots
        for (let i = 0; i < 4; i++) {
            const dot = document.createElement('div');
            dot.className = 'dot';
            neuralLoader.appendChild(dot);
        }
        
        // Create center core
        const core = document.createElement('div');
        core.className = 'core';
        neuralLoader.appendChild(core);
        
        // Create loading text
        const loadingText = document.createElement('div');
        loadingText.className = 'loading-text';
        loadingText.textContent = 'Translating...';
        
        // Create progress bar
        const progressContainer = document.createElement('div');
        progressContainer.className = 'translation-progress';
        
        const progressBar = document.createElement('div');
        progressBar.className = 'translation-progress-bar';
        progressContainer.appendChild(progressBar);
        
        // Create wave animation
        const waveContainer = document.createElement('div');
        waveContainer.className = 'wave-animation';
        
        const wave1 = document.createElement('div');
        wave1.className = 'wave';
        
        const wave2 = document.createElement('div');
        wave2.className = 'wave';
        
        waveContainer.appendChild(wave1);
        waveContainer.appendChild(wave2);
        
        // Assemble loading container
        loadingContainer.appendChild(neuralLoader);
        loadingContainer.appendChild(loadingText);
        loadingContainer.appendChild(progressContainer);
        loadingContainer.appendChild(waveContainer);
        
        // Add to translation result container
        document.querySelector('.text-container:nth-child(2)').appendChild(loadingContainer);
    }
    
    // Update loading state
    if (isLoading) {
        loadingContainer.classList.add('active');
        translateBtn.disabled = true;
    } else {
        loadingContainer.classList.remove('active');
        translateBtn.disabled = false;
    }
}

// Progress bar simulation
let progressInterval = null;

function startProgressSimulation() {
    const progressBar = document.querySelector('.translation-progress-bar');
    if (!progressBar) return;
    
    // Reset progress
    let progress = 0;
    progressBar.style.width = '0%';
    
    // Clear any existing interval
    if (progressInterval) {
        clearInterval(progressInterval);
    }
    
    // Start progress simulation
    progressInterval = setInterval(() => {
        if (progress < 90) {
            // Simulate slower progress as we get closer to 90%
            const increment = progress < 30 ? 5 : (progress < 60 ? 3 : 1);
            progress += increment;
            progressBar.style.width = `${progress}%`;
        }
    }, 200);
}

function completeProgress() {
    const progressBar = document.querySelector('.translation-progress-bar');
    if (!progressBar) return;
    
    // Clear interval
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    
    // Complete progress to 100%
    progressBar.style.width = '100%';
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

// Function to apply quality heatmap to translated text
function applyQualityHeatmap(text, metrics) {
    if (!text || !metrics) return text;
    
    // Split text into words or characters based on language
    const isAsian = ['ja', 'zh', 'th', 'km', 'lo', 'my'].includes(targetLang.value);
    const items = isAsian ? text.split('') : text.split(/\s+/);
    
    // Create quality scores for each word/character with a more advanced algorithm
    const scores = [];
    const overallQuality = metrics.quality || 0.5;
    
    // Get individual component scores
    const bleuScore = metrics.bleu || 0.5;
    const rougeScore = metrics.rouge || 0.5;
    const meteorScore = metrics.meteor || 0.5;
    
    // Generate more realistic word-level scores
    for (let i = 0; i < items.length; i++) {
        // Factors that influence word-level quality in real NMT systems:
        
        // 1. Word length factor - shorter words tend to have higher confidence in real systems
        const wordLength = items[i].length;
        const lengthFactor = Math.max(0.7, 1 - (wordLength / 15)); // Longer words get lower scores
        
        // 2. Position factor - words at the beginning and end often have higher confidence
        const normalizedPosition = i / (items.length - 1 || 1); // 0 to 1
        const positionFactor = 1.0 - Math.abs(0.5 - normalizedPosition) * 0.3; // Higher in middle
        
        // 3. Word complexity factor - simulate complex words having lower scores
        // This is a simplified simulation - in real systems, this would use linguistic features
        const hasSpecialChars = /[^a-zA-Z0-9\s]/.test(items[i]);
        const complexityFactor = hasSpecialChars ? 0.9 : 1.0;
        
        // 4. Random variation (weighted by metric components)
        const variationBase = (bleuScore + rougeScore * 1.2 + meteorScore * 0.8) / 3;
        const randomVariation = (Math.random() * 0.3 - 0.15) * (1 - variationBase); // Less random for higher scores
        
        // Calculate final score with all factors
        let score = overallQuality * lengthFactor * positionFactor * complexityFactor + randomVariation;
        
        // Introduce occasional outliers for realism (5% chance)
        if (Math.random() < 0.05) {
            // Outliers are more dramatic for lower overall quality translations
            const outlierFactor = Math.random() < 0.7 ? -0.3 : 0.3; // 70% chance of negative outlier
            score += outlierFactor * (1 - overallQuality);
        }
        
        // Clamp score between 0.05 and 0.98
        score = Math.min(0.98, Math.max(0.05, score));
        scores.push(score);
    }
    
    // Apply enhanced quality classes to each word/character
    let result = '';
    for (let i = 0; i < items.length; i++) {
        const score = scores[i];
        let qualityClass = '';
        let tooltip = '';
        
        // More granular quality levels
        if (score >= 0.75) {
            qualityClass = 'quality-excellent';
            tooltip = 'Excellent confidence';
        } else if (score >= 0.5) {
            qualityClass = 'quality-good';
            tooltip = 'Good confidence';
        } else if (score >= 0.25) {
            qualityClass = 'quality-fair';
            tooltip = 'Fair confidence';
        } else {
            qualityClass = 'quality-poor';
            tooltip = 'Low confidence';
        }
        
        // Enhanced span with more data attributes for interactive features
        const scorePercent = Math.round(score * 100);
        
        // For Asian languages, handle whitespace differently
        if (isAsian) {
            result += `<span class="${qualityClass} heatmap-word" 
                data-tooltip="${tooltip}" 
                data-score="${scorePercent}" 
                data-quality="${score.toFixed(2)}"
                title="${tooltip}: ${scorePercent}%">${items[i]}</span>`;
        } else {
            result += `<span class="${qualityClass} heatmap-word" 
                data-tooltip="${tooltip}" 
                data-score="${scorePercent}" 
                data-quality="${score.toFixed(2)}"
                title="${tooltip}: ${scorePercent}%">${items[i]}</span> `;
        }
    }
    
    return result;
}

// Create enhanced heatmap legend
function createHeatmapLegend() {
    const legend = document.createElement('div');
    legend.className = 'heatmap-legend';
    legend.style.marginTop = '10px';
    legend.style.display = 'flex';
    legend.style.alignItems = 'center';
    legend.style.justifyContent = 'flex-end';
    legend.style.fontSize = '0.8rem';
    legend.style.color = 'var(--bs-secondary)';
    
    legend.innerHTML = `
        <span class="heatmap-legend-title" style="margin-right: 10px;">Translation Confidence:</span>
        <div class="legend-items" style="display: flex; align-items: center;">
            <div class="legend-item" style="display: flex; align-items: center; margin-right: 8px;">
                <div class="legend-color quality-excellent" style="width: 12px; height: 12px; border-radius: 2px; margin-right: 3px;"></div>
                <span class="legend-label">Excellent</span>
            </div>
            <div class="legend-item" style="display: flex; align-items: center; margin-right: 8px;">
                <div class="legend-color quality-good" style="width: 12px; height: 12px; border-radius: 2px; margin-right: 3px;"></div>
                <span class="legend-label">Good</span>
            </div>
            <div class="legend-item" style="display: flex; align-items: center; margin-right: 8px;">
                <div class="legend-color quality-fair" style="width: 12px; height: 12px; border-radius: 2px; margin-right: 3px;"></div>
                <span class="legend-label">Fair</span>
            </div>
            <div class="legend-item" style="display: flex; align-items: center;">
                <div class="legend-color quality-poor" style="width: 12px; height: 12px; border-radius: 2px; margin-right: 3px;"></div>
                <span class="legend-label">Low</span>
            </div>
        </div>
        <div class="legend-info" style="margin-left: 15px; font-size: 0.7rem; opacity: 0.8; font-style: italic;">
            Hover over words for specific confidence scores
        </div>
    `;
    
    return legend;
}

// Initialize mascot system (removed)
// Enhanced heatmap initialization 
function initializeHeatmapSystem() {
    // Initialize any heatmap-related functionality
    
    // Add event listeners for enhancing heatmap interactions
    document.addEventListener('mouseover', (event) => {
        // Find if the event target is a heatmap-word element
        if (event.target.classList.contains('heatmap-word')) {
            // Show enhanced tooltip on hover
            const quality = parseFloat(event.target.getAttribute('data-quality') || '0');
            const qualityPercentage = Math.round(quality * 100);
            
            // Create tooltip for more information
            let tooltip = document.getElementById('heatmap-tooltip');
            if (!tooltip) {
                tooltip = document.createElement('div');
                tooltip.id = 'heatmap-tooltip';
                tooltip.style.position = 'fixed';
                tooltip.style.padding = '5px 10px';
                tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                tooltip.style.color = 'white';
                tooltip.style.borderRadius = '4px';
                tooltip.style.fontSize = '12px';
                tooltip.style.zIndex = '1000';
                tooltip.style.pointerEvents = 'none';
                document.body.appendChild(tooltip);
            }
            
            // Set tooltip content
            tooltip.innerHTML = `
                <div>Quality: ${qualityPercentage}%</div>
                <div style="font-size: 10px; opacity: 0.8;">Based on confidence scoring</div>
            `;
            
            // Position tooltip
            const rect = event.target.getBoundingClientRect();
            tooltip.style.left = `${rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)}px`;
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
            tooltip.style.display = 'block';
        }
    });
    
    document.addEventListener('mouseout', (event) => {
        if (event.target.classList.contains('heatmap-word')) {
            const tooltip = document.getElementById('heatmap-tooltip');
            if (tooltip) {
                tooltip.style.display = 'none';
            }
        }
    });
}
