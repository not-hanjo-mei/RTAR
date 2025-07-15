"""
Preset response management.
"""

import json
import os
from typing import Dict, List, Optional, Any


class PresetManager:
    """Manages preset responses for different interaction types."""
    
    def __init__(self, preset_path: Optional[str] = None):
        """Initialize preset manager."""
        self.preset_path = preset_path or self._get_default_preset_path()
        self.presets: Dict[str, Dict[str, Any]] = {}
        self.load_presets()
    
    def _get_default_preset_path(self) -> str:
        """Get default preset file path."""
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config',
            'presets.json'
        )
    
    def load_presets(self) -> bool:
        """Load preset responses from file."""
        try:
            if os.path.exists(self.preset_path):
                with open(self.preset_path, 'r', encoding='utf-8') as f:
                    self.presets = json.load(f)
                return True
            else:
                # Create default presets if file doesn't exist
                self._create_default_presets()
                return self.save_presets()
        except Exception as e:
            print(f"Error loading presets: {e}")
            return False
    
    def save_presets(self) -> bool:
        """Save presets to file."""
        try:
            os.makedirs(os.path.dirname(self.preset_path), exist_ok=True)
            with open(self.preset_path, 'w', encoding='utf-8') as f:
                json.dump(self.presets, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Error saving presets: {e}")
            return False
    
    def _create_default_presets(self):
        """Create default preset responses."""
        self.presets = {
            "join": {
                "description": "Auto-reply when users join the livestream",
                "replies": [
                    "Welcome {username} to the livestream! 😊",
                    "Hello {username}, welcome to the stream!",
                    "{username} is here, welcome welcome! 👋",
                    "Welcome new friend {username}!",
                    "Hi {username}, let's watch the stream together!"
                ]
            },
            "like": {
                "description": "Auto-reply when users like the stream",
                "replies": [
                    "Thank you {username} for the like! ❤️",
                    "{username} liked it, thanks for the support!",
                    "Received {username}'s love!",
                    "Got {username}'s like, so happy!",
                    "Thanks {username} for the support!"
                ]
            },
            "follow": {
                "description": "Auto-reply when users follow",
                "replies": [
                    "Thank you {username} for following! 🎉",
                    "{username} followed, thanks for the support!",
                    "Welcome new follower {username}!",
                    "Received {username}'s follow, thank you!",
                    "Thanks {username} for becoming a new fan!"
                ]
            },
            "gift": {
                "description": "Auto-reply when users send gifts",
                "replies": [
                    "Thank you {username} for the gift! So touched!",
                    "Received {username}'s gift, love you!",
                    "Wow, {username}'s gift is amazing!",
                    "Thank you {username} for the generous support!",
                    "{username}'s gift makes my whole day!"
                ]
            }
        }
    
    def get_preset_response(self, interaction_type: str, username: str) -> Optional[str]:
        """Get a preset response for interaction type."""
        if interaction_type not in self.presets:
            return None
        
        replies = self.presets[interaction_type].get('replies', [])
        if not replies:
            return None
        
        import random
        template = random.choice(replies)
        return template.replace("{username}", username)
    
    def get_all_presets(self) -> Dict[str, Dict[str, List[str]]]:
        """Get all presets."""
        return self.presets
    
    # def add_preset(self, interaction_type: str, reply: str) -> bool:
    #     """Add a new preset response for interaction type."""
    #     if interaction_type not in self.presets:
    #         self.presets[interaction_type] = {
    #             "description": f"Preset reply type: {interaction_type}",
    #             "replies": []
    #         }
        
    #     if reply not in self.presets[interaction_type]['replies']:
    #         self.presets[interaction_type]['replies'].append(reply)
    #         return self.save_presets()
        
    #     return True
    
    # def remove_preset(self, interaction_type: str, reply: str) -> bool:
    #     """Remove a preset response."""
    #     if interaction_type in self.presets:
    #         replies = self.presets[interaction_type]['replies']
    #         if reply in replies:
    #             replies.remove(reply)
    #             return self.save_presets()
        
    #     return False
    
    # def update_presets(self, new_presets: Dict[str, Dict[str, List[str]]]) -> bool:
    #     """Update all presets."""
    #     self.presets = new_presets
    #     return self.save_presets()