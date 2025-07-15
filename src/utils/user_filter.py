"""
User filtering utility for vlive_id-based blocking.
"""

import json
import os
import threading
import time
from typing import List, Set, Optional
from pathlib import Path


class UserFilter:
    """Manages user blocking based on vlive_id."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize user filter."""
        self.config_dir = Path(config_dir)
        self.filter_file = self.config_dir / "filter_list.json"
        self.blocked_vlive_ids: Set[str] = set()
        self.last_modified = 0
        self.lock = threading.RLock()
        self.load_filters()
    
    def load_filters(self):
        """Load blocked vlive_ids from filter file."""
        with self.lock:
            try:
                if not self.filter_file.exists():
                    self._create_default_filter_file()
                
                current_modified = os.path.getmtime(self.filter_file)
                if current_modified <= self.last_modified:
                    return  # No changes
                
                with open(self.filter_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.blocked_vlive_ids = set(data.get('filters', {}).get('blocked_vlive_ids', []))
                
                self.last_modified = current_modified
                print(f"[Filter] Loaded {len(self.blocked_vlive_ids)} blocked vlive_ids")
                
            except Exception as e:
                print(f"[Filter] Error loading filters: {e}")
                self.blocked_vlive_ids = set()
    
    def _create_default_filter_file(self):
        """Create default filter file if it doesn't exist."""
        default_data = {
            "filters": {
                "blocked_vlive_ids": []
            },
            "comments": {
                "blocked_vlive_ids": "List of vlive_id values that should not receive AI responses"
            }
        }
        
        self.config_dir.mkdir(exist_ok=True)
        with open(self.filter_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
    
    def is_blocked(self, vlive_id: str) -> bool:
        """Check if a vlive_id is blocked."""
        # Reload filters if file changed
        current_modified = 0
        try:
            current_modified = os.path.getmtime(self.filter_file)
        except (OSError, FileNotFoundError):
            pass
        
        if current_modified > self.last_modified:
            self.load_filters()
        
        return str(vlive_id) in self.blocked_vlive_ids
    
    def add_blocked_user(self, vlive_id: str) -> bool:
        """Add a vlive_id to blocked list."""
        with self.lock:
            vlive_id = str(vlive_id)
            if vlive_id in self.blocked_vlive_ids:
                return False
            
            self.blocked_vlive_ids.add(vlive_id)
            self._save_filters()
            return True
    
    def remove_blocked_user(self, vlive_id: str) -> bool:
        """Remove a vlive_id from blocked list."""
        with self.lock:
            vlive_id = str(vlive_id)
            if vlive_id not in self.blocked_vlive_ids:
                return False
            
            self.blocked_vlive_ids.discard(vlive_id)
            self._save_filters()
            return True
    
    def _save_filters(self):
        """Save current filters to file."""
        try:
            data = {
                "filters": {
                    "blocked_vlive_ids": list(self.blocked_vlive_ids)
                },
                "comments": {
                    "blocked_vlive_ids": "List of vlive_id values that should not receive AI responses"
                }
            }
            
            with open(self.filter_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.last_modified = os.path.getmtime(self.filter_file)
            
        except Exception as e:
            print(f"[Filter] Error saving filters: {e}")
    
    def get_blocked_users(self) -> List[str]:
        """Get list of blocked vlive_ids."""
        return list(self.blocked_vlive_ids)
    
    def clear_all_blocked(self):
        """Clear all blocked users."""
        with self.lock:
            self.blocked_vlive_ids.clear()
            self._save_filters()
    
    def reload_filters(self):
        """Force reload filters from file."""
        self.last_modified = 0
        self.load_filters()
    
    def add_bot_vlive_id(self, vlive_id: str):
        """Add bot's own vlive_id to prevent self-responses."""
        if vlive_id:
            self.add_blocked_user(str(vlive_id))
            print(f"[Filter] Added bot vlive_id {vlive_id} to blocked list")