"""
Score emails against trained Naive Bayes classifiers.
"""

from pathlib import Path
from email import message_from_bytes
from dataclasses import dataclass
import joblib

@dataclass
class ClassificationResult:
    category: str
    score: float

class BayesClassifier:
    """Score emails against multiple category classifiers."""
    
    def __init__(self, db_dir: Path, threshold: float = 0.70):
        self.db_dir = db_dir
        self.threshold = threshold
        self._models: dict = {}
    
    def model_path(self, category: str) -> Path:
        return self.db_dir / f"{category}.joblib"
    
    def _load_model(self, category: str):
        """Load model lazily."""
        if category not in self._models:
            path = self.model_path(category)
            if path.exists():
                self._models[category] = joblib.load(path)
        return self._models.get(category)
    
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
    
    def score(self, email_raw: bytes, category: str) -> float:
        """Get the probability that an email belongs to a category."""
        model = self._load_model(category)
        if model is None:
            return 0.0
        
        text = self._extract_text(email_raw)
        proba = model.predict_proba([text])[0]
        return proba[1]  # probability of class 1 (positive/ham)
    
    def classify(self, email_raw: bytes, categories: list[str]) -> ClassificationResult | None:
        """Classify an email against all categories, return best match above threshold."""
        best: ClassificationResult | None = None
        
        for category in categories:
            score = self.score(email_raw, category)
            if score >= self.threshold:
                if best is None or score > best.score:
                    best = ClassificationResult(category=category, score=score)
        
        return best
    
    def classify_all(self, email_raw: bytes, categories: list[str]) -> list[ClassificationResult]:
        """Get scores for all categories."""
        results = []
        for category in categories:
            score = self.score(email_raw, category)
            results.append(ClassificationResult(category=category, score=score))
        return sorted(results, key=lambda r: r.score, reverse=True)
