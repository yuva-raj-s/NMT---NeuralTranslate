#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Download and prepare the Asian Language Treebank (ALT) dataset for mBART fine-tuning.
This script downloads the ALT dataset and structures it for use with the mBART model training.
"""

import os
import requests
import tarfile
import logging
import argparse
from tqdm import tqdm
import pandas as pd
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("alt_dataset_download.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ALT dataset URLs
ALT_DATA_URLS = {
    'main': 'https://www2.nict.go.jp/astrec-att/member/mutiyama/ALT/ALT-Parallel-Corpus-20191206.tar.gz',
    'backup': 'https://www2.nict.go.jp/astrec-att/member/mutiyama/ALT/ALT-Parallel-Corpus-20190422.tar.gz'
}

# Language codes in ALT dataset
ALT_LANGUAGES = {
    'en': 'English',
    'bn': 'Bengali',
    'fil': 'Filipino',
    'hi': 'Hindi',
    'id': 'Indonesian',
    'ja': 'Japanese',
    'km': 'Khmer',
    'lo': 'Lao',
    'ms': 'Malay',
    'my': 'Myanmar',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'zh': 'Chinese'
}

def download_file(url, dest_path):
    """
    Download a file from a URL and save it to the specified path, showing a progress bar.
    
    Args:
        url: URL to download
        dest_path: Destination path to save the file
    """
    logger.info(f"Downloading from {url} to {dest_path}")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # Download the file with progress bar
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(dest_path, 'wb') as file, tqdm(
        desc=os.path.basename(dest_path),
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)
    
    logger.info(f"Download complete: {dest_path}")

def extract_tarfile(tar_path, extract_path):
    """
    Extract a tar file to the specified path.
    
    Args:
        tar_path: Path to the tar file
        extract_path: Path to extract the files to
    """
    logger.info(f"Extracting {tar_path} to {extract_path}")
    
    # Create extraction directory if it doesn't exist
    os.makedirs(extract_path, exist_ok=True)
    
    # Extract the tar file
    with tarfile.open(tar_path) as tar:
        # Use a progress bar for extraction
        members = tar.getmembers()
        with tqdm(total=len(members), desc="Extracting") as pbar:
            for member in members:
                tar.extract(member, path=extract_path)
                pbar.update(1)
    
    logger.info(f"Extraction complete: {extract_path}")

def find_alt_files(extract_path):
    """
    Find and organize ALT dataset files by language.
    
    Args:
        extract_path: Path where ALT dataset was extracted
    
    Returns:
        Dictionary with paths to files for each language
    """
    logger.info(f"Searching for ALT dataset files in {extract_path}")
    
    # Search for ALT dataset directories
    alt_data_dirs = []
    for root, dirs, files in os.walk(extract_path):
        if 'ALT-Parallel-Corpus' in root and any('data' in d for d in dirs):
            alt_data_dirs.append(root)
    
    if not alt_data_dirs:
        logger.error(f"Could not find ALT data directories in {extract_path}")
        return None
    
    # Find the most recent version
    alt_data_dir = sorted(alt_data_dirs)[-1]
    logger.info(f"Using ALT dataset directory: {alt_data_dir}")
    
    # Find language files by extension
    lang_files = {}
    for lang_code in ALT_LANGUAGES.keys():
        # Different extension conventions in ALT dataset
        extensions = [f'.{lang_code}', f'.{lang_code.upper()}']
        found = False
        
        for root, dirs, files in os.walk(os.path.join(alt_data_dir, 'data')):
            for ext in extensions:
                matching_files = [f for f in files if f.endswith(ext)]
                if matching_files:
                    # Take the largest file (likely the main corpus)
                    largest_file = max(matching_files, key=lambda f: os.path.getsize(os.path.join(root, f)))
                    lang_files[lang_code] = os.path.join(root, largest_file)
                    logger.info(f"Found {lang_code} file: {lang_files[lang_code]}")
                    found = True
                    break
            if found:
                break
    
    missing_langs = [lang for lang in ALT_LANGUAGES.keys() if lang not in lang_files]
    if missing_langs:
        logger.warning(f"Could not find files for languages: {', '.join(missing_langs)}")
    
    return lang_files

def create_parallel_corpus(lang_files, output_dir):
    """
    Create a parallel corpus from the ALT dataset files.
    
    Args:
        lang_files: Dictionary with paths to files for each language
        output_dir: Directory to write the processed files to
    
    Returns:
        Path to the directory with processed files
    """
    logger.info(f"Creating parallel corpus in {output_dir}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read all files and align them
    lang_data = {}
    line_counts = []
    
    # First, read all files and get line counts
    for lang, file_path in lang_files.items():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
            lang_data[lang] = [line.strip() for line in content]
            line_counts.append(len(content))
    
    # Check if line counts match
    if len(set(line_counts)) > 1:
        logger.warning(f"Line count mismatch across language files: {line_counts}")
        # Use the minimum line count for alignment
        min_lines = min(line_counts)
        for lang in lang_data:
            lang_data[lang] = lang_data[lang][:min_lines]
        logger.info(f"Truncated all files to {min_lines} lines")
    
    # Create a pandas DataFrame for the parallel corpus
    df = pd.DataFrame(lang_data)
    
    # Save as individual language files in the format needed for training
    for lang in lang_data:
        output_file = os.path.join(output_dir, f"{lang}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lang_data[lang]))
        logger.info(f"Wrote {len(lang_data[lang])} lines to {output_file}")
    
    # Save as a JSON-Lines file for easier processing
    jsonl_path = os.path.join(output_dir, "alt_parallel.jsonl")
    with open(jsonl_path, 'w', encoding='utf-8') as f:
        for i in range(len(df)):
            row = df.iloc[i].to_dict()
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    logger.info(f"Wrote {len(df)} lines to {jsonl_path}")
    
    # Also save as a single CSV file
    csv_path = os.path.join(output_dir, "alt_parallel.csv")
    df.to_csv(csv_path, index=False)
    logger.info(f"Wrote parallel corpus to {csv_path}")
    
    # Create a small sample for quick testing
    sample_size = min(1000, len(df))
    sample_df = df.sample(sample_size, random_state=42)
    sample_path = os.path.join(output_dir, "alt_sample.csv")
    sample_df.to_csv(sample_path, index=False)
    logger.info(f"Wrote sample corpus ({sample_size} lines) to {sample_path}")
    
    return output_dir

def create_language_pairs(parallel_dir, output_dir, source_lang='en'):
    """
    Create language pair datasets for training mBART models.
    
    Args:
        parallel_dir: Directory with the parallel corpus
        output_dir: Directory to write the language pair datasets to
        source_lang: Source language code
    """
    logger.info(f"Creating language pair datasets in {output_dir}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the parallel corpus
    csv_path = os.path.join(parallel_dir, "alt_parallel.csv")
    df = pd.read_csv(csv_path)
    
    # Create language pair datasets
    for target_lang in [l for l in ALT_LANGUAGES.keys() if l != source_lang]:
        pair_dir = os.path.join(output_dir, f"{source_lang}-{target_lang}")
        os.makedirs(pair_dir, exist_ok=True)
        
        # Create train and validation splits
        from sklearn.model_selection import train_test_split
        train_df, valid_df = train_test_split(
            df[[source_lang, target_lang]].dropna(),
            test_size=0.1,
            random_state=42
        )
        
        # Save train and validation sets
        train_df.to_csv(os.path.join(pair_dir, "train.csv"), index=False)
        valid_df.to_csv(os.path.join(pair_dir, "valid.csv"), index=False)
        
        # Also save as text files for easier use with HuggingFace datasets
        with open(os.path.join(pair_dir, f"train.{source_lang}"), 'w', encoding='utf-8') as f:
            f.write('\n'.join(train_df[source_lang].tolist()))
        with open(os.path.join(pair_dir, f"train.{target_lang}"), 'w', encoding='utf-8') as f:
            f.write('\n'.join(train_df[target_lang].tolist()))
        with open(os.path.join(pair_dir, f"valid.{source_lang}"), 'w', encoding='utf-8') as f:
            f.write('\n'.join(valid_df[source_lang].tolist()))
        with open(os.path.join(pair_dir, f"valid.{target_lang}"), 'w', encoding='utf-8') as f:
            f.write('\n'.join(valid_df[target_lang].tolist()))
        
        logger.info(f"Created language pair dataset {source_lang}-{target_lang} with "
                   f"{len(train_df)} training examples and {len(valid_df)} validation examples")

def main():
    """Main function to download and prepare the ALT dataset"""
    parser = argparse.ArgumentParser(description="Download and prepare the ALT dataset")
    parser.add_argument("--data_dir", type=str, default="./datasets", 
                        help="Directory to store the dataset")
    args = parser.parse_args()
    
    # Create base directories
    base_dir = args.data_dir
    download_dir = os.path.join(base_dir, "downloads")
    extract_dir = os.path.join(base_dir, "extracted")
    processed_dir = os.path.join(base_dir, "alt_processed")
    pairs_dir = os.path.join(base_dir, "alt_pairs")
    
    os.makedirs(base_dir, exist_ok=True)
    
    # Download the dataset
    tar_path = os.path.join(download_dir, "alt_dataset.tar.gz")
    if not os.path.exists(tar_path):
        try:
            download_file(ALT_DATA_URLS['main'], tar_path)
        except Exception as e:
            logger.warning(f"Failed to download from main URL: {e}")
            logger.info("Trying backup URL...")
            download_file(ALT_DATA_URLS['backup'], tar_path)
    else:
        logger.info(f"Using existing download: {tar_path}")
    
    # Extract the dataset
    if not os.path.exists(extract_dir) or not os.listdir(extract_dir):
        extract_tarfile(tar_path, extract_dir)
    else:
        logger.info(f"Using existing extracted files in {extract_dir}")
    
    # Find and organize ALT dataset files
    lang_files = find_alt_files(extract_dir)
    if not lang_files:
        logger.error("Failed to find ALT dataset files")
        return
    
    # Create a parallel corpus
    parallel_dir = create_parallel_corpus(lang_files, processed_dir)
    
    # Create language pair datasets
    create_language_pairs(parallel_dir, pairs_dir)
    
    logger.info(f"ALT dataset preparation complete. Files are in {base_dir}")
    logger.info(f"To train mBART models, use the language pair datasets in {pairs_dir}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Error in ALT dataset preparation: {e}")