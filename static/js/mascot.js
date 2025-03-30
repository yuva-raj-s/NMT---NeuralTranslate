/**
 * TranslatorMascot - A playful mascot for the Neural Machine Translation application
 * 
 * This class provides an interactive mascot that reacts to user interactions,
 * translation operations, and language selections to enhance the user experience.
 */
class TranslatorMascot {
    constructor() {
        // Mascot configuration
        this.config = {
            defaultMessage: 'Hello! I\'m Neuron, your translation assistant. Enter some text to get started!',
            thinkingMessages: [
                'Analyzing language patterns...',
                'Accessing neural language model...',
                'Processing translation...',
                'Computing linguistic mappings...'
            ],
            languages: {
                'bn': { name: 'Bengali', icon: '🇧🇩', greeting: 'শুভেচ্ছা!' },
                'en': { name: 'English', icon: '🇬🇧', greeting: 'Hello!' },
                'fil': { name: 'Filipino', icon: '🇵🇭', greeting: 'Kamusta!' },
                'hi': { name: 'Hindi', icon: '🇮🇳', greeting: 'नमस्ते!' },
                'id': { name: 'Indonesian', icon: '🇮🇩', greeting: 'Halo!' },
                'ja': { name: 'Japanese', icon: '🇯🇵', greeting: 'こんにちは!' },
                'km': { name: 'Khmer', icon: '🇰🇭', greeting: 'សួស្តី!' },
                'lo': { name: 'Lao', icon: '🇱🇦', greeting: 'ສະບາຍດີ!' },
                'ms': { name: 'Malay', icon: '🇲🇾', greeting: 'Selamat datang!' },
                'my': { name: 'Myanmar', icon: '🇲🇲', greeting: 'မင်္ဂလာပါ!' },
                'th': { name: 'Thai', icon: '🇹🇭', greeting: 'สวัสดี!' },
                'vi': { name: 'Vietnamese', icon: '🇻🇳', greeting: 'Xin chào!' },
                'zh': { name: 'Chinese', icon: '🇨🇳', greeting: '你好!' }
            }
        };
        
        // Mascot state
        this.currentLanguage = 'en';
        this.isThinking = false;
        this.state = 'idle'; // idle, thinking, speaking, error
        
        // Initialize the mascot
        this.init();
    }
    
    /**
     * Initialize the mascot
     */
    init() {
        // Create the mascot DOM structure
        this.createMascotDOM();
        
        // Add event listeners for mascot interaction
        this.addEventListeners();
        
        // Show initial greeting
        setTimeout(() => {
            this.speak(this.config.defaultMessage);
        }, 1000);
    }
    
    /**
     * Create the mascot DOM elements
     */
    createMascotDOM() {
        // Create mascot container
        this.container = document.createElement('div');
        this.container.className = 'mascot-container';
        
        // Create mascot character
        this.character = document.createElement('div');
        this.character.className = 'mascot-character';
        
        // Create mascot avatar with language icon
        this.avatar = document.createElement('div');
        this.avatar.className = 'mascot-avatar';
        this.avatar.innerHTML = `
            <div class="mascot-face">
                <div class="mascot-eyes">
                    <div class="mascot-eye"></div>
                    <div class="mascot-eye"></div>
                </div>
                <div class="mascot-mouth"></div>
            </div>
            <div class="mascot-language-icon">
                ${this.config.languages[this.currentLanguage].icon}
            </div>
        `;
        
        // Create speech bubble
        this.speechBubble = document.createElement('div');
        this.speechBubble.className = 'mascot-speech-bubble';
        
        // Create thinking animation
        this.thinkingDots = document.createElement('div');
        this.thinkingDots.className = 'mascot-thinking-dots';
        this.thinkingDots.innerHTML = '<span></span><span></span><span></span>';
        
        // Create speech text
        this.speechText = document.createElement('div');
        this.speechText.className = 'mascot-speech-text';
        
        // Assemble speech bubble
        this.speechBubble.appendChild(this.thinkingDots);
        this.speechBubble.appendChild(this.speechText);
        
        // Assemble mascot
        this.character.appendChild(this.avatar);
        this.character.appendChild(this.speechBubble);
        this.container.appendChild(this.character);
        
        // Add mascot to the document
        document.querySelector('.translator-container').appendChild(this.container);
    }
    
