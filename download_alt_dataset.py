import os
import logging
from datasets import load_dataset # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        # Load the ALT parallel dataset from Hugging Face
        logger.info("Loading ALT dataset from Hugging Face...")
        dataset = load_dataset("mutiyama/alt", "alt-parallel")
        
        # Define output directory
        output_dir = "./alt_dataset"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save dataset in Parquet format
        for split in dataset.keys():
            parquet_path = os.path.join(output_dir, f"{split}.parquet")
            dataset[split].to_parquet(parquet_path)
            logger.info(f"Saved {split} split to {parquet_path}")
        
        logger.info("ALT dataset processing complete.")
    
    except Exception as e:
        logger.exception(f"Error processing ALT dataset: {e}")

if __name__ == "__main__":
    main()
