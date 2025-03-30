import os
import logging
from flask import Flask, render_template, request, jsonify
from translation_model import TranslationModel

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Initialize the translation model
translation_model = None

# Available target languages
SUPPORTED_LANGUAGES = {
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "th": "Thai",
    "vi": "Vietnamese",
    "my": "Burmese",
    "id": "Indonesian"
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
        
        # Check if input is valid
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({'error': f'Language {target_lang} is not supported'}), 400
        
        # Initialize the model if it's not already initialized
        global translation_model
        if translation_model is None:
            logger.debug("Initializing translation model...")
            translation_model = TranslationModel()
        
        # Translate the text
        translated_text = translation_model.translate(text, target_lang)
        
        return jsonify({'translation': translated_text})
    
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
