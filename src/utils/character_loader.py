"""
Character/personality loader for AI responses.
"""

import os
from typing import Optional


class CharacterLoader:
    """Loads character/personality configurations for AI responses."""
    
    def __init__(self, character_path: Optional[str] = None):
        """Initialize character loader."""
        self.character_path = character_path or self._get_default_character_path()
        self.character_prompt = self.load_character()
    
    def _get_default_character_path(self) -> str:
        """Get default character file path."""
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config',
            'character.md'
        )
    
    def load_character(self) -> str:
        """Load character personality from file."""
        try:
            if os.path.exists(self.character_path):
                with open(self.character_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    return self._process_character_content(content)
            else:
                return self._get_default_character()
        except Exception as e:
            print(f"Error loading character: {e}")
            return self._get_default_character()
    
    def _process_character_content(self, content: str) -> str:
        """Process character content by removing markdown formatting."""
        lines = []
        for line in content.split('\n'):
            # Skip headers and empty lines
            if line.startswith('#') or line.strip() == '':
                continue
            
            # Remove list symbols
            if line.startswith('- '):
                line = line[2:]
            
            lines.append(line.strip())
        
        return '\n'.join(lines).strip()
    
    def _get_default_character(self) -> str:
        """Get default character personality."""
        return """You are a friendly chat bot participating in REALITY App live stream chat.
Keep responses friendly, interesting, and brief (preferably under 100 characters).
Don't use overly complex vocabulary or sentence structures.
You can use appropriate emojis to increase friendliness.
Don't introduce yourself or explain that you're AI, respond like a regular chat user.
Don't mention that you see "recent messages", just respond naturally."""
    
    def reload_character(self) -> str:
        """Reload character from file."""
        self.character_prompt = self.load_character()
        return self.character_prompt
    
    def get_character(self) -> str:
        """Get current character prompt."""
        return self.character_prompt
    
    def set_character(self, prompt: str) -> bool:
        """Set custom character prompt."""
        self.character_prompt = prompt
        return True
    
    def save_character(self, prompt: str) -> bool:
        """Save character prompt to file."""
        try:
            os.makedirs(os.path.dirname(self.character_path), exist_ok=True)
            with open(self.character_path, 'w', encoding='utf-8') as f:
                f.write(prompt)
            self.character_prompt = prompt
            return True
        except Exception as e:
            print(f"Error saving character: {e}")
            return False