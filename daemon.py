#!/usr/bin/env python3
"""
Daemon that monitors INBOX and auto-classifies new emails.
"""

import time
import signal
import sys
from pathlib import Path

from config import load_config, AppConfig
from imap_client import ImapFetcher
from classifier import BayesClassifier

class FilterDaemon:
    """Background service to auto-classify incoming emails."""
    
    def __init__(self, config: AppConfig, poll_interval: int = 60):
        self.config = config
        self.poll_interval = poll_interval
        self.running = False
        self.classifier = BayesClassifier(config.db_dir)
    
    def start(self) -> None:
        """Start the daemon loop."""
        self.running = True
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        print(f"Daemon started, polling every {self.poll_interval}s")
        print(f"Categories: {', '.join(self.config.categories)}")
        
        while self.running:
            try:
                self._process_inbox()
            except Exception as e:
                print(f"Error processing inbox: {e}")
            
            time.sleep(self.poll_interval)
    
    def _process_inbox(self) -> None:
        """Fetch and classify unseen emails."""
        with ImapFetcher(self.config.imap) as fetcher:
            emails = fetcher.fetch_unseen('INBOX')
            
            if not emails:
                return
            
            print(f"Processing {len(emails)} new email(s)")
            
            for email in emails:
                result = self.classifier.classify(email.raw, self.config.categories)
                
                if result:
                    dest_folder = f"_auto_categorization/{result.category}"
                    fetcher.move_email(email.uid, dest_folder)
                    print(f"  Moved '{email.subject[:40]}...' → {result.category} ({result.score:.2f})")
                else:
                    print(f"  No match for '{email.subject[:40]}...'")
    
    def _handle_signal(self, signum, frame) -> None:
        print("\nShutting down...")
        self.running = False

def main():
    config = load_config()
    
    if not config.imap.username or not config.imap.password:
        print("Error: Set IMAP_USER and IMAP_PASS environment variables")
        sys.exit(1)
    
    daemon = FilterDaemon(config)
    daemon.start()

if __name__ == '__main__':
    main()
