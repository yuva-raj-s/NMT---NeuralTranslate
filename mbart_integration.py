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
            tuple: (translated_text, confidence_score)
                - translated_text (str): The translated text
                - confidence_score (float): Confidence score between 0.0 and 1.0
        """
        if not self.model or not self.tokenizer:
            logger.warning("mBART model not loaded, cannot translate")
            # Return a fallback translation with very low confidence
            if target_lang == 'ja':
                return "翻訳モデルが読み込まれていません", 0.2
            elif target_lang == 'zh':
                return "翻译模型未加载", 0.2
            elif target_lang == 'ko':
                return "번역 모델이 로드되지 않았습니다", 0.2
            else:
                return "Translation model not loaded", 0.2
        
        try:
            # Set the source language
            self.tokenizer.src_lang = MBART_LANG_MAP[self.source_lang]
            
            # Ensure target language is supported
            if target_lang not in MBART_LANG_MAP:
                logger.warning(f"Target language {target_lang} not supported by mBART, defaulting to Japanese")
                target_lang = 'ja'
                target_confidence_factor = 0.7  # Lower confidence for fallback language
            else:
                # Adjust confidence factor based on language support in mBART
                if MBART_LANG_MAP[target_lang] == "en_XX":  # Using English as fallback
                    target_confidence_factor = 0.7
                else:
                    target_confidence_factor = 0.9
            
            # Tokenize the text
            inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
            
            # Generate translation with beam search to get better quality and score
            translated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.lang_code_to_id[MBART_LANG_MAP[target_lang]],
                max_length=128,
                num_beams=5,  # Use beam search
                num_return_sequences=1,
                length_penalty=1.0,
                early_stopping=True,
                return_dict_in_generate=True,
                output_scores=True  # Get generation scores
            )
            
            # Decode the tokens
            translation = self.tokenizer.batch_decode(translated_tokens.sequences, skip_special_tokens=True)[0]
            
            # Check if translation is empty or same as input (indicating a failure)
            if not translation or translation.strip() == text.strip():
                logger.warning(f"mBART produced invalid translation for '{text}'")
                # Return a fallback translation with low confidence
                if target_lang == 'ja':
                    return "翻訳エラー。もう一度お試しください。", 0.3
                elif target_lang == 'zh':
                    return "翻译错误。请再试一次。", 0.3
                elif target_lang == 'hi':
                    return "अनुवाद त्रुटि। कृपया पुनः प्रयास करें।", 0.3
                else:
                    return "Translation error. Please try again.", 0.3
            
            # Calculate confidence score based on the model's output scores
            # Higher scores indicate higher confidence
            try:
                # Extract raw scores from the model output
                if hasattr(translated_tokens, "sequences_scores"):
                    # Get the sequence score (log probability)
                    log_prob = translated_tokens.sequences_scores[0].item()
                    
                    # Convert log probability to a confidence score between 0 and 1
                    # log_prob is negative, with values closer to 0 indicating higher confidence
                    # Map typical range of log_prob (-10 to 0) to confidence range (0.5 to 0.98)
                    raw_confidence = 0.5 + min(0.48, max(0, (10 + log_prob) / 20))
                    
                    # Adjust for text length (longer texts are harder to translate well)
                    length_factor = max(0.8, min(1.0, 100 / max(len(text), 10)))
                    
                    # Apply language and length factors
                    confidence_score = raw_confidence * target_confidence_factor * length_factor
                    
                    # Ensure confidence is within reasonable bounds
                    confidence_score = max(0.4, min(0.98, confidence_score))
                else:
                    # Fallback if scores not available
                    # Base confidence on target language and text length
                    text_length_factor = max(0.7, min(1.0, 200 / max(len(text), 10)))
                    confidence_score = 0.75 * target_confidence_factor * text_length_factor
            except Exception as score_err:
                logger.warning(f"Error calculating confidence score: {str(score_err)}")
                confidence_score = 0.7 * target_confidence_factor  # Default fallback
            
            return translation, confidence_score
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            # Return a language-specific error message with very low confidence
            if target_lang == 'ja':
                return f"翻訳エラー: {str(e)}", 0.1
            elif target_lang == 'zh':
                return f"翻译错误: {str(e)}", 0.1
            else:
                return f"Translation error: {str(e)}", 0.1
    
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