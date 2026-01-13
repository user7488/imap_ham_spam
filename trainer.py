"""
Train Naive Bayes classifiers per category using scikit-learn.
"""

from pathlib import Path
from email import message_from_bytes
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from storage import LocalStorage

class BayesTrainer:
    """Train independent Bayesian classifiers per category."""
    
    def __init__(self, db_dir: Path, storage: LocalStorage):
        self.db_dir = db_dir
        self.storage = storage
        self.db_dir.mkdir(parents=True, exist_ok=True)
    
    def model_path(self, category: str) -> Path:
        return self.db_dir / f"{category}.joblib"
    
    def _extract_text(self, raw: bytes) -> str:
        """Extract text content from email."""
        msg = message_from_bytes(raw)
        parts = []
        
        parts.append(msg.get('Subject', ''))
        parts.append(msg.get('From', ''))
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        parts.append(payload.decode('utf-8', errors='ignore'))
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                parts.append(payload.decode('utf-8', errors='ignore'))
        
        return ' '.join(parts)
    
    def train_category(self, category: str, all_categories: list[str]) -> dict:
        """
        Train a classifier for a single category.
        Emails in this category are positive (1), all others are negative (0).
        """
        texts = []
        labels = []
        
        ham_emails = self.storage.load_emails(category)
        for raw in ham_emails:
            texts.append(self._extract_text(raw))
            labels.append(1)
        
        for other_cat in all_categories:
            if other_cat == category:
                continue
            spam_emails = self.storage.load_emails(other_cat)
            for raw in spam_emails:
                texts.append(self._extract_text(raw))
                labels.append(0)
        
        if not texts:
            return {'ham': 0, 'spam': 0}
        
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, stop_words='english')),
            ('clf', MultinomialNB()),
        ])
        
        pipeline.fit(texts, labels)
        joblib.dump(pipeline, self.model_path(category))
        
        return {'ham': len(ham_emails), 'spam': len(texts) - len(ham_emails)}
    
    def train_all(self, categories: list[str]) -> dict[str, dict]:
        """Train classifiers for all categories."""
        results = {}
        for category in categories:
            if self.storage.count_emails(category) > 0:
                results[category] = self.train_category(category, categories)
        return results
