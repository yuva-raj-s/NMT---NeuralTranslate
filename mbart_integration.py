#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
mBART integration module for Neural Machine Translation application.
This module provides functions to load and use a fine-tuned mBART model for translation.
"""

import os
import logging
import torch

logger = logging.getLogger(__name__)

# Language mapping for mBART model
MBART_LANG_MAP = {
    "bn": "bn_IN",  # Bengali
    "en": "en_XX",  # English
    "fil": "en_XX", # Filipino (use English as fallback since not directly in mBART)
    "hi": "hi_IN",  # Hindi
    "id": "id_ID",  # Indonesian
    "ja": "ja_XX",  # Japanese
    "km": "km_KH",  # Khmer
    "lo": "lo_LA",  # Lao (mBART may not have direct support)
    "ms": "en_XX",  # Malay (use English as fallback since not directly in mBART)
    "my": "my_MM",  # Myanmar
    "th": "th_TH",  # Thai
    "vi": "vi_VN",  # Vietnamese
    "zh": "zh_CN"   # Chinese (Simplified)
}

class MBartTranslator:
    """Class to handle translation using the mBART model"""
    
    def __init__(self, model_path='./mbart-finetuned'):
        """
        Initialize the mBART translator
        
        Args:
            model_path: Path to the fine-tuned mBART model directory
        """
        self.model = None
        self.tokenizer = None
        self.model_path = model_path
        self.source_lang = 'en'
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Try loading the model
        self.load_model()
        
    def load_model(self):
        """Load the mBART model and tokenizer"""
        try:
            from transformers import MBart50TokenizerFast, MBartForConditionalGeneration
            
            if os.path.exists(self.model_path):
                logger.info(f"Loading mBART model from {self.model_path}")
                self.model = MBartForConditionalGeneration.from_pretrained(self.model_path)
                self.tokenizer = MBart50TokenizerFast.from_pretrained(self.model_path)
                
                # Move model to appropriate device
                self.model = self.model.to(self.device)
                
                # Set source language
                self.tokenizer.src_lang = MBART_LANG_MAP[self.source_lang]
                
                logger.info("mBART model loaded successfully")
                return True
            else:
                logger.warning(f"Model directory {self.model_path} does not exist. "
                              f"Using default model behavior.")
                return False
        except ImportError:
            logger.error("transformers package not installed, cannot load mBART model")
            return False
        except Exception as e:
            logger.error(f"Error loading mBART model: {str(e)}")
            return False
    
    def translate(self, text, target_lang):
        """
        Translate text using the mBART model
        
        Args:
            text: Text to translate
            target_lang: Target language code
            
        Returns:
            Translated text
        """
        if not self.model or not self.tokenizer:
            logger.warning("mBART model not loaded, cannot translate")
            return None
        
        try:
            # Set the source language
            self.tokenizer.src_lang = MBART_LANG_MAP[self.source_lang]
            
            # Ensure target language is supported
            if target_lang not in MBART_LANG_MAP:
                logger.warning(f"Target language {target_lang} not supported by mBART, defaulting to Japanese")
                target_lang = 'ja'
            
            # Tokenize the text
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
            
            # Generate translation
            translated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[MBART_LANG_MAP[target_lang]],
                max_length=128
            )
            
            # Decode the tokens
            translation = self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
            
            return translation
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return f"Translation error: {str(e)}"
    
    def is_model_loaded(self):
        """Check if the mBART model is loaded"""
        return self.model is not None and self.tokenizer is not None

# Singleton instance
mbart_translator = None

def get_translator():
    """Get or create the mBART translator instance"""
    global mbart_translator
    if mbart_translator is None:
        mbart_translator = MBartTranslator()
    return mbart_translator