#!/usr/bin/env python3
"""
Fetch training data from IMAP folders and store locally.
"""

import sys
from config import load_config
from imap_client import ImapFetcher
from storage import LocalStorage

def main():
    config = load_config()
    
    if not config.imap.username or not config.imap.password:
        print("Error: Set IMAP_USER and IMAP_PASS environment variables")
        sys.exit(1)
    
    storage = LocalStorage(config.data_dir)
    
    with ImapFetcher(config.imap) as fetcher:
        print("Connected to IMAP server")
        
        for category in config.categories:
            folder = f"_auto_categorization/{category}"
            print(f"\nFetching from {folder}...")
            
            try:
                emails = fetcher.fetch_from_folder(folder)
                count = storage.save_emails(category, emails)
                print(f"  Saved {count} emails to {config.data_dir}/{category}/")
            except Exception as e:
                print(f"  Error: {e}")
    
    print("\nDone. Training data stored locally.")
    print("Run train.py to build classifiers.")

if __name__ == '__main__':
    main()
