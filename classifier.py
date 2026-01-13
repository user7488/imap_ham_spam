"""
Score emails against trained Bayesian classifiers.
"""

import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ClassificationResult:
    category: str
    score: float

class BayesClassifier:
    """Score emails against multiple category classifiers."""
    
    def __init__(self, db_dir: Path, threshold: float = 0.90):
        self.db_dir = db_dir
        self.threshold = threshold
    
    def db_path(self, category: str) -> Path:
        return self.db_dir / f"{category}.db"
    
    def score(self, email_raw: bytes, category: str) -> float:
        """Get the probability that an email belongs to a category."""
        db = self.db_path(category)
        if not db.exists():
            return 0.0
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.eml') as f:
            f.write(email_raw)
            f.flush()
            temp_path = f.name
        
        try:
            result = subprocess.run(
                ['sb_filter.py', '--classify', f'--database={db}', temp_path],
                capture_output=True,
                text=True,
            )
            return self._parse_score(result.stdout)
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def _parse_score(self, output: str) -> float:
        """Parse SpamBayes output to extract probability."""
        # #TODOLLM: Parse actual SpamBayes output format
        for line in output.splitlines():
            if 'probability' in line.lower() or 'score' in line.lower():
                parts = line.split()
                for part in parts:
                    try:
                        return float(part)
                    except ValueError:
                        continue
        return 0.0
    
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
