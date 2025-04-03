#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Train mBART model with the ALT dataset.
This script handles downloading, processing, and fine-tuning mBART for Asian languages.
"""

import os
import sys
import re
import json
import datetime
import logging
import argparse
import traceback
from pathlib import Path
import shutil
import subprocess

import pandas as pd
import torch
from torch.optim import AdamW
from transformers import (
    MBart50TokenizerFast,
    MBartForConditionalGeneration,
    TrainingArguments,
    Trainer,
    get_linear_schedule_with_warmup
)
from datasets import load_dataset, Dataset
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from torch import optim
from torch.nn import functional as F
from tqdm import tqdm
import gc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mbart_training.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Update language mappings to include both mBART and special token mappings
LANG_TOKEN_MAPPING = {
    'en': '<en>',  # English
    'hi': '<hi>',  # Hindi
    'ja': '<ja>',  # Japanese
    'ko': '<ko>',  # Korean
    'zh': '<zh>',  # Chinese
    'th': '<th>',  # Thai
    'vi': '<vi>',  # Vietnamese
    'id': '<id>',  # Indonesian
    'ms': '<ms>',  # Malay
    'bn': '<bn>',  # Bengali
    'fil': '<fil>', # Filipino
    'km': '<km>',  # Khmer
    'lo': '<lo>',  # Lao
    'my': '<my>'   # Burmese
}

# mBART language codes
MBART_LANG_MAP = {
    'en': 'en_XX',  # English
    'hi': 'hi_IN',  # Hindi
    'ja': 'ja_XX',  # Japanese
    'ko': 'ko_KR',  # Korean
    'zh': 'zh_CN',  # Chinese
    'th': 'th_TH',  # Thai
    'vi': 'vi_VN',  # Vietnamese
    'id': 'id_ID',  # Indonesian
    'ms': 'ms_MY',  # Malay
    'bn': 'bn_IN',  # Bengali
    'fil': 'tl_XX', # Filipino
    'km': 'km_KH',  # Khmer
    'lo': 'lo_LA',  # Lao
    'my': 'my_MM',  # Burmese
}

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = {
        'torch': 'PyTorch',
        'transformers': 'Transformers',
        'datasets': 'Datasets',
        'pandas': 'Pandas',
        'numpy': 'NumPy'
    }
    
    missing = []
    for package, name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing.append(name)
    
    if missing:
        logger.error("Missing required packages: " + ", ".join(missing))
        logger.error("Please install them using:")
        logger.error("pip install torch transformers datasets pandas numpy")
        return False
    return True

def setup_directories(output_dir, source_lang, target_lang):
    """Setup necessary directories for training"""
    # Create main output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create language-specific directory
    model_dir = os.path.join(output_dir, f"{source_lang}-{target_lang}")
    os.makedirs(model_dir, exist_ok=True)
    
    # Create logs directory
    logs_dir = os.path.join(model_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    return model_dir, logs_dir

def load_alt_dataset():
    """Load ALT dataset using datasets library"""
    try:
        logger.info("Loading ALT dataset from Hugging Face...")
        dataset = load_dataset("mutiyama/alt", "alt-parallel")
        return dataset
    except Exception as e:
        logger.error(f"Error loading ALT dataset: {e}")
        return None

def process_alt_dataset(dataset, source_lang="en", target_lang="hi", max_examples=5000):
    """Process ALT dataset similar to MT5 approach"""
    logger.info(f"Processing dataset for {source_lang}-{target_lang} pair...")
    
    if dataset is None:
        logger.error("No dataset provided!")
        return None

    try:
        # Extract parallel texts for the specific language pair
        train_data = []
        for example in dataset['train']:
            if (source_lang in example['translation'] and 
                target_lang in example['translation']):
                
                source_text = example['translation'][source_lang]
                target_text = example['translation'][target_lang]
                
                # Clean texts
                source_text = f"<{source_lang}> " + re.sub(r'\s+', ' ', source_text).strip()
                target_text = f"<{target_lang}> " + re.sub(r'\s+', ' ', target_text).strip()
                
                if source_text and target_text:
                    train_data.append({
                        'source': source_text,
                        'target': target_text
                    })

        # Limit dataset size if needed
        if len(train_data) > max_examples:
            import random
            random.shuffle(train_data)
            train_data = train_data[:max_examples]

        # Convert to Dataset format
        train_dataset = Dataset.from_pandas(pd.DataFrame(train_data))
        train_test = train_dataset.train_test_split(test_size=0.1)
        
        return train_test

    except Exception as e:
        logger.error(f"Error processing dataset: {e}")
        logger.error(traceback.format_exc())
        return None

def setup_tokenizer_and_model(model_checkpoint="facebook/mbart-large-50-many-to-many-mmt"):
    """Setup tokenizer and model with special tokens"""
    tokenizer = MBart50TokenizerFast.from_pretrained(model_checkpoint)
    model = MBartForConditionalGeneration.from_pretrained(model_checkpoint)

    # Add special tokens
    special_tokens_dict = {'additional_special_tokens': list(LANG_TOKEN_MAPPING.values())}
    num_added_tokens = tokenizer.add_special_tokens(special_tokens_dict)
    logger.info(f"Added {num_added_tokens} special tokens: {list(LANG_TOKEN_MAPPING.values())}")
    
    # Resize token embeddings
    model.resize_token_embeddings(len(tokenizer))
    
    return tokenizer, model

def encode_input_str(text, target_lang, tokenizer, seq_len=128):
    """Encode input string with language token"""
    target_lang_token = LANG_TOKEN_MAPPING[target_lang]
    input_text = f"{target_lang_token} {text}"
    
    input_ids = tokenizer.encode(
        text=input_text,
        return_tensors='pt',
        padding='max_length',
        truncation=True,
        max_length=seq_len
    )
    
    return input_ids[0]

def encode_target_str(text, tokenizer, seq_len=128):
    """Encode target string"""
    token_ids = tokenizer.encode(
        text=text,
        return_tensors='pt',
        padding='max_length',
        truncation=True,
        max_length=seq_len
    )
    
    return token_ids[0]

def get_data_generator(dataset, tokenizer, batch_size=32, seq_len=128):
    """Generate batches of data"""
    dataset = dataset.shuffle()
    
    def process_batch(examples):
        inputs = []
        targets = []
        
        for source, target in zip(examples['source'], examples['target']):
            input_ids = encode_input_str(source, examples['target_lang'][0], tokenizer, seq_len)
            target_ids = encode_target_str(target, tokenizer, seq_len)
            
            inputs.append(input_ids.unsqueeze(0))
            targets.append(target_ids.unsqueeze(0))
        
        return torch.cat(inputs), torch.cat(targets)
    
    for i in range(0, len(dataset), batch_size):
        batch = dataset[i:i+batch_size]
        yield process_batch(batch)

def finetune_mbart(train_dataset, source_lang, target_lang, output_dir):
    try:
        model_dir, logs_dir = setup_directories(output_dir, source_lang, target_lang)
        
        # Setup tokenizer and model with special tokens
        tokenizer, model = setup_tokenizer_and_model()
        
        # Move model to GPU if available
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        
        logger.info(f"Using device: {device}")
        
        # Set mBART language codes
        tokenizer.src_lang = MBART_LANG_MAP[source_lang]
        tokenizer.tgt_lang = MBART_LANG_MAP[target_lang]

        # Training parameters
        n_epochs = 8
        batch_size = 16
        print_freq = 50
        checkpoint_freq = 1000
        lr = 5e-4

        # Calculate steps
        n_batches = int(np.ceil(len(train_dataset['train']) / batch_size))
        total_steps = n_epochs * n_batches
        n_warmup_steps = int(total_steps * 0.01)

        # Optimizer and scheduler
        optimizer = AdamW(model.parameters(), lr=lr)
        scheduler = get_linear_schedule_with_warmup(
            optimizer, n_warmup_steps, total_steps)

        # Training loop
        losses = []
        for epoch in range(n_epochs):
            model.train()
            data_generator = get_data_generator(
                train_dataset['train'], tokenizer, batch_size)
            
            progress_bar = tqdm(range(n_batches), 
                              desc=f"Epoch {epoch+1}/{n_epochs}")
            
            for batch_idx in progress_bar:
                try:
                    # Get batch data
                    input_ids, label_ids = next(data_generator)
                    
                    # Move tensors to device
                    input_ids = input_ids.to(device)
                    label_ids = label_ids.to(device)
                    
                    # Forward pass
                    outputs = model(
                        input_ids=input_ids,
                        labels=label_ids
                    )
                    
                    loss = outputs.loss
                    losses.append(loss.item())
                    
                    # Backward pass
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    scheduler.step()
                    
                    # Update progress
                    progress_bar.set_postfix({'loss': f"{loss.item():.3f}"})
                    
                    if (batch_idx + 1) % print_freq == 0:
                        avg_loss = np.mean(losses[-print_freq:])
                        logger.info(
                            f'Epoch: {epoch+1} | Step: {batch_idx+1} | '
                            f'Avg. loss: {avg_loss:.3f} | '
                            f'lr: {scheduler.get_last_lr()[0]}'
                        )
                    
                    # Save checkpoint
                    if (batch_idx + 1) % checkpoint_freq == 0:
                        checkpoint_path = os.path.join(
                            model_dir, f"checkpoint-{epoch+1}-{batch_idx+1}")
                        try:
                            model.save_pretrained(checkpoint_path)
                            tokenizer.save_pretrained(checkpoint_path)
                            logger.info(f"Saved checkpoint to {checkpoint_path}")
                        except Exception as e:
                            logger.error(f"Failed to save checkpoint: {e}")
                
                except Exception as e:
                    logger.error(f"Error in batch {batch_idx}: {e}")
                    continue
            
            # Save epoch checkpoint
            checkpoint_path = os.path.join(model_dir, f"checkpoint-epoch-{epoch+1}")
            try:
                model.save_pretrained(checkpoint_path)
                tokenizer.save_pretrained(checkpoint_path)
                logger.info(f"Saved epoch checkpoint to {checkpoint_path}")
            except Exception as e:
                logger.error(f"Failed to save epoch checkpoint: {e}")

        # Save final model
        logger.info(f"Starting model save to {model_dir}")
        logger.info(f"Available disk space: {shutil.disk_usage(model_dir).free / (1024**3):.2f} GB")
        
        model = model.cpu()
        model.save_pretrained(model_dir)
        
        if os.path.exists(os.path.join(model_dir, "pytorch_model.bin")):
            logger.info("Model file successfully saved and verified")
        else:
            logger.error("Model file not found after save attempt")
            
        # Save model info
        model_info = {
            "source_language": source_lang,
            "target_language": target_lang,
            "training_examples": len(train_dataset['train']),
            "validation_examples": len(train_dataset['test']),
            "epochs": n_epochs,
            "batch_size": batch_size,
            "learning_rate": lr,
            "device": str(device),
            "trained_on": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(os.path.join(model_dir, "model_info.json"), "w") as f:
            json.dump(model_info, f, indent=2)
        
        logger.info("Model and info saved successfully")
        
        # Move model back to original device
        model = model.to(device)
        
        # Clear GPU cache
        torch.cuda.empty_cache()
        gc.collect()
        
        return model, tokenizer
        
    except Exception as e:
        logger.error(f"Error in finetune_mbart: {e}")
        logger.error(traceback.format_exc())
        return None, None

def verify_model_saved(output_dir, source_lang, target_lang):
    """Verify that the model was saved correctly"""
    model_dir = os.path.join(output_dir, f"{source_lang}-{target_lang}")
    required_files = [
        "pytorch_model.bin",
        "config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "model_info.json"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(os.path.join(model_dir, file)):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing required files in {model_dir}:")
        for file in missing_files:
            logger.error(f"  - {file}")
        return False
    
    logger.info(f"Model files verified successfully in {model_dir}")
    return True

def train_all_languages(data_path, output_dir, examples, epochs, batch_size):
    """Train mBART models for all language pairs"""
    logger.info("Training mBART models for all language pairs...")
    try:
        cmd = [
            sys.executable, 
            "train_mbart_model.py",
            "--output_dir", output_dir,
            "--max_examples", str(examples),
            "--epochs", str(epochs),
            "--batch_size", str(batch_size),
            "--target_lang", None  # This will trigger all-languages training
        ]
        subprocess.run(cmd, check=True)
        logger.info("Training completed for all language pairs")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error training models: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Train mBART model with ALT dataset")
    parser.add_argument("--output_dir", default="./mbart-finetuned",
                      help="Output directory for saved models")
    parser.add_argument("--source_lang", default="en",
                      help="Source language code")
    parser.add_argument("--target_lang", default=None,
                      help="Target language code (if not specified, train all languages)")
    parser.add_argument("--max_examples", type=int, default=5000,
                      help="Maximum number of examples to use")
    parser.add_argument("--epochs", type=int, default=8,
                      help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16,
                      help="Training batch size")
    
    args = parser.parse_args()

    try:
        if args.target_lang is None:
            # Train all languages
            train_all_languages(args.max_examples, args.output_dir, args.epochs, args.batch_size)
        else:
            # Train single language pair
            if args.source_lang not in LANG_TOKEN_MAPPING or args.target_lang not in LANG_TOKEN_MAPPING:
                logger.error(f"Invalid language code. Supported languages: {list(LANG_TOKEN_MAPPING.keys())}")
                return

            # Regular training pipeline
            dataset = load_alt_dataset()
            if dataset is None:
                return

            processed_dataset = process_alt_dataset(
                dataset,
                args.source_lang,
                args.target_lang,
                args.max_examples
            )
            if processed_dataset is None:
                return

            model, tokenizer = finetune_mbart(
                processed_dataset,
                args.source_lang,
                args.target_lang,
                args.output_dir
            )

            if not verify_model_saved(args.output_dir, args.source_lang, args.target_lang):
                logger.error("Model verification failed!")
                return

            logger.info("Training completed successfully!")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        logger.error(traceback.format_exc())

def train_single_language(data_path, output_dir, target_lang, examples, epochs, batch_size):
    """Train mBART model for a specific language pair"""
    logger.info(f"Training mBART model for English to {target_lang}...")
    try:
        cmd = [
            sys.executable, 
            "train_mbart_model.py",
            "--source_lang", "en",
            "--target_lang", target_lang,
            "--output_dir", output_dir,
            "--max_examples", str(examples),
            "--epochs", str(epochs),
            "--batch_size", str(batch_size)
            # Remove --data_path and --gradient_accumulation_steps
        ]
        subprocess.run(cmd, check=True)
        logger.info(f"Training completed for English to {target_lang}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error training model: {e}")
        return False

if __name__ == "__main__":
    try:
        # Check requirements first
        if not check_requirements():
            sys.exit(1)
        
        # Run main function
        main()
    except KeyboardInterrupt:
        logger.info("\nTraining interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