    /**
     * Add event listeners for mascot interaction
     */
    addEventListeners() {
        // Listen for translation events
        document.addEventListener('translation:started', (e) => {
            this.onTranslationStarted(e.detail.text, e.detail.targetLang);
        });
        
        document.addEventListener('translation:success', (e) => {
            this.onTranslationSuccess(e.detail.translation);
        });
        
        document.addEventListener('translation:error', (e) => {
            this.onTranslationError(e.detail.error);
        });
        
        document.addEventListener('translation:languageChanged', (e) => {
            this.onLanguageChanged(e.detail.language);
        });
        
        document.addEventListener('translation:textChanged', (e) => {
            this.onTextChanged(e.detail.text);
        });
        
        // Add click interaction with mascot
        this.character.addEventListener('click', () => {
            if (!this.isThinking) {
                // Show a random tip when clicked
                const tips = [
                    'Try translating short sentences for the best results!',
                    'You can copy the translation with the copy button.',
                    'BLEU, ROUGE, and METEOR are metrics that evaluate translation quality.',
                    'This translator uses mBART, a multilingual neural machine translation model.',
                    `The ${this.config.languages[this.currentLanguage].name} translations are powered by the ALT dataset.`,
                    'Higher metric scores indicate better translation quality.',
                    'Try clearing the text and starting fresh for a new translation!'
                ];
                
                const randomTip = tips[Math.floor(Math.random() * tips.length)];
                this.speak(randomTip, 4000);
            }
        });
    }
    
    /**
     * Make the mascot speak (show a message in the speech bubble)
     * @param {string} message - The message to display
     * @param {number} duration - How long to show the message (ms)
     */
    speak(message, duration = 4000) {
        // Clear any existing timers
        if (this.speakTimer) {
            clearTimeout(this.speakTimer);
        }
        
        // Update mascot state
        this.state = 'speaking';
        this.isThinking = false;
        
        // Show speech bubble and hide thinking dots
        this.thinkingDots.style.display = 'none';
        this.speechBubble.style.display = 'block';
        this.speechText.textContent = message;
        
        // Animate the speech bubble
        this.speechBubble.style.transform = 'scale(0.8)';
        this.speechBubble.style.opacity = '0';
        
        setTimeout(() => {
            this.speechBubble.style.transform = 'scale(1)';
            this.speechBubble.style.opacity = '1';
        }, 50);
        
        // If duration is specified, hide the speech bubble after that time
        if (duration !== Infinity) {
            this.speakTimer = setTimeout(() => {
                this.speechBubble.style.transform = 'scale(0.8)';
                this.speechBubble.style.opacity = '0';
                
                setTimeout(() => {
                    this.speechBubble.style.display = 'none';
                    this.state = 'idle';
                }, 300);
            }, duration);
        }
    }
    
    /**
     * Make the mascot appear to be thinking
     * @param {boolean} isThinking - Whether the mascot should be thinking
     */
    think(isThinking) {
        this.isThinking = isThinking;
        
        if (isThinking) {
            // Clear any speaking timer
            if (this.speakTimer) {
                clearTimeout(this.speakTimer);
            }
            
            // Show thinking animation
            this.state = 'thinking';
            this.speechBubble.style.display = 'block';
            this.thinkingDots.style.display = 'flex';
            this.speechText.textContent = '';
            
            // Show a random thinking message
            const thinkingIndex = Math.floor(Math.random() * this.config.thinkingMessages.length);
            const thinkingMessage = this.config.thinkingMessages[thinkingIndex];
            
            // Replace thinking messages with intervals
            if (this.thinkingInterval) clearInterval(this.thinkingInterval);
            
            this.thinkingInterval = setInterval(() => {
                const randomIndex = Math.floor(Math.random() * this.config.thinkingMessages.length);
                this.speechText.textContent = this.config.thinkingMessages[randomIndex];
            }, 2000);
            
            this.speechText.textContent = thinkingMessage;
        } else {
            // Stop thinking animation
            if (this.thinkingInterval) {
                clearInterval(this.thinkingInterval);
                this.thinkingInterval = null;
            }
        }
    }
    
