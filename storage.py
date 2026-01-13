"""
Local storage for training emails, organized by category.
"""

from pathlib import Path
from imap_client import Email

class LocalStorage:
    """Store and retrieve emails locally by category."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def category_path(self, category: str) -> Path:
        path = self.data_dir / category
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def save_email(self, category: str, email: Email) -> Path:
        """Save an email to the category folder."""
        folder = self.category_path(category)
        filepath = folder / f"{email.uid}.eml"
        with open(filepath, 'wb') as f:
            f.write(email.raw)
        return filepath
    
    def save_emails(self, category: str, emails: list[Email]) -> int:
        """Save multiple emails to the category folder."""
        count = 0
        for email in emails:
            self.save_email(category, email)
            count += 1
        return count
    
    def load_emails(self, category: str) -> list[bytes]:
        """Load all emails from a category folder."""
        folder = self.category_path(category)
        emails = []
        for filepath in folder.glob('*.eml'):
            with open(filepath, 'rb') as f:
                emails.append(f.read())
        return emails
    
    def count_emails(self, category: str) -> int:
        """Count emails in a category folder."""
        folder = self.category_path(category)
        return len(list(folder.glob('*.eml')))
    
    def list_categories(self) -> list[str]:
        """List all category folders that have data."""
        return [d.name for d in self.data_dir.iterdir() if d.is_dir()]
