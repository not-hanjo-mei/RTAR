"""
AI response generation using OpenAI API.
"""

import asyncio
import re
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from ..models.message import MessageItem
from ..core.config_manager import ConfigManager


class ResponseGenerator:
    """Generates AI responses using OpenAI API."""
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize response generator."""
        self.config = config_manager
    def __init__(self, config_manager: ConfigManager):
        """Initialize response generator."""
        self.config = config_manager
        # Client is now initialized per-request to handle thread-local event loops
    
    def _create_client(self) -> Optional[AsyncOpenAI]:
        """Create OpenAI client with current configuration."""
        api_key = self.config.get_value('openai.apiKey')
        api_base = self.config.get_value('openai.apiBase')
        
        if api_key and api_base:
            return AsyncOpenAI(
                api_key=api_key,
                base_url=api_base
            )
        return None
    
    async def generate_response(self, 
                              message: str, 
                              username: str, 
                              context: List[Dict[str, str]],
                              character_prompt: Optional[str] = None) -> str:
        """
        Generate AI response for a message.
        """
        client = self._create_client()
        if not client:
            return "[Error: OpenAI client not configured]"
        
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(username, character_prompt)
            
            # Build user prompt with context
            user_prompt = self._build_user_prompt(message, username, context)
            
            # Get model configuration
            model = self.config.get_value('openai.model', 'free:QwQ-32B')
            temperature = self.config.get_value('openai.temperature', 0.7)
            # Increased token limit to allow reasoning models (like zai-glm-4.7) to finish thinking
            max_tokens = 8192
            
            # Generate response
            # Use 'async with' if client supported it, but AsyncOpenAI standard usage is direct for now 
            # (or we manually close if needed, though httpx handles it mostly)
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            # Extract and clean response
            content = response.choices[0].message.content
            
            # DEBUG LOGGING
            import logging
            logger = logging.getLogger(__name__)
            try:
                # Log full response structure to debug missing content
                full_json = response.model_dump_json()
                logger.debug(f"FULL RESPONSE DUMP: {full_json}")
            except:
                logger.debug(f"RAW CONTENT: {content}")
            
            reply = (content or "").strip()
            reply = self._clean_response(reply, username)
            
            if not reply and content:
                logger.warning("Response became empty after cleaning! Check regex logic.")
            
            await client.close() # Explicitly close to be safe with loops
            return reply
            
        except Exception as e:
            if client:
                await client.close()
            return f"[Error: {str(e)[:50]}...]"
    
    def _build_system_prompt(self, username: str, custom_prompt: Optional[str] = None) -> str:
        """Build system prompt for AI."""
        bot_name = self.config.get_value('bot.myNickname', 'RTAT Assistant')
        
        # Use custom prompt or default character
        if custom_prompt:
            base_prompt = custom_prompt
        else:
            base_prompt = self._get_default_character()
        
        return f"""{base_prompt}
                    Your username is "{bot_name}".
                    You need to reply to the comment from "{username}".
                    Keep responses friendly, engaging, and concise (under 100 characters when possible).
                    Use appropriate emojis to increase friendliness.
                    Don't introduce yourself as AI, respond naturally like a regular chat user.
                """
    
    def _build_user_prompt(self, message: str, username: str, context: List[Dict[str, str]]) -> str:
        """Build user prompt with context."""
        context_str = ""
        if context:
            context_length = self.config.get_value('bot.contextLength', 25)
            context_str = "Recent messages:\n"
            for msg in context[-context_length:]:
                context_str += f"{msg['name']}: {msg['content']}\n"
            context_str += "\n"
        
        return f"{context_str}Please reply to this comment from {username}: \"{message}\""
    
    def _clean_response(self, response: str, username: str) -> str:
        """Clean and format AI response."""
        # Remove thinking process tags
        response = re.sub(r'<think>.*?</think>\n', '', response, flags=re.DOTALL)
        
        # Remove username prefix if present
        response = re.sub(rf'^\s*{re.escape(username)}[:\s]*', '', response)
        
        # Clean up extra whitespace
        response = re.sub(r'\s+', ' ', response).strip()
        
        return response
    
    def _get_default_character(self) -> str:
        """Get default character personality."""
        return """You are a friendly chat bot participating in REALITY App live stream chat.
Keep responses friendly, interesting, and brief (preferably under 100 characters).
Don't use overly complex vocabulary or sentence structures.
You can use appropriate emojis to increase friendliness.
Don't introduce yourself or explain that you're AI, respond like a regular chat user.
Don't mention that you see "recent messages", just respond naturally."""
    
    async def generate_preset_response(self, 
                                     interaction_type: str, 
                                     username: str,
                                     preset_templates: Dict[str, List[str]]) -> Optional[str]:
        """
        Generate response from preset templates.
        
        Args:
            interaction_type: Type of interaction (join, like, follow)
            username: Username of the user
            preset_templates: Dictionary of preset templates
            
        Returns:
            Generated response or None if no template available
        """
        if interaction_type not in preset_templates:
            return None
        
        templates = preset_templates[interaction_type]
        if not templates:
            return None
        
        import random
        template = random.choice(templates)
        return template.replace("{username}", username)
    
    def is_configured(self) -> bool:
        """Check if OpenAI client is properly configured."""
        return (self.client is not None and 
                self.config.get_value('openai.apiKey') and
                self.config.get_value('openai.apiBase') and
                self.config.get_value('openai.model'))