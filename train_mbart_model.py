#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fine-tune mBART model on the ALT dataset for Neural Machine Translation
This script trains the mBART-large-50 model using the ALT dataset
for improved translation between English and 12 Asian languages.

Enhanced version with support for all language pairs and improved training.
"""

import os
import json
import logging
import argparse
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from tqdm import tqdm

try:
    import torch
    from torch.utils.data import Dataset, DataLoader
    from datasets import Dataset as HFDataset, load_dataset
    from transformers import (
        MBart50TokenizerFast,
        MBartForConditionalGeneration,
        Seq2SeqTrainingArguments,
        Seq2SeqTrainer,
        DataCollatorForSeq2Seq,
        IntervalStrategy
    )
except ImportError:
    print("Required packages not found. Please install with:")
    print("pip install torch transformers datasets pandas numpy scikit-learn tqdm")
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
    "lo": "lo_LA",  # Lao (closest available in mBART)
    "ms": "en_XX",  # Malay (use English as fallback since not directly in mBART)
    "my": "my_MM",  # Myanmar
    "th": "th_TH",  # Thai
    "vi": "vi_VN",  # Vietnamese
    "zh": "zh_CN"   # Chinese (Simplified)
}

# Natural language names for each language code
LANG_NAMES = {
    "bn": "Bengali",
    "en": "English",
    "fil": "Filipino",
    "hi": "Hindi",
    "id": "Indonesian",
    "ja": "Japanese",
    "km": "Khmer",
    "lo": "Lao",
    "ms": "Malay",
    "my": "Myanmar",
    "th": "Thai",
    "vi": "Vietnamese",
    "zh": "Chinese"
}

def load_alt_dataset(data_path: str, source_lang: str = 'en', target_lang: Optional[str] = None):
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
    
    # Check for different possible dataset locations
    if os.path.exists(os.path.join(data_path, "alt_parallel.csv")):
        # Use the processed parallel corpus
        logger.info(f"Loading processed ALT parallel corpus")
        df = pd.read_csv(os.path.join(data_path, "alt_parallel.csv"))
        return df
    
    if target_lang and os.path.exists(os.path.join(data_path, f"{source_lang}-{target_lang}")):
        # Use specific language pair directory
        pair_dir = os.path.join(data_path, f"{source_lang}-{target_lang}")
        if os.path.exists(os.path.join(pair_dir, "train.csv")):
            logger.info(f"Loading specific language pair {source_lang}-{target_lang}")
            train_df = pd.read_csv(os.path.join(pair_dir, "train.csv"))
            return train_df
    
    # If individual language files exist
    langs = [source_lang]
    if target_lang:
        langs.append(target_lang)
    else:
        langs.extend([lang for lang in LANG_MAP.keys() if lang != source_lang])
    
    # Check if all language files exist
    all_exist = True
    for lang in langs:
        file_path = os.path.join(data_path, f"{lang}.txt")
        if not os.path.exists(file_path):
            all_exist = False
            logger.warning(f"Language file not found: {file_path}")
    
    if all_exist:
        # Load each language file
        data = {}
        for lang in langs:
            file_path = os.path.join(data_path, f"{lang}.txt")
            with open(file_path, 'r', encoding='utf-8') as f:
                data[lang] = f.readlines()
        
        # Create DataFrame
        df_data = {}
        min_lines = min(len(data[lang]) for lang in data)
        for lang in data:
            df_data[lang] = [line.strip() for line in data[lang][:min_lines]]
        
        df = pd.DataFrame(df_data)
        return df
    
    # If no valid dataset format is found, create a small sample dataset
    logger.warning(f"No valid ALT dataset found at {data_path}, creating a sample dataset")
    
    # Create a small sample dataset for demonstration
    sample_data = [
        {
            "en": "Japanese experts have predicted that petroleum prices may decrease within two years.",
            "bn": "জাপানি বিশেষজ্ঞরা ভবিষ্যদ্বাণী করেছেন যে দুই বছরের মধ্যে পেট্রোলিয়ামের দাম কমতে পারে।",
            "fil": "Hinulaan ng mga ekspertong Hapones na ang presyo ng petrolyo ay maaaring bumaba sa loob ng dalawang taon.",
            "hi": "जापानी विशेषज्ञों ने भविष्यवाणी की है कि पेट्रोलियम की कीमतें दो साल के भीतर कम हो सकती हैं।",
            "id": "Para ahli Jepang telah memprediksi bahwa harga minyak bumi dapat menurun dalam dua tahun.",
            "ja": "日本の専門家は、石油価格が2年以内に下がる可能性があると予測している。",
            "km": "អ្នកជំនាញជប៉ុនបានព្យាករណ៍ថាតម្លៃប្រេងអាចនឹងធ្លាក់ចុះក្នុងរយៈពេលពីរឆ្នាំ។",
            "lo": "ຜູ້ຊ່ຽວຊານຍີ່ປຸ່ນໄດ້ທໍານາຍວ່າລາຄານ້ໍາມັນອາດຈະຫຼຸດລົງພາຍໃນສອງປີ.",
            "ms": "Pakar Jepun telah meramalkan bahawa harga petroleum mungkin menurun dalam masa dua tahun.",
            "my": "ဂျပန်ကျွမ်းကျင်သူများသည် ရေနံစျေးနှုန်းများသည် နှစ်နှစ်အတွင်း လျော့ကျနိုင်သည်ဟု ခန့်မှန်းခဲ့သည်။",
            "th": "ผู้เชี่ยวชาญชาวญี่ปุ่นได้ทำนายว่าราคาน้ำมันอาจลดลงภายในสองปี",
            "vi": "Các chuyên gia Nhật Bản đã dự đoán rằng giá dầu mỏ có thể giảm trong vòng hai năm.",
            "zh": "日本专家预测石油价格可能在两年内下降。"
        },
        {
            "en": "No ships are sailing in the dangerous situation in the Bay of Bengal.",
            "bn": "বঙ্গোপসাগরে বিপদসংকুল অবস্থায় কোন জাহাজ চলাচল করছে না।",
            "fil": "Walang mga barko ang naglalayag sa mapanganib na sitwasyon sa Bay of Bengal.",
            "hi": "बंगाल की खाड़ी में खतरनाक स्थिति में कोई जहाज नहीं चल रहा है।",
            "id": "Tidak ada kapal yang berlayar dalam situasi berbahaya di Teluk Benggala.",
            "ja": "ベンガル湾の危険な状況では、船が航行していない。",
            "km": "គ្មាននាវាណាកំពុងធ្វើដំណើរក្នុងស្ថានភាពគ្រោះថ្នាក់នៅឈូងសមុទ្រឆកបេន្ឡាឡេ។",
            "lo": "ບໍ່ມີເຮືອແລ່ນໃນສະຖານະການອັນຕະລາຍຢູ່ອ່າວ Bengal.",
            "ms": "Tiada kapal yang belayar dalam situasi berbahaya di Teluk Bengal.",
            "my": "ဘင်္ဂလားပင်လယ်အော်ရှိ အန္တရာယ်ရှိသော အခြေအနေတွင် သင်္ဘောများ မရွှေ့လျားနိုင်ပါ။",
            "th": "ไม่มีเรือแล่นในสถานการณ์อันตรายในอ่าวเบงกอล",
            "vi": "Không có tàu nào đang di chuyển trong tình huống nguy hiểm ở vịnh Bengal.",
            "zh": "在孟加拉湾的危险情况下没有船只航行。"
        },
        {
            "en": "The weather forecast predicts heavy rain tomorrow in the city.",
            "bn": "আবহাওয়ার পূর্বাভাস আগামীকাল শহরে ভারী বৃষ্টির পূর্বাভাস দিচ্ছে।",
            "fil": "Inaasahan ng forecast ng panahon na malakas na ulan bukas sa lungsod.",
            "hi": "मौसम पूर्वानुमान कल शहर में भारी बारिश की भविष्यवाणी करता है।",
            "id": "Ramalan cuaca memperkirakan hujan lebat besok di kota.",
            "ja": "天気予報では、明日市内で大雨が予想されています。",
            "km": "ការព្យាករណ៍អាកាសធាតុព្យាករណ៍ថានឹងមានភ្លៀងធ្លាក់ខ្លាំងនៅថ្ងៃស្អែកនៅក្នុងទីក្រុង។",
            "lo": "ການພະຍາກອນອາກາດຄາດວ່າຈະມີຝົນຕົກໜັກໃນວັນມື້ອື່ນຢູ່ໃນເມືອງ.",
            "ms": "Ramalan cuaca meramalkan hujan lebat esok di bandar.",
            "my": "မိုးလေဝသခန့်မှန်းချက်အရ နက်ဖြန်မြို့တွင် မိုးသည်းထန်စွာရွာမည်ဟု ခန့်မှန်းထားသည်။",
            "th": "การพยากรณ์อากาศทำนายว่าจะมีฝนตกหนักในเมืองพรุ่งนี้",
            "vi": "Dự báo thời tiết dự đoán ngày mai sẽ có mưa to trong thành phố.",
            "zh": "天气预报预测明天城市将有大雨。"
        }
    ]
    
    # Create sample dataset directory and save
    os.makedirs(data_path, exist_ok=True)
    sample_path = os.path.join(data_path, "alt_sample_data.json")
    with open(sample_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    # Convert to DataFrame
    df = pd.DataFrame(sample_data)
    
    # Save as CSV for easier loading next time
    csv_path = os.path.join(data_path, "alt_parallel.csv")
    df.to_csv(csv_path, index=False)
    
    return df

def prepare_dataset(df: pd.DataFrame, source_lang: str = 'en', target_lang: str = 'ja', 
                   max_examples: int = 5000) -> HFDataset:
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

def finetune_mbart(dataset: HFDataset, source_lang: str = 'en', target_lang: str = 'ja', 
                  output_dir: str = './mbart-finetuned', epochs: int = 3, 
                  batch_size: int = 8, gradient_accumulation_steps: int = 4) -> Tuple:
    """
    Fine-tune mBART model
    
    Args:
        dataset: HuggingFace Dataset for training
        source_lang: Source language code
        target_lang: Target language code
        output_dir: Directory to save the model
        epochs: Number of training epochs
        batch_size: Batch size for training
        gradient_accumulation_steps: Number of steps to accumulate gradients
    
    Returns:
        Tuple of (model, tokenizer)
    """
    logger.info(f"Fine-tuning mBART model ({source_lang} to {target_lang})")
    
    # Create output directory for this specific language pair
    lang_pair_dir = os.path.join(output_dir, f"{source_lang}-{target_lang}")
    os.makedirs(lang_pair_dir, exist_ok=True)
    
    # Check if model already exists and if we should resume training
    resume_from_checkpoint = False
    if os.path.exists(os.path.join(lang_pair_dir, "pytorch_model.bin")):
        logger.info(f"Found existing model at {lang_pair_dir}")
        resume_from_checkpoint = True
    
    # Load mBART model and tokenizer
    model_checkpoint = "facebook/mbart-large-50-many-to-many-mmt"
    
    if resume_from_checkpoint:
        logger.info(f"Loading existing fine-tuned model from {lang_pair_dir}")
        try:
            tokenizer = MBart50TokenizerFast.from_pretrained(lang_pair_dir)
            model = MBartForConditionalGeneration.from_pretrained(lang_pair_dir)
        except Exception as e:
            logger.warning(f"Failed to load existing model, starting fresh: {e}")
            tokenizer = MBart50TokenizerFast.from_pretrained(model_checkpoint)
            model = MBartForConditionalGeneration.from_pretrained(model_checkpoint)
            resume_from_checkpoint = False
    else:
        # Load pretrained model and tokenizer
        logger.info(f"Loading pretrained mBART model")
        tokenizer = MBart50TokenizerFast.from_pretrained(model_checkpoint)
        model = MBartForConditionalGeneration.from_pretrained(model_checkpoint)
    
    # Set source language for tokenizer
    tokenizer.src_lang = LANG_MAP[source_lang]
    
    # Preprocessing function
    def preprocess_function(examples):
        source_texts = examples['source']
        target_texts = examples['target']
        
        # Tokenize inputs (with special tokens and padding/truncation)
        model_inputs = tokenizer(
            source_texts, 
            max_length=128, 
            truncation=True, 
            padding="max_length",
            return_tensors="pt"
        )
        
        # Tokenize targets
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(
                target_texts, 
                max_length=128, 
                truncation=True, 
                padding="max_length",
                return_tensors="pt"
            )
        
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs
    
    # Preprocess the dataset
    tokenized_dataset = dataset.map(
        preprocess_function, 
        batched=True,
        remove_columns=['source', 'target', 'source_lang', 'target_lang']
    )
    
    # Split into train and validation sets
    train_val_dict = tokenized_dataset.train_test_split(test_size=0.1)
    
    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
    
    # Training arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=lang_pair_dir,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=3e-5,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        weight_decay=0.01,
        save_total_limit=2,
        num_train_epochs=epochs,
        predict_with_generate=True,
        fp16=torch.cuda.is_available(),
        logging_dir=os.path.join(lang_pair_dir, "logs"),
        logging_strategy="steps",
        logging_steps=100,
        log_level="info",
        push_to_hub=False,
        report_to=["tensorboard"],
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
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
    logger.info(f"Starting training for {source_lang} to {target_lang}...")
    trainer.train(resume_from_checkpoint=resume_from_checkpoint)
    
    # Save the fine-tuned model
    logger.info(f"Saving fine-tuned model to {lang_pair_dir}")
    model.save_pretrained(lang_pair_dir)
    tokenizer.save_pretrained(lang_pair_dir)
    
    # Save model info
    model_info = {
        "source_language": source_lang,
        "target_language": target_lang,
        "source_language_name": LANG_NAMES.get(source_lang, source_lang),
        "target_language_name": LANG_NAMES.get(target_lang, target_lang),
        "training_examples": len(train_val_dict["train"]),
        "validation_examples": len(train_val_dict["test"]),
        "epochs": epochs,
        "base_model": model_checkpoint,
        "trained_on": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(os.path.join(lang_pair_dir, "model_info.json"), "w", encoding="utf-8") as f:
        json.dump(model_info, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Fine-tuning completed successfully for {source_lang} to {target_lang}")
    return model, tokenizer

def test_translation(model, tokenizer, source_text: str, source_lang: str = 'en', 
                    target_lang: str = 'ja') -> str:
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
    inputs = tokenizer(source_text, return_tensors="pt", padding=True)
    
    # Move inputs to the appropriate device if model is on GPU
    if next(model.parameters()).is_cuda:
        inputs = {k: v.cuda() for k, v in inputs.items()}
    
    # Generate translation with improved parameters
    translated_tokens = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.lang_code_to_id[LANG_MAP[target_lang]],
        max_length=128,
        num_beams=5,
        length_penalty=1.0,
        early_stopping=True,
        no_repeat_ngram_size=2
    )
    
    # Decode the tokens
    translation = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
    
    return translation

def train_all_languages(data_path: str, output_dir: str, source_lang: str = 'en', 
                       max_examples: int = 5000, epochs: int = 3, batch_size: int = 8):
    """
    Train mBART models for all language pairs
    
    Args:
        data_path: Path to ALT dataset
        output_dir: Base directory to save the fine-tuned models
        source_lang: Source language code
        max_examples: Maximum number of examples to use for each language pair
        epochs: Number of training epochs
        batch_size: Batch size for training
    """
    logger.info(f"Training mBART models for all languages from {source_lang}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all target languages (excluding the source language)
    target_languages = [lang for lang in LANG_MAP.keys() if lang != source_lang]
    
    # Load the full ALT dataset once
    df = load_alt_dataset(data_path, source_lang)
    logger.info(f"Loaded ALT dataset with {len(df)} examples")
    
    # Store successful models
    trained_models = []
    
    # Train a model for each target language
    for target_lang in target_languages:
        logger.info(f"=== Starting training for {source_lang} to {target_lang} ===")
        
        try:
            # Prepare dataset for this language pair
            dataset = prepare_dataset(df, source_lang, target_lang, max_examples)
            
            # Fine-tune the model
            model, tokenizer = finetune_mbart(
                dataset, 
                source_lang, 
                target_lang, 
                output_dir,
                epochs,
                batch_size
            )
            
            # Save model file path
            trained_models.append(f"{source_lang}-{target_lang}")
            
            # Test the model with a few examples
            test_examples = [
                "Hello world, how are you doing today?",
                "This is a neural machine translation system.",
                "Can you help me translate this document?"
            ]
            
            logger.info(f"\nTesting translations from {source_lang} to {target_lang}:")
            for example in test_examples:
                translation = test_translation(model, tokenizer, example, 
                                              source_lang, target_lang)
                logger.info(f"Source: {example}")
                logger.info(f"Translation: {translation}\n")
                
        except Exception as e:
            logger.error(f"Error training model for {target_lang}: {str(e)}")
            logger.exception(e)
            continue
    
    # Save summary of trained models
    summary = {
        "base_model": "facebook/mbart-large-50-many-to-many-mmt",
        "source_language": source_lang,
        "trained_models": trained_models,
        "max_examples": max_examples,
        "epochs": epochs,
        "completed_on": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    summary_path = os.path.join(output_dir, "training_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Training complete. Summary saved to {summary_path}")
    logger.info(f"Successfully trained models: {', '.join(trained_models)}")

def train_single_model(data_path: str, output_dir: str, source_lang: str = 'en', 
                      target_lang: str = 'ja', max_examples: int = 5000, epochs: int = 3,
                      batch_size: int = 8, gradient_accumulation_steps: int = 4):
    """
    Train a single mBART model for a specific language pair
    
    Args:
        data_path: Path to ALT dataset
        output_dir: Base directory to save the fine-tuned model
        source_lang: Source language code
        target_lang: Target language code
        max_examples: Maximum number of examples to use
        epochs: Number of training epochs
        batch_size: Batch size for training
        gradient_accumulation_steps: Number of steps to accumulate gradients
    """
    logger.info(f"Training mBART model for {source_lang} to {target_lang}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Load ALT dataset
        df = load_alt_dataset(data_path, source_lang, target_lang)
        logger.info(f"Loaded dataset with {len(df)} examples")
        
        # If there are too few examples, try to augment or log warning
        if len(df) < 100:
            logger.warning(f"Very small dataset ({len(df)} examples). Results may not be good.")
        
        # Prepare dataset for fine-tuning
        dataset = prepare_dataset(df, source_lang, target_lang, max_examples)
        
        # Fine-tune the model
        model, tokenizer = finetune_mbart(
            dataset, 
            source_lang, 
            target_lang, 
            output_dir,
            epochs,
            batch_size,
            gradient_accumulation_steps
        )
        
        # Test the model with a few examples
        test_examples = [
            "Hello world, how are you doing today?",
            "This is a neural machine translation system.",
            "Can you help me translate this document?"
        ]
        
        logger.info(f"\nTesting translations ({source_lang} to {target_lang}):")
        for example in test_examples:
            translation = test_translation(model, tokenizer, example, 
                                          source_lang, target_lang)
            logger.info(f"Source: {example}")
            logger.info(f"Translation: {translation}\n")
            
        logger.info(f"Training complete for {source_lang} to {target_lang}")
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        logger.exception(e)
        raise

def main():
    """Main function to run the fine-tuning process"""
    parser = argparse.ArgumentParser(description="Fine-tune mBART model on ALT dataset")
    parser.add_argument("--data_path", type=str, default="./datasets/alt_processed", 
                        help="Path to ALT dataset directory")
    parser.add_argument("--source_lang", type=str, default="en", 
                        help="Source language code")
    parser.add_argument("--target_lang", type=str, default=None, 
                        help="Target language code. If not specified, train all languages.")
    parser.add_argument("--output_dir", type=str, default="./mbart-finetuned", 
                        help="Directory to save the fine-tuned model")
    parser.add_argument("--max_examples", type=int, default=5000, 
                        help="Maximum number of examples to use for training")
    parser.add_argument("--epochs", type=int, default=3, 
                        help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=8, 
                        help="Batch size for training")
    parser.add_argument("--gradient_accumulation_steps", type=int, default=4, 
                        help="Number of steps to accumulate gradients")
    parser.add_argument("--all", action="store_true", 
                        help="Train models for all language pairs")
    args = parser.parse_args()

    # Check if CUDA is available
    if torch.cuda.is_available():
        logger.info("CUDA is available, using GPU for training")
        device_info = f"Device: {torch.cuda.get_device_name(0)}"
        memory_info = f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB"
        logger.info(f"{device_info}, {memory_info}")
    else:
        logger.warning("CUDA is not available, using CPU for training (may be very slow)")
    
    # Check if we're training all languages or a specific pair
    if args.all or args.target_lang is None:
        train_all_languages(
            args.data_path,
            args.output_dir,
            args.source_lang,
            args.max_examples,
            args.epochs,
            args.batch_size
        )
    else:
        train_single_model(
            args.data_path,
            args.output_dir,
            args.source_lang,
            args.target_lang,
            args.max_examples,
            args.epochs,
            args.batch_size,
            args.gradient_accumulation_steps
        )

if __name__ == "__main__":
    main()