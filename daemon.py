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
    
    CHUNK_SIZE = 50
    NO_MATCH_FOLDER = '_auto_categorization/_no_match'
    
    def __init__(self, config: AppConfig, poll_interval: int = 60, run_once: bool = False):
        self.config = config
        self.poll_interval = poll_interval
        self.run_once = run_once
        self.running = False
        self.classifier = BayesClassifier(config.db_dir)
    
    def start(self) -> None:
        """Start the daemon loop."""
        self.running = True
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        if self.run_once:
            print("Running once...")
        else:
            print(f"Daemon started, polling every {self.poll_interval}s")
        print(f"Categories: {', '.join(self.config.categories)}")
        
        while self.running:
            try:
                processed = self._process_chunk()
                if self.run_once and processed == 0:
                    break
            except Exception as e:
                print(f"Error processing inbox: {e}")
                if self.run_once:
                    break
            
            if not self.run_once:
                time.sleep(self.poll_interval)
            elif processed > 0:
                print(f"Waiting {self.poll_interval}s before next chunk...")
                time.sleep(self.poll_interval)
    
    def _process_chunk(self) -> int:
        """Fetch and classify a chunk of unseen emails. Returns count processed."""
        with ImapFetcher(self.config.imap) as fetcher:
            emails = fetcher.fetch_unseen('INBOX', limit=self.CHUNK_SIZE)
            
            if not emails:
                return 0
            
            print(f"Processing {len(emails)} email(s)...")
            
            for email in emails:
                result = self.classifier.classify(email.raw, self.config.categories)
                subject = email.subject[:40] if email.subject else '(no subject)'
                
                if result:
                    dest_folder = f"_auto_categorization/{result.category}"
                    fetcher.move_email(email.uid, dest_folder)
                    print(f"  → {result.category} ({result.score:.2f}): {subject}")
                else:
                    fetcher.move_email(email.uid, self.NO_MATCH_FOLDER)
                    print(f"  → _no_match: {subject}")
            
            return len(emails)
    
    def _handle_signal(self, signum, frame) -> None:
        print("\nShutting down...")
        self.running = False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='IMAP email auto-classifier daemon')
    parser.add_argument('--once', action='store_true', help='Process all emails once and exit')
    parser.add_argument('--interval', type=int, default=60, help='Poll interval in seconds (default: 60)')
    args = parser.parse_args()
    
    config = load_config()
    
    if not config.imap.username or not config.imap.password:
        print("Error: Set IMAP_USER and IMAP_PASS environment variables")
        sys.exit(1)
    
    daemon = FilterDaemon(config, poll_interval=args.interval, run_once=args.once)
    daemon.start()

if __name__ == '__main__':
    main()
