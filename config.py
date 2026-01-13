"""
Configuration loader for IMAP credentials and categories.
"""

import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ImapConfig:
    host: str
    port: int
    username: str
    password: str
    use_ssl: bool = True

@dataclass
class AppConfig:
    imap: ImapConfig
    categories: list[str]
    data_dir: Path
    db_dir: Path

def load_categories(path: Path) -> list[str]:
    """Parse categories.md and extract folder names."""
    categories = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('\\ '):
                categories.append(line[2:])
    return categories

def load_config() -> AppConfig:
    """Load configuration from environment variables and categories.md."""
    # #TODOLLM: Add .env file support for credentials
    imap = ImapConfig(
        host=os.environ.get('IMAP_HOST', 'imap.gmail.com'),
        port=int(os.environ.get('IMAP_PORT', '993')),
        username=os.environ.get('IMAP_USER', ''),
        password=os.environ.get('IMAP_PASS', ''),
    )
    
    project_root = Path(__file__).parent
    categories = load_categories(project_root / 'categories.md')
    
    data_dir = Path(os.environ.get('DATA_DIR', project_root / 'data'))
    db_dir = Path(os.environ.get('DB_DIR', project_root / 'classifiers'))
    
    return AppConfig(
        imap=imap,
        categories=categories,
        data_dir=data_dir,
        db_dir=db_dir,
    )
