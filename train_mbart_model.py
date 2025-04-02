import os
import re
import pandas as pd
import torch
from transformers import (
    MBart50TokenizerFast,
    MBartForConditionalGeneration,
    TrainingArguments,
    Trainer
)
from datasets import Dataset

# Define available languages and their mBART-50 language codes
lang_map = {
    'en': 'en_XX',
    'hi': 'hi_IN',
    'ja': 'ja_XX',
    'ko': 'ko_KR',
    'zh': 'zh_CN',
    'th': 'th_TH',
    'vi': 'vi_VN',
    'id': 'id_ID',
    'ms': 'ms_MY',
    'bn': 'bn_IN',
    'fil': 'tl_XX',
    'km': 'km_KH',
    'lo': 'lo_LA',
    'my': 'my_MM',
}

# Get only the languages supported by mBART-50
languages = list(lang_map.keys())
print("Languages supported by mBART-50:", languages)

def process_alt_dataset(dataset):
    """Cleans and prepares the ALT dataset for fine-tuning."""
    print("Cleaning data...")
    data = {lang: [] for lang in languages}
    for entry in dataset['train']:
        if isinstance(entry['translation'], dict):
            entry_data = {}
            for lang in languages:
                if lang in entry['translation'] and isinstance(entry['translation'][lang], str):
                    entry_data[lang] = entry['translation'][lang]
            if 'en' in entry_data and len(entry_data) > 1:
                for lang in languages:
                    data[lang].append(entry_data.get(lang, None))

    df = pd.DataFrame(data)

    def clean_text(text):
        if not isinstance(text, str):
            return None
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'<.*?>', '', text)
        return text if text else None

    for lang in df.columns:
        df[lang] = df[lang].apply(clean_text)

    df.drop_duplicates(inplace=True)
    df.dropna(how='all', inplace=True)
    df.dropna(subset=['en'], inplace=True)

    # Save cleaned dataset
    output_path = "./processed_data"
    os.makedirs(output_path, exist_ok=True)
    cleaned_data_path = os.path.join(output_path, 'alt_cleaned_data.csv')
    df.to_csv(cleaned_data_path, index=False, encoding="utf-8")
    print(f"✅ Cleaned dataset saved at {cleaned_data_path}")

    # Prepare dataset for fine-tuning in the correct format - focusing on English to Hindi for simplicity
    print("Preparing training data...")
    train_data = []
    for _, row in df.iterrows():
        if pd.notna(row['en']) and pd.notna(row['hi']):  # Focus on English to Hindi
            train_data.append({
                'source': row['en'],
                'target': row['hi'],
                'source_lang': lang_map['en'],
                'target_lang': lang_map['hi']
            })

    # Limit the dataset size to avoid memory issues
    MAX_EXAMPLES = 5000  # Reduced for faster processing
    if len(train_data) > MAX_EXAMPLES:
        print(f"Limiting dataset to {MAX_EXAMPLES} examples (from {len(train_data)})")
        import random
        random.shuffle(train_data)
        train_data = train_data[:MAX_EXAMPLES]

    # Convert to Hugging Face dataset format
    train_dataset = Dataset.from_pandas(pd.DataFrame(train_data))
    return train_dataset

def finetune_mbart(train_dataset):
    """Fine-tunes the mBART model."""
    print("Loading pre-trained model...")
    MODEL_CHECKPOINT = "facebook/mbart-large-50-many-to-many-mmt"
    tokenizer = MBart50TokenizerFast.from_pretrained(MODEL_CHECKPOINT)

    # Set source language to English
    tokenizer.src_lang = lang_map['en']

    def process_single_example(example):
        """Process a single example without batching to avoid language code issues"""
        source = example['source']
        target = example['target']

        # Tokenize inputs with explicit source language
        source_tokens = tokenizer(
            source,
            max_length=128,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )

        # Tokenize targets with explicit target language
        target_tokens = tokenizer(
            target,
            max_length=128,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )

        # Create inputs
        model_inputs = {
            "input_ids": source_tokens["input_ids"][0],
            "attention_mask": source_tokens["attention_mask"][0],
            "labels": target_tokens["input_ids"][0],
        }
        return model_inputs

    # Process the dataset
    print("Tokenizing dataset...")
    tokenized_dataset = train_dataset.map(
        process_single_example,
        remove_columns=train_dataset.column_names
    )

    # Split dataset into train and validation
    tokenized_datasets = tokenized_dataset.train_test_split(test_size=0.1)

    # Initialize model
    model = MBartForConditionalGeneration.from_pretrained(MODEL_CHECKPOINT)

    # Define training arguments
    training_args = TrainingArguments(
        output_dir="./mbart-finetuned",
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        num_train_epochs=1,
        weight_decay=0.01,
        save_strategy="epoch",
        push_to_hub=False,
        logging_dir="./logs",
        logging_steps=100,
        fp16=True,
        report_to=["none"],
        run_name=None,
    )

    # Initialize trainer
    print("Initializing trainer...")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
    )

    # Train the model
    print("Starting training...")
    trainer.train()

    # Save the fine-tuned model
    print("Saving fine-tuned model...")
    model.save_pretrained("./mbart-finetuned")
    tokenizer.save_pretrained("./mbart-finetuned")
    print("✅ Fine-tuning completed and model saved!")
    return model, tokenizer

def translate_text(model, tokenizer, input_text, target_lang):
    """Translates text using the fine-tuned model."""
    tokenizer.src_lang = lang_map['en']
    inputs = tokenizer(input_text, return_tensors="pt", padding=True)
    translated_tokens = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.lang_code_to_id[lang_map[target_lang]],
        max_length=128
    )
    translation = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
    return translation

def main(dataset):
    """Main function to orchestrate the fine-tuning and translation."""
    train_dataset = process_alt_dataset(dataset)
    model, tokenizer = finetune_mbart(train_dataset)
    # Example usage of translation function
    example_text = "Hello, how are you?"
    translated_text = translate_text(model, tokenizer, example_text, 'hi') # translate to hindi
    print(f"\nExample Translation (English to Hindi):\nSource: {example_text}\nTranslation: {translated_text}")