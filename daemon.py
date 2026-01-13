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
    
    NO_MATCH_FOLDER = '_auto_categorization/_no_match'
    
    def __init__(self, config: AppConfig, poll_interval: int = 60, run_once: bool = False, chunk_size: int = 50, process_all: bool = False):
        self.config = config
        self.poll_interval = poll_interval
        self.run_once = run_once
        self.chunk_size = chunk_size
        self.process_all = process_all
        self.running = False
        self.classifier = BayesClassifier(config.db_dir)
    
    def start(self) -> None:
        """Start the daemon loop."""
        self.running = True
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
        mode = "all" if self.process_all else "unseen"
        if self.run_once:
            print(f"Running once (mode={mode}, chunk_size={self.chunk_size}, interval={self.poll_interval}s)...")
        else:
            print(f"Daemon started (mode={mode}, chunk_size={self.chunk_size}, interval={self.poll_interval}s)")
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
        """Fetch and classify a chunk of emails. Returns count processed."""
        with ImapFetcher(self.config.imap) as fetcher:
            if self.process_all:
                emails = fetcher.fetch_from_folder('INBOX', limit=self.chunk_size, readonly=False)
            else:
                emails = fetcher.fetch_unseen('INBOX', limit=self.chunk_size)
            
            if not emails:
                msg = "No emails in INBOX" if self.process_all else "No unseen emails in INBOX"
                print(msg)
                return 0
            
            print(f"Processing {len(emails)} email(s)...")
            
            for email in emails:
                subject = email.subject[:50] if email.subject else '(no subject)'
                sender = email.sender[:30] if email.sender else '(unknown)'
                
                all_scores = self.classifier.classify_all(email.raw, self.config.categories)
                result = self.classifier.classify(email.raw, self.config.categories)
                
                scores_str = ', '.join(f"{r.category}={r.score:.2f}" for r in all_scores[:3])
                print(f"\n  [{email.uid}] {sender}")
                print(f"    Subject: {subject}")
                print(f"    Scores: {scores_str}")
                
                if result:
                    dest_folder = f"_auto_categorization/{result.category}"
                    fetcher.move_email(email.uid, dest_folder)
                    print(f"    Decision: MATCH → {result.category} (score={result.score:.2f})")
                    print(f"    Action: MOVE to {dest_folder}")
                else:
                    fetcher.move_email(email.uid, self.NO_MATCH_FOLDER)
                    print(f"    Decision: NO MATCH (threshold={self.classifier.threshold})")
                    print(f"    Action: MOVE to {self.NO_MATCH_FOLDER}")
            
            return len(emails)
    
    def _handle_signal(self, signum, frame) -> None:
        print("\nShutting down...")
        self.running = False
        sys.exit(0)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='IMAP email auto-classifier daemon')
    parser.add_argument('--once', action='store_true', help='Process emails and exit')
    parser.add_argument('--all', action='store_true', help='Process all emails (not just unseen)')
    parser.add_argument('--interval', type=int, default=60, help='Poll interval in seconds (default: 60)')
    parser.add_argument('--chunk-size', type=int, default=50, help='Emails per chunk (default: 50)')
    args = parser.parse_args()
    
    config = load_config()
    
    if not config.imap.username or not config.imap.password:
        print("Error: Set IMAP_USER and IMAP_PASS environment variables")
        sys.exit(1)
    
    daemon = FilterDaemon(
        config,
        poll_interval=args.interval,
        run_once=args.once,
        chunk_size=args.chunk_size,
        process_all=args.all,
    )
    daemon.start()

if __name__ == '__main__':
    main()
