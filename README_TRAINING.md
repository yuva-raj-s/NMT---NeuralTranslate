# mBART Training with ALT Dataset

This document provides instructions for training the mBART model with the Asian Language Treebank (ALT) dataset to improve translation quality for all supported languages.

## Prerequisites

Before training, make sure you have the following dependencies installed:

```bash
pip install torch transformers datasets pandas numpy scikit-learn tqdm
```

You'll also need to download the NLTK data for evaluation metrics:

```python
import nltk
nltk.download('punkt')
nltk.download('wordnet')
```

## Training Process

The training process consists of two main steps:

1. **Download and prepare the ALT dataset**
2. **Fine-tune the mBART model** using the prepared dataset

We've created a unified script `train_model.py` that simplifies this process, but you can also run each step individually.

### Using the Unified Training Script

To download the dataset and train models for all languages:

```bash
python train_model.py
```

To train a model for a specific language pair:

```bash
python train_model.py --target_lang ja  # For English to Japanese
```

To only download the dataset without training:

```bash
python train_model.py --download_only
```

### Advanced Options

The unified script supports several parameters:

- `--data_dir`: Directory to store the ALT dataset (default: "./datasets")
- `--output_dir`: Directory to save the fine-tuned models (default: "./mbart-finetuned")
- `--target_lang`: Target language code (e.g., 'ja' for Japanese). If not specified, train all languages
- `--examples`: Maximum number of examples to use for training (default: 5000)
- `--epochs`: Number of training epochs (default: 3)
- `--batch_size`: Batch size for training (default: 8)

### Manual Process

If you prefer to run the steps individually:

1. **Download and prepare the ALT dataset**:

```bash
python download_alt_dataset.py --data_dir ./datasets
```

2. **Train the mBART model**:

```bash
# Train for a specific language pair
python train_mbart_model.py --data_path ./datasets/alt_processed --source_lang en --target_lang ja --output_dir ./mbart-finetuned

# Train for all language pairs
python train_mbart_model.py --data_path ./datasets/alt_processed --all --output_dir ./mbart-finetuned
```

## Supported Languages

The ALT dataset and our training scripts support the following languages:

- Bengali (bn)
- English (en)
- Filipino (fil)
- Hindi (hi)
- Indonesian (id)
- Japanese (ja)
- Khmer (km)
- Lao (lo)
- Malay (ms)
- Myanmar (my)
- Thai (th)
- Vietnamese (vi)
- Chinese (zh)

## Resource Requirements

Training mBART models is computationally intensive. Here are the approximate requirements:

- **Memory**: At least 16GB RAM
- **Disk Space**: ~10GB for the model and dataset
- **GPU**: Highly recommended, but not strictly required
- **Training Time**: Several hours per language pair on a modern GPU

## Using the Trained Models

After training, the models will be saved in language-specific subdirectories under the output directory, e.g., `./mbart-finetuned/en-ja/` for the English-to-Japanese model.

The application will automatically discover and use these models for translation.