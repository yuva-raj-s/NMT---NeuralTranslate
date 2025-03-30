#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test mBART translation with a few examples.
This script uses the MBartTranslator to translate a few examples and displays the results.
"""

import os
import sys
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the MBartTranslator
from mbart_integration import MBartTranslator

def print_language_list(translator):
    """Print the available languages"""
    languages = translator.get_available_languages()
    
    print("\nAvailable languages:")
    print("===================")
    
    for lang in languages:
        ft_mark = "★" if lang.get('finetuned', False) else " "
        print(f"{ft_mark} {lang['code']}: {lang['name']}")
    
    print("\n★ = Fine-tuned model available")

def translate_examples(translator, target_lang, examples=None):
    """Translate example texts to the target language"""
    if examples is None:
        examples = [
            "Hello world, how are you doing today?",
            "This is a neural machine translation system.",
            "Can you help me translate this document?",
            "The weather forecast predicts heavy rain tomorrow in the city.",
            "No ships are sailing in the dangerous situation in the Bay of Bengal."
        ]
    
    source_lang = 'en'  # Always English source for now
    
    print(f"\nTranslation from {source_lang} to {target_lang}:")
    print("=" * 60)
    
    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}:")
        print(f"Source: {example}")
        
        try:
            # Translate with the mBART model
            translation, metrics = translator.translate(example, target_lang)
            
            # Print the translation and metrics
            print(f"Translation: {translation}")
            print(f"BLEU score: {metrics['bleu_score']:.2f}")
            print(f"ROUGE score: {metrics['rouge_score']:.2f}")
            print(f"METEOR score: {metrics['meteor_score']:.2f}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 60)

def main():
    """Main function to test translations"""
    parser = argparse.ArgumentParser(description="Test mBART translations")
    parser.add_argument("--target_lang", type=str, default="ja", 
                       help="Target language code (e.g., 'ja' for Japanese)")
    parser.add_argument("--model_path", type=str, default="./mbart-finetuned", 
                       help="Path to the fine-tuned models directory")
    parser.add_argument("--list_languages", action="store_true", 
                       help="List available languages and exit")
    parser.add_argument("--text", type=str, 
                       help="Custom text to translate (in English)")
    
    args = parser.parse_args()
    
    # Initialize the translator
    translator = MBartTranslator(model_base_path=args.model_path)
    
    # If requested, just list the languages and exit
    if args.list_languages:
        print_language_list(translator)
        return
    
    # Get model info
    model_info = translator.get_model_info()
    print("\nModel information:")
    print(f"- Available models: {model_info['available_models']}")
    print(f"- Loaded models: {model_info['loaded_models']}")
    print(f"- Source language: {model_info['source_language']}")
    print(f"- Using device: {model_info['device']}")
    
    # If a custom text is provided, use it as the only example
    examples = None
    if args.text:
        examples = [args.text]
    
    # Translate examples
    translate_examples(translator, args.target_lang, examples)

if __name__ == "__main__":
    main()