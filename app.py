import os
import logging
from flask import Flask, render_template, request, jsonify
from translation_model import TranslationModel
try:
    from mbart_integration import get_translator
    HAS_MBART = True
except ImportError:
    HAS_MBART = False

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Initialize the translation models
translation_model = None
mbart_translator = None

# Available target languages (all 13 languages from ALT dataset)
SUPPORTED_LANGUAGES = {
    "bn": "Bengali",
    "en": "English",
    "fil": "Filipino",
    "hi": "Hindi",
    "id": "Bahasa Indonesia",
    "ja": "Japanese",
    "km": "Khmer",
    "lo": "Lao",
    "ms": "Malay",
    "my": "Myanmar (Burmese)",
    "th": "Thai",
    "vi": "Vietnamese",
    "zh": "Chinese (Simplified)"
}

@app.route('/')
def index():
    return render_template('index.html', languages=SUPPORTED_LANGUAGES)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/translate', methods=['POST'])
def translate():
    try:
        # Get text and target language from the request
        data = request.json
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'ja')
        use_mbart = data.get('use_mbart', False)  # Default to legacy model if not specified
        
        # Check if input is valid
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({'error': f'Language {target_lang} is not supported'}), 400
        
        # Try using mBART model first if requested and available
        if use_mbart and HAS_MBART:
            try:
                global mbart_translator
                if mbart_translator is None:
                    logger.debug("Initializing mBART translator...")
                    mbart_translator = get_translator()
                
                if mbart_translator.is_model_loaded():
                    logger.debug(f"Using mBART model for translation to {target_lang}")
                    translated_text = mbart_translator.translate(text, target_lang)
                    return jsonify({'translation': translated_text, 'model': 'mbart'})
                else:
                    logger.warning("mBART model failed to load, falling back to legacy model")
            except Exception as e:
                logger.error(f"mBART translation error: {str(e)}")
                logger.warning("Falling back to legacy translation model")
        
        # Fall back to legacy model if mBART is not available or fails
        global translation_model
        if translation_model is None:
            logger.debug("Initializing legacy translation model...")
            translation_model = TranslationModel()
        
        # Translate the text using legacy model
        translated_text = translation_model.translate(text, target_lang)
        
        return jsonify({'translation': translated_text, 'model': 'legacy'})
    
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return jsonify({'error': 'An error occurred during translation. Please try again.'}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', languages=SUPPORTED_LANGUAGES), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('index.html', languages=SUPPORTED_LANGUAGES, error='Internal server error. Please try again later.'), 500
