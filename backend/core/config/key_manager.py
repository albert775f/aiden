from cryptography.fernet import Fernet
from typing import Dict, Optional
import json
import os
from pathlib import Path

class APIKeyManager:
    """Manages API keys for different services with encryption."""
    
    def __init__(self, encryption_key: bytes = None):
        """Initialize the key manager with an optional encryption key."""
        if encryption_key is None:
            encryption_key = Fernet.generate_key()
        self.fernet = Fernet(encryption_key)
        self.keys: Dict[str, bytes] = {}
        self.config_path = Path("config/keys.json")
        self._load_keys()

    def _load_keys(self) -> None:
        """Load encrypted keys from file if it exists."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                encrypted_keys = json.load(f)
                self.keys = {k: v.encode() for k, v in encrypted_keys.items()}

    def _save_keys(self) -> None:
        """Save encrypted keys to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            encrypted_keys = {k: v.decode() for k, v in self.keys.items()}
            json.dump(encrypted_keys, f)

    def store_key(self, service: str, api_key: str) -> None:
        """Store an API key for a service."""
        encrypted_key = self.fernet.encrypt(api_key.encode())
        self.keys[service] = encrypted_key
        self._save_keys()

    def get_key(self, service: str) -> Optional[str]:
        """Get a decrypted API key for a service."""
        if service not in self.keys:
            return None
        return self.fernet.decrypt(self.keys[service]).decode()

    def remove_key(self, service: str) -> bool:
        """Remove an API key for a service."""
        if service in self.keys:
            del self.keys[service]
            self._save_keys()
            return True
        return False

    def list_services(self) -> list[str]:
        """List all services with stored API keys."""
        return list(self.keys.keys())