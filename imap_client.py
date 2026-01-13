"""
IMAP client for fetching emails from category folders.
"""

from dataclasses import dataclass
from imapclient import IMAPClient
from email import message_from_bytes
from email.message import Message

from config import ImapConfig

@dataclass
class Email:
    uid: int
    subject: str
    sender: str
    raw: bytes

class ImapFetcher:
    """Fetches emails from IMAP folders."""
    
    def __init__(self, config: ImapConfig):
        self.config = config
        self.client: IMAPClient | None = None
    
    def connect(self) -> None:
        self.client = IMAPClient(self.config.host, port=self.config.port, ssl=self.config.use_ssl)
        self.client.login(self.config.username, self.config.password)
    
    def disconnect(self) -> None:
        if self.client:
            self.client.logout()
            self.client = None
    
    def list_folders(self) -> list[str]:
        """List all IMAP folders."""
        if not self.client:
            raise RuntimeError("Not connected")
        folders = self.client.list_folders()
        return [f[2] for f in folders]
    
    def fetch_from_folder(self, folder: str, limit: int = 0, readonly: bool = True) -> list[Email]:
        """Fetch emails from a specific folder."""
        if not self.client:
            raise RuntimeError("Not connected")
        
        self.client.select_folder(folder, readonly=readonly)
        uids = self.client.search(['ALL'])
        
        if limit > 0:
            uids = uids[:limit]
        
        if not uids:
            return []
        
        emails = []
        messages = self.client.fetch(uids, ['RFC822'])
        
        for uid, data in messages.items():
            raw = data[b'RFC822']
            msg: Message = message_from_bytes(raw)
            emails.append(Email(
                uid=uid,
                subject=msg.get('Subject', ''),
                sender=msg.get('From', ''),
                raw=raw,
            ))
        
        return emails
    
    def fetch_unseen(self, folder: str = 'INBOX', limit: int = 0) -> list[Email]:
        """Fetch only unseen emails from a folder."""
        if not self.client:
            raise RuntimeError("Not connected")
        
        self.client.select_folder(folder)
        uids = self.client.search(['UNSEEN'])
        
        if limit > 0:
            uids = uids[:limit]
        
        if not uids:
            return []
        
        emails = []
        messages = self.client.fetch(uids, ['RFC822'])
        
        for uid, data in messages.items():
            raw = data[b'RFC822']
            msg: Message = message_from_bytes(raw)
            emails.append(Email(
                uid=uid,
                subject=msg.get('Subject', ''),
                sender=msg.get('From', ''),
                raw=raw,
            ))
        
        return emails
    
    def count_unseen(self, folder: str = 'INBOX') -> int:
        """Count unseen emails in a folder."""
        if not self.client:
            raise RuntimeError("Not connected")
        self.client.select_folder(folder, readonly=True)
        uids = self.client.search(['UNSEEN'])
        return len(uids)
    
    def move_email(self, uid: int, dest_folder: str) -> None:
        """Move an email to a destination folder."""
        if not self.client:
            raise RuntimeError("Not connected")
        # #NOTELLM: Gmail uses COPY+DELETE instead of MOVE for older IMAP
        self.client.move([uid], dest_folder)
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
