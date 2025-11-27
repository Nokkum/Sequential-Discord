import json
import os
from typing import Optional, Dict, Any
import asyncio
from threading import Lock

class Database:
    def __init__(self, filepath: str = "server_settings.json"):
        self.filepath = filepath
        self.lock = Lock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                json.dump({}, f)
    
    def _read_data(self) -> Dict:
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _write_data(self, data: Dict):
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_server_settings(self, guild_id: int) -> Dict[str, Any]:
        with self.lock:
            data = self._read_data()
            guild_key = str(guild_id)
            
            if guild_key not in data:
                data[guild_key] = self._get_default_settings()
                self._write_data(data)
            
            return data[guild_key]
    
    def update_server_setting(self, guild_id: int, key: str, value: Any):
        with self.lock:
            data = self._read_data()
            guild_key = str(guild_id)
            
            if guild_key not in data:
                data[guild_key] = self._get_default_settings()
            
            data[guild_key][key] = value
            self._write_data(data)
    
    def _get_default_settings(self) -> Dict[str, Any]:
        return {
            "welcome_channel": "welcome",
            "rules_channel": "rules",
            "welcome_enabled": True,
            "goodbye_enabled": True,
            "welcome_message": "Welcome to {server}, {mention}! 🎉\n\nWe're glad to have you here. You're member #{member_count}!",
            "goodbye_message": "{username} has left the server. We'll miss you! 👋",
            "embed_color": 0x00ff00
        }
    
    def get_setting(self, guild_id: int, key: str, default: Any = None) -> Any:
        settings = self.get_server_settings(guild_id)
        return settings.get(key, default)
