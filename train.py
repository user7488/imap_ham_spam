#!/usr/bin/env python3
"""
Train SpamBayes classifiers from locally stored emails.
"""

from config import load_config
from storage import LocalStorage
from trainer import BayesTrainer

def main():
    config = load_config()
    storage = LocalStorage(config.data_dir)
    trainer = BayesTrainer(config.db_dir, storage)
    
    print("Training classifiers...")
    print(f"Data directory: {config.data_dir}")
    print(f"Database directory: {config.db_dir}")
    print()
    
    for category in config.categories:
        count = storage.count_emails(category)
        print(f"  {category}: {count} emails")
    
    print()
    
    results = trainer.train_all(config.categories)
    
    for category, stats in results.items():
        print(f"  Trained {category}: {stats['ham']} ham, {stats['spam']} spam")
    
    print("\nDone. Classifiers saved to", config.db_dir)

if __name__ == '__main__':
    main()
