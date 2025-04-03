#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Train mBART model with the ALT dataset.
This script simplifies the process of downloading the ALT dataset and training the mBART model.
"""

import os
import sys
import logging
import argparse
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("train_model.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import torch
        import pandas
        import numpy
        import transformers
        import datasets
        import sklearn
        import tqdm
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Please install required packages with:")
        logger.error("pip install torch transformers datasets pandas numpy scikit-learn tqdm")
        return False

def download_alt_dataset(data_dir):
    """Download and prepare the ALT dataset"""
    logger.info("Downloading and preparing ALT dataset...")
    try:
        cmd = [sys.executable, "download_alt_dataset.py", "--data_dir", data_dir]
        subprocess.run(cmd, check=True)
        logger.info("ALT dataset preparation completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error downloading ALT dataset: {e}")
        return False

def train_single_language(data_path, output_dir, target_lang, examples, epochs, batch_size):
    """Train mBART model for a specific language pair"""
    logger.info(f"Training mBART model for English to {target_lang}...")
    try:
        cmd = [
            sys.executable, 
            "train_mbart_model.py",
            "--data_path", data_path,
            "--source_lang", "en",
            "--target_lang", target_lang,
            "--output_dir", output_dir,
            "--max_examples", str(examples),
            "--epochs", str(epochs),
            "--batch_size", str(batch_size),
            "--gradient_accumulation_steps", "4"
        ]
        subprocess.run(cmd, check=True)
        logger.info(f"Training completed for English to {target_lang}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error training model: {e}")
        return False

def train_all_languages(data_path, output_dir, examples, epochs, batch_size):
    """Train mBART models for all language pairs"""
    logger.info("Training mBART models for all language pairs...")
    try:
        cmd = [
            sys.executable, 
            "train_mbart_model.py",
            "--data_path", data_path,
            "--output_dir", output_dir,
            "--max_examples", str(examples),
            "--epochs", str(epochs),
            "--batch_size", str(batch_size),
            "--all"
        ]
        subprocess.run(cmd, check=True)
        logger.info("Training completed for all language pairs")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error training models: {e}")
        return False

def main():
    """Main function to run the training process"""
    parser = argparse.ArgumentParser(description="Train mBART model with ALT dataset")
    
    parser.add_argument("--all", action="store_true", 
                       help="Train models for all language pairs")
    parser.add_argument("--download_only", action="store_true", 
                        help="Only download and prepare the ALT dataset without training")
    parser.add_argument("--data_dir", type=str, default="./datasets", 
                        help="Directory to store the ALT dataset")
    parser.add_argument("--output_dir", type=str, default="./mbart-finetuned", 
                        help="Directory to save the fine-tuned model")
    parser.add_argument("--target_lang", type=str, default=None, 
                        help="Target language code (e.g., 'ja' for Japanese). If not specified, train all languages")
    parser.add_argument("--examples", type=int, default=5000, 
                        help="Maximum number of examples to use for training")
    parser.add_argument("--epochs", type=int, default=3, 
                        help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=8, 
                        help="Batch size for training")
    
    args = parser.parse_args()
    
    # Create directories
    os.makedirs(args.data_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Check if required dependencies are installed
    if not check_dependencies():
        return
    
    # Define paths
    processed_dir = os.path.join(args.data_dir, "alt_processed")
    
    # Download and prepare ALT dataset if needed
    if not os.path.exists(os.path.join(processed_dir, "alt_parallel.csv")):
        if not download_alt_dataset(args.data_dir):
            logger.error("Failed to download and prepare ALT dataset. Aborting.")
            return
    else:
        logger.info(f"Using existing ALT dataset at {processed_dir}")
    
    if args.download_only:
        logger.info("Download only mode. Skipping training.")
        return
    
    # Train the model(s)
    if args.target_lang:
        # Train for a specific language pair
        train_single_language(
            processed_dir,
            args.output_dir,
            args.target_lang,
            args.examples,
            args.epochs,
            args.batch_size
        )
    else:
        # Train for all language pairs
        train_all_languages(
            processed_dir,
            args.output_dir,
            args.examples,
            args.epochs,
            args.batch_size
        )
    
    logger.info("Training process completed")

if __name__ == "__main__":
    main()