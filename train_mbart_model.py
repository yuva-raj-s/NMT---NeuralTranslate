#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fine-tune mBART model on the ALT dataset for Neural Machine Translation
This script trains the mBART-large-50 model using the ALT dataset
for improved translation between English and 12 Asian languages.
"""

import os
import json
import logging
import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

try:
    import torch
    from torch.utils.data import Dataset, DataLoader
    from datasets import Dataset as HFDataset
    from transformers import (
        MBart50TokenizerFast,
        MBartForConditionalGeneration,
        Seq2SeqTrainingArguments,
        Seq2SeqTrainer,
        DataCollatorForSeq2Seq
    )
except ImportError:
    print("Required packages not found. Please install with:")
    print("pip install torch transformers datasets pandas numpy scikit-learn")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mbart_training.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Language mapping for mBART model
LANG_MAP = {
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

def load_alt_dataset(data_path, source_lang='en', target_lang=None):
    """
    Load the ALT dataset from a directory containing language files
    
    Args:
        data_path: Path to directory containing language files
        source_lang: Source language code (default: 'en')
        target_lang: Target language code (if None, all languages will be loaded)
        
    Returns:
        DataFrame with parallel texts
    """
    logger.info(f"Loading ALT dataset from {data_path}")
    
    # If ALT dataset is not available, create a small sample dataset
    if not os.path.exists(data_path):
        logger.warning(f"ALT dataset not found at {data_path}, creating a sample dataset")
        
        # Create a small sample dataset for demonstration
        sample_data = []
        
        # Add some sample parallel sentences for demonstration
        with open('alt_sample_data.json', 'w') as f:
            sample_data = [
                {
                    "en": "Japanese experts have predicted that petroleum prices may decrease within two years.",
                    "bn": "জাপানি বিশেষজ্ঞরা ভবিষ্যদ্বাণী করেছেন যে দুই বছরের মধ্যে পেট্রোলিয়ামের দাম কমতে পারে।",
                    "hi": "जापानी विशेषज्ञों ने भविष्यवाणी की है कि पेट्रोलियम की कीमतें दो साल के भीतर कम हो सकती हैं।",
                    "ja": "日本の専門家は、石油価格が2年以内に下がる可能性があると予測している。",
                    "zh": "日本专家预测石油价格可能在两年内下降。",
                    "th": "ผู้เชี่ยวชาญชาวญี่ปุ่นได้ทำนายว่าราคาน้ำมันอาจลดลงภายในสองปี",
                    "vi": "Các chuyên gia Nhật Bản đã dự đoán rằng giá dầu mỏ có thể giảm trong vòng hai năm."
                },
                {
                    "en": "No ships are sailing in the dangerous situation in the Bay of Bengal.",
                    "bn": "বঙ্গোপসাগরে বিপদসংকুল অবস্থায় কোন জাহাজ চলাচল করছে না।",
                    "hi": "बंगाल की खाड़ी में खतरनाक स्थिति में कोई जहाज नहीं चल रहा है।",
                    "ja": "ベンガル湾の危険な状況では、船が航行していない。",
                    "zh": "在孟加拉湾的危险情况下没有船只航行。",
                    "th": "ไม่มีเรือแล่นในสถานการณ์อันตรายในอ่าวเบงกอล",
                    "vi": "Không có tàu nào đang di chuyển trong tình huống nguy hiểm ở vịnh Bengal."
                },
                # Add more examples here
            ]
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        # Convert to DataFrame
        df = pd.DataFrame(sample_data)
        return df
        
    # If it's a real dataset, load it properly
    # Implement actual loading logic for ALT dataset
    # This would depend on the specific format of your ALT dataset
    
    # For this example, we'll assume files are named like 'en.txt', 'ja.txt', etc.
    langs = [source_lang]
    if target_lang:
        langs.append(target_lang)
    else:
        langs.extend([lang for lang in LANG_MAP.keys() if lang != source_lang])
    
    # Load each language file
    data = {}
    for lang in langs:
        file_path = os.path.join(data_path, f"{lang}.txt")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data[lang] = f.readlines()
    
    # Create DataFrame
    df_data = {}
    for lang in data:
        df_data[lang] = [line.strip() for line in data[lang]]
    
    df = pd.DataFrame(df_data)
    return df

def prepare_dataset(df, source_lang='en', target_lang='ja', max_examples=5000):
    """
    Prepare the dataset for fine-tuning
    
    Args:
        df: DataFrame with parallel texts
        source_lang: Source language code
        target_lang: Target language code
        max_examples: Maximum number of examples to use
    
    Returns:
        HuggingFace Dataset for training
    """
    logger.info(f"Preparing dataset for fine-tuning ({source_lang} to {target_lang})")
    
    # Filter rows where both languages have valid text
    valid_rows = df[[source_lang, target_lang]].dropna()
    
    # Prepare training data
    train_data = []
    for _, row in valid_rows.iterrows():
        if pd.notna(row[source_lang]) and pd.notna(row[target_lang]):
            train_data.append({
                'source': row[source_lang],
                'target': row[target_lang],
                'source_lang': LANG_MAP[source_lang],
                'target_lang': LANG_MAP[target_lang]
            })
    
    # Limit dataset size if needed
    if len(train_data) > max_examples:
        logger.info(f"Limiting dataset to {max_examples} examples (from {len(train_data)})")
        import random
        random.shuffle(train_data)
        train_data = train_data[:max_examples]
    
    # Convert to HuggingFace Dataset
    train_dataset = HFDataset.from_pandas(pd.DataFrame(train_data))
    return train_dataset

def finetune_mbart(dataset, source_lang='en', target_lang='ja', 
                   output_dir='./mbart-finetuned', epochs=3):
    """
    Fine-tune mBART model
    
    Args:
        dataset: HuggingFace Dataset for training
        source_lang: Source language code
        target_lang: Target language code
        output_dir: Directory to save the model
        epochs: Number of training epochs
    """
    logger.info(f"Fine-tuning mBART model ({source_lang} to {target_lang})")
    
    # Load mBART model and tokenizer
    model_checkpoint = "facebook/mbart-large-50-many-to-many-mmt"
    tokenizer = MBart50TokenizerFast.from_pretrained(model_checkpoint)
    model = MBartForConditionalGeneration.from_pretrained(model_checkpoint)
    
    # Set source language for tokenizer
    tokenizer.src_lang = LANG_MAP[source_lang]
    
    # Preprocessing function
    def preprocess_function(examples):
        source_texts = examples['source']
        target_texts = examples['target']
        
        # Tokenize inputs
        model_inputs = tokenizer(source_texts, max_length=128, truncation=True, padding="max_length")
        
        # Tokenize targets
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(target_texts, max_length=128, truncation=True, padding="max_length")
        
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs
    
    # Preprocess the dataset
    tokenized_dataset = dataset.map(preprocess_function, batched=True)
    
    # Split into train and validation sets
    train_val_dict = tokenized_dataset.train_test_split(test_size=0.1)
    
    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
    
    # Training arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        weight_decay=0.01,
        save_total_limit=3,
        num_train_epochs=epochs,
        predict_with_generate=True,
        fp16=True if torch.cuda.is_available() else False,
        push_to_hub=False,
        report_to=["none"],
    )
    
    # Initialize trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_val_dict["train"],
        eval_dataset=train_val_dict["test"],
        tokenizer=tokenizer,
        data_collator=data_collator,
    )
    
    # Train the model
    logger.info("Starting training...")
    trainer.train()
    
    # Save the fine-tuned model
    logger.info(f"Saving fine-tuned model to {output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    logger.info("Fine-tuning completed successfully")
    return model, tokenizer

def test_translation(model, tokenizer, source_text, source_lang='en', target_lang='ja'):
    """
    Test the fine-tuned model by translating a text
    
    Args:
        model: Fine-tuned mBART model
        tokenizer: mBART tokenizer
        source_text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        Translated text
    """
    # Set the source language
    tokenizer.src_lang = LANG_MAP[source_lang]
    
    # Tokenize the text
    inputs = tokenizer(source_text, return_tensors="pt")
    
    # Generate translation
    translated_tokens = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.lang_code_to_id[LANG_MAP[target_lang]],
        max_length=128
    )
    
    # Decode the tokens
    translation = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
    
    return translation

def main():
    """Main function to run the fine-tuning process"""
    parser = argparse.ArgumentParser(description="Fine-tune mBART model on ALT dataset")
    parser.add_argument("--data_path", type=str, default="./alt_dataset", 
                        help="Path to ALT dataset directory")
    parser.add_argument("--source_lang", type=str, default="en", 
                        help="Source language code")
    parser.add_argument("--target_lang", type=str, default="ja", 
                        help="Target language code")
    parser.add_argument("--output_dir", type=str, default="./mbart-finetuned", 
                        help="Directory to save the fine-tuned model")
    parser.add_argument("--max_examples", type=int, default=5000, 
                        help="Maximum number of examples to use for training")
    parser.add_argument("--epochs", type=int, default=3, 
                        help="Number of training epochs")
    args = parser.parse_args()

    # Check if CUDA is available
    if torch.cuda.is_available():
        logger.info("CUDA is available, using GPU for training")
    else:
        logger.warning("CUDA is not available, using CPU for training (may be very slow)")
    
    # Load ALT dataset
    df = load_alt_dataset(args.data_path, args.source_lang, args.target_lang)
    logger.info(f"Loaded dataset with {len(df)} examples")
    
    # Prepare dataset for fine-tuning
    dataset = prepare_dataset(df, args.source_lang, args.target_lang, args.max_examples)
    
    # Fine-tune the model
    model, tokenizer = finetune_mbart(
        dataset, 
        args.source_lang, 
        args.target_lang, 
        args.output_dir,
        args.epochs
    )
    
    # Test the model with a few examples
    test_examples = [
        "Hello world, how are you doing today?",
        "This is a neural machine translation system.",
        "Can you help me translate this document?"
    ]
    
    logger.info(f"\nTesting translations ({args.source_lang} to {args.target_lang}):")
    for example in test_examples:
        translation = test_translation(model, tokenizer, example, 
                                       args.source_lang, args.target_lang)
        logger.info(f"Source: {example}")
        logger.info(f"Translation: {translation}\n")

if __name__ == "__main__":
    main()