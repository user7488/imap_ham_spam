"""
Train SpamBayes classifiers per category.
"""

import subprocess
from pathlib import Path
from storage import LocalStorage

class BayesTrainer:
    """Train independent Bayesian classifiers per category."""
    
    def __init__(self, db_dir: Path, storage: LocalStorage):
        self.db_dir = db_dir
        self.storage = storage
        self.db_dir.mkdir(parents=True, exist_ok=True)
    
    def db_path(self, category: str) -> Path:
        return self.db_dir / f"{category}.db"
    
    def train_category(self, category: str, all_categories: list[str]) -> dict:
        """
        Train a classifier for a single category.
        Emails in this category are HAM, all others are SPAM.
        """
        db = self.db_path(category)
        stats = {'ham': 0, 'spam': 0}
        
        ham_folder = self.storage.category_path(category)
        ham_files = list(ham_folder.glob('*.eml'))
        
        if ham_files:
            self._run_sb_filter('--ham', ham_files, db)
            stats['ham'] = len(ham_files)
        
        for other_cat in all_categories:
            if other_cat == category:
                continue
            spam_folder = self.storage.category_path(other_cat)
            spam_files = list(spam_folder.glob('*.eml'))
            if spam_files:
                self._run_sb_filter('--spam', spam_files, db)
                stats['spam'] += len(spam_files)
        
        return stats
    
    def train_all(self, categories: list[str]) -> dict[str, dict]:
        """Train classifiers for all categories."""
        results = {}
        for category in categories:
            if self.storage.count_emails(category) > 0:
                results[category] = self.train_category(category, categories)
        return results
    
    def _run_sb_filter(self, mode: str, files: list[Path], db: Path) -> None:
        """Run sb_filter.py with given mode and files."""
        # #LATERLLM: Consider batching for large file counts
        cmd = ['sb_filter.py', mode, f'--database={db}']
        cmd.extend(str(f) for f in files)
        subprocess.run(cmd, check=True, capture_output=True)
