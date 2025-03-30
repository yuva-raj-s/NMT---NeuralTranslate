import os
import logging
from flask import Flask, render_template, request, jsonify
from mbart_integration import get_translator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Initialize the translation model
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
        
        # Check if input is valid
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if target_lang not in SUPPORTED_LANGUAGES:
            return jsonify({'error': f'Language {target_lang} is not supported'}), 400
        
        # Initialize mBART translator if not already initialized
        global mbart_translator
        if mbart_translator is None:
            logger.info("Initializing mBART translator...")
            mbart_translator = get_translator()
        
        # Translate using mBART and get evaluation metrics
        logger.debug(f"Translating text to {target_lang} using mBART model")
        translated_text, evaluation_metrics = mbart_translator.translate(text, target_lang)
        
        # Format evaluation metrics as percentages with 1 decimal place
        bleu_percentage = round(evaluation_metrics["bleu_score"] * 100, 1)
        rouge_percentage = round(evaluation_metrics["rouge_score"] * 100, 1)
        meteor_percentage = round(evaluation_metrics["meteor_score"] * 100, 1)
        
        # Calculate average score for overall quality indicator
        average_score = (evaluation_metrics["bleu_score"] + 
                         evaluation_metrics["rouge_score"] + 
                         evaluation_metrics["meteor_score"]) / 3
        quality_percentage = round(average_score * 100, 1)
        
        return jsonify({
            'translation': translated_text,
            'model': 'mbart',
            'metrics': {
                'bleu': evaluation_metrics["bleu_score"],
                'rouge': evaluation_metrics["rouge_score"],
                'meteor': evaluation_metrics["meteor_score"],
                'quality': average_score
            },
            'percentages': {
                'bleu': bleu_percentage,
                'rouge': rouge_percentage,
                'meteor': meteor_percentage,
                'quality': quality_percentage
            }
        })
    
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