    /**
     * Handle the start of a translation
     * @param {string} text - The text being translated
     * @param {string} targetLang - The target language code
     */
    onTranslationStarted(text, targetLang) {
        this.think(true);
        
        // Update mascot language icon if different
        if (this.currentLanguage !== targetLang) {
            this.onLanguageChanged(targetLang);
        }
        
        // Show a message about the translation in progress
        const sourceLang = 'English';
        const targetLangName = this.config.languages[targetLang]?.name || 'Unknown Language';
        
        // Shortened text preview
        const textPreview = text.length > 15 ? text.substring(0, 15) + '...' : text;
        
        // Random translation messages
        const translationStartMessages = [
            `Translating from ${sourceLang} to ${targetLangName}...`,
            `Working on your ${targetLangName} translation...`,
            `Processing with neural model for ${targetLangName}...`,
            `Connecting neural pathways for ${targetLangName}...`
        ];
        
        const randomMessage = translationStartMessages[Math.floor(Math.random() * translationStartMessages.length)];
        this.speechText.textContent = randomMessage;
    }
    
    /**
     * Handle a successful translation
     * @param {string} translation - The translated text
     */
    onTranslationSuccess(translation) {
        this.think(false);
        
        // Show a success message
        const successMessages = [
            `Translation complete! How does it look?`,
            `All done! Check out the quality metrics below.`,
            `${this.config.languages[this.currentLanguage].greeting} Translation successful!`,
            `Neural translation complete! Need anything else?`
        ];
        
        const randomMessage = successMessages[Math.floor(Math.random() * successMessages.length)];
        this.speak(randomMessage, 6000);
        
        // Make the mascot appear happy
        this.avatar.classList.add('mascot-happy');
        setTimeout(() => {
            this.avatar.classList.remove('mascot-happy');
        }, 2000);
    }
    
    /**
     * Handle a translation error
     * @param {string} error - The error message
     */
    onTranslationError(error) {
        this.think(false);
        
        // Show an error message
        this.state = 'error';
        this.speak(`Oops! Something went wrong with the translation. Please try again.`, 8000);
        
        // Make the mascot appear sad
        this.avatar.classList.add('mascot-sad');
        setTimeout(() => {
            this.avatar.classList.remove('mascot-sad');
        }, 3000);
    }
    
    /**
     * Handle a language change event
     * @param {string} language - The new language code
     */
    onLanguageChanged(language) {
        // Update mascot language
        this.currentLanguage = language;
        
        // Update the language icon
        this.updateLanguageIcon(language);
        
        // Show a greeting in the new language
        const langInfo = this.config.languages[language];
        if (langInfo) {
            this.speak(`${langInfo.greeting} Now translating to ${langInfo.name}!`, 3000);
        }
    }
    
    /**
     * Handle text input changes
     * @param {string} text - The current text
     */
    onTextChanged(text) {
        // Only react if text is not too long and not empty
        if (text.length > 0 && text.length < 100) {
            // Show typing reaction occasionally (not on every keystroke)
            if (Math.random() < 0.2 && this.state === 'idle') {
                const reactionMessages = [
                    "I see you're typing something...",
                    "Type a bit more and I'll start translating!",
                    "Looking good! Keep typing.",
                    "Ready to translate when you are!"
                ];
                
                const randomMessage = reactionMessages[Math.floor(Math.random() * reactionMessages.length)];
                this.speak(randomMessage, 2500);
            }
        }
    }
    
    /**
     * Update the language icon
     * @param {string} language - The language code
     */
    updateLanguageIcon(language) {
        // Get the language information
        const langInfo = this.config.languages[language];
        
        if (langInfo) {
            // Update the icon
            const languageIcon = this.avatar.querySelector('.mascot-language-icon');
            if (languageIcon) {
                languageIcon.textContent = langInfo.icon;
            }
            
            // Add a class for language-specific styling
            this.avatar.className = 'mascot-avatar';
            this.avatar.classList.add(`lang-${language}`);
        }
    }
}

// Initialize the mascot when the DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.translatorMascot = new TranslatorMascot();
});