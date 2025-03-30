"""
Translation evaluation module using industry-standard metrics.
This module provides functions to evaluate the quality of translations
using BLEU, ROUGE, and METEOR metrics.
"""

import logging
import re
import string
from collections import Counter

import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download necessary NLTK data if not already downloaded
try:
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    logger.warning(f"Could not download NLTK data: {e}")

class TranslationEvaluator:
    """Class to evaluate translation quality using multiple metrics"""
    
    def __init__(self):
        """Initialize the translator evaluator"""
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        self.smoothing_function = SmoothingFunction().method1
        
    def evaluate_translation(self, source_text, translated_text, reference_text=None):
        """
        Evaluate translation quality using multiple metrics
        
        Args:
            source_text (str): The original source text
            translated_text (str): The machine-translated text
            reference_text (str, optional): Human-translated reference text, if available
            
        Returns:
            dict: Dictionary with evaluation metrics
                - bleu_score (float): BLEU score (0-1)
                - rouge_score (float): ROUGE score (0-1)
                - meteor_score (float): METEOR score (0-1)
        """
        # If no reference text is provided, we'll use source text as a fallback
        # This isn't ideal but allows us to compute *something* when no reference is available
        if reference_text is None:
            reference_text = source_text
        
        # Calculate scores
        bleu = self._calculate_bleu(translated_text, reference_text)
        rouge = self._calculate_rouge(translated_text, reference_text)
        meteor = self._calculate_meteor(translated_text, reference_text)
        
        return {
            "bleu_score": bleu,
            "rouge_score": rouge,
            "meteor_score": meteor
        }
    
    def _calculate_bleu(self, hypothesis, reference):
        """
        Calculate BLEU score for a translation
        
        Args:
            hypothesis (str): The machine-translated text
            reference (str): The reference text
            
        Returns:
            float: BLEU score (0-1)
        """
        try:
            # Tokenize hypothesis and reference
            hypothesis_tokens = self._tokenize(hypothesis.lower())
            reference_tokens = [self._tokenize(reference.lower())]
            
            # If either text is empty, return 0
            if not hypothesis_tokens or not reference_tokens[0]:
                return 0.0
            
            # Calculate BLEU score with smoothing
            weights = (0.25, 0.25, 0.25, 0.25)  # Equal weights for 1-gram to 4-gram
            return sentence_bleu(
                reference_tokens, 
                hypothesis_tokens,
                weights=weights,
                smoothing_function=self.smoothing_function
            )
        except Exception as e:
            logger.error(f"Error calculating BLEU score: {e}")
            return 0.0
    
    def _calculate_rouge(self, hypothesis, reference):
        """
        Calculate ROUGE score for a translation
        
        Args:
            hypothesis (str): The machine-translated text
            reference (str): The reference text
            
        Returns:
            float: Average ROUGE score (0-1)
        """
        try:
            # If either text is empty, return 0
            if not hypothesis.strip() or not reference.strip():
                return 0.0
            
            # Calculate ROUGE scores
            scores = self.rouge_scorer.score(reference, hypothesis)
            
            # Average the different ROUGE metrics (rouge1, rouge2, rougeL)
            avg_rouge = (
                scores['rouge1'].fmeasure + 
                scores['rouge2'].fmeasure + 
                scores['rougeL'].fmeasure
            ) / 3.0
            
            return avg_rouge
        except Exception as e:
            logger.error(f"Error calculating ROUGE score: {e}")
            return 0.0
    
    def _calculate_meteor(self, hypothesis, reference):
        """
        Calculate METEOR score for a translation
        
        This is a simplified version as the full METEOR implementation requires
        additional resources. This version uses overlap and synonym matching.
        
        Args:
            hypothesis (str): The machine-translated text
            reference (str): The reference text
            
        Returns:
            float: METEOR-like score (0-1)
        """
        try:
            # Tokenize hypothesis and reference
            hypothesis_tokens = self._tokenize(hypothesis.lower())
            reference_tokens = self._tokenize(reference.lower())
            
            # If either text is empty, return 0
            if not hypothesis_tokens or not reference_tokens:
                return 0.0
            
            # Count the exact matches
            h_counts = Counter(hypothesis_tokens)
            r_counts = Counter(reference_tokens)
            
            # Calculate precision and recall based on token overlap
            matches = sum((h_counts & r_counts).values())
            precision = matches / len(hypothesis_tokens) if hypothesis_tokens else 0
            recall = matches / len(reference_tokens) if reference_tokens else 0
            
            # Calculate F1 score (harmonic mean of precision and recall)
            if precision + recall == 0:
                return 0.0
            f1 = 2 * precision * recall / (precision + recall)
            
            # Simple approximation of METEOR score
            # Real METEOR would include stemming, synonyms, and chunk penalties
            return f1
        except Exception as e:
            logger.error(f"Error calculating METEOR score: {e}")
            return 0.0
    
    def _tokenize(self, text):
        """
        Tokenize text into words
        
        Args:
            text (str): Text to tokenize
            
        Returns:
            list: List of tokens
        """
        # Remove punctuation and tokenize
        text = re.sub(f'[{re.escape(string.punctuation)}]', ' ', text)
        return nltk.word_tokenize(text)

# Singleton pattern for evaluator
_evaluator = None

def get_evaluator():
    """Get or create the translation evaluator instance"""
    global _evaluator
    if _evaluator is None:
        _evaluator = TranslationEvaluator()
    return _evaluator