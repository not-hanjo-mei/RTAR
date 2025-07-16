"""
Message processing and queue management.
"""

import asyncio
import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Set, Optional
from queue import Queue, Empty
import random

from ..models.message import MessageItem
from ..core.config_manager import ConfigManager
from ..core.response_generator import ResponseGenerator
from ..utils.adb_controller import ADBController
from ..utils.preset_manager import PresetManager
from ..utils.user_filter import UserFilter
from ..utils.character_loader import CharacterLoader


class MessageProcessor:
    """Processes incoming messages and generates responses."""
    
    def __init__(self, config_manager: ConfigManager, response_generator: ResponseGenerator, character_loader: Optional[CharacterLoader] = None):
        """Initialize message processor."""
        self.config = config_manager
        self.response_generator = response_generator
        self.character_loader = character_loader
        self.adb_controller = ADBController(config_manager)
        self.preset_manager = PresetManager()
        self.user_filter = UserFilter()
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Processing queues
        self.message_queue = Queue()
        self.output_queue = Queue()
        
        # State tracking
        self.processed_messages: Set[str] = set()
        self.processed_content: Set[str] = set()
        self.recent_context: List[Dict[str, str]] = []
        self.connection_time = 0
        
        # Threading
        self.processing_thread: Optional[threading.Thread] = None
        self.executor: Optional[ThreadPoolExecutor] = None
        self.is_running = False
        
        # Configuration
        self.max_workers = self.config.get_value('performance.maxWorkers', 4)
        self.response_timeout = self.config.get_value('performance.responseTimeout', 30)
        self.initial_cutoff = self.config.get_value('bot.initialHistoryCutoff', 5)
        self.response_rate = self.config.get_value('bot.responseRate', 1.0)
        self.context_length = self.config.get_value('bot.contextLength', 20)
    
    def start_processing(self):
        """Start message processing thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.processing_thread = threading.Thread(target=self._process_messages, daemon=True)
        self.processing_thread.start()
    
    def stop_processing(self):
        """Stop message processing thread."""
        self.is_running = False
        
        # Signal threads to stop
        self.message_queue.put(None)
        
        if self.processing_thread and self.processing_thread.is_alive():
            try:
                self.processing_thread.join(timeout=5)
            except:
                pass
        
        if self.executor:
            self.executor.shutdown(wait=False)
    
    def add_message(self, message: MessageItem):
        """Add message to processing queue."""
        if message and message.msg_id not in self.processed_messages:
            self.logger.debug(f"Adding message to queue: {message.name}: {message.msg}")
            self.message_queue.put(message)
    
    def set_connection_time(self, connection_time: float):
        """Set the connection time for history cutoff."""
        self.connection_time = connection_time
    
    def _process_messages(self):
        """Main message processing loop."""
        # Wait for connection to be established
        while self.connection_time == 0 and self.is_running:
            time.sleep(0.1)
        
        initial_cutoff_time = self.connection_time + self.initial_cutoff
        
        while self.is_running:
            try:
                message = self.message_queue.get(timeout=1)
                if message is None:  # Shutdown signal
                    break
                
                self._process_single_message(message, initial_cutoff_time)
                
            except Empty:
                continue
            except Exception as e:
                self._log_error(f"Error processing message: {e}")
    
    def _process_single_message(self, message: MessageItem, initial_cutoff_time: float):
        """Process a single message."""
        if message.is_empty:
            return
            
        self.logger.debug(f"Processing message: {message.name} ({message.content_type}): {message.msg}")
        
        # Add to context
        self.recent_context.append({
            'name': message.name,
            'content': message.msg
        })
        
        # Keep only recent context
        if len(self.recent_context) > self.context_length:
            self.recent_context = self.recent_context[-self.context_length:]
        
        # Log received message
        self._log_message(f"{message.sender_type}{message.name}: {message.msg}")
        
        # Check if should respond
        should_respond = self._should_respond(message, initial_cutoff_time)
        
        if should_respond:
            self.processed_messages.add(message.msg_id)
            
            # Generate response in thread pool if executor is available
            if self.executor is not None:
                future = self.executor.submit(
                    self._generate_response_sync,
                    message,
                    list(self.recent_context)
                )
                
                try:
                    response = future.result(timeout=self.response_timeout)
                    if response:
                        self._handle_response(response, message)
                except Exception as e:
                    self._log_error(f"Error generating response: {e}")
            else:
                # Fallback to synchronous execution if executor is not available
                try:
                    response = self._generate_response_sync(message, list(self.recent_context))
                    if response:
                        self._handle_response(response, message)
                except Exception as e:
                    self._log_error(f"Error generating response (sync): {e}")
    
    def _should_respond(self, message: MessageItem, initial_cutoff_time: float) -> bool:
        """Determine if we should respond to this message."""
        # Skip if already processed
        if message.msg_id in self.processed_messages:
            self.logger.debug(f"Skipping already processed message: {message.msg_id}")
            return False
        
        # Skip blocked users (vlive_id-based filtering only)
        if message.vlive_id:
            if self.user_filter.is_blocked(message.vlive_id):
                self.logger.debug(f"Skipping blocked user: {message.vlive_id}")
                return False
        
        # Skip history messages - Apply to ALL message types including interaction messages
        if message.timestamp < initial_cutoff_time:
            self.logger.debug(f"Skipping history message: {message.timestamp} < {initial_cutoff_time} (type: {message.content_type})")
            return False
        
        # Skip system messages
        if message.is_system_message:
            return False
        
        # Handle interaction messages with presets
        if message.is_interaction_message:
            return self._handle_interaction_message(message)
        
        # Handle all regular messages with probability (no bot filtering)
        return random.random() < self.response_rate
    
    def _handle_interaction_message(self, message: MessageItem) -> bool:
        """Handle interaction messages (like, follow, join) with preset responses."""
        if message.content_type is None:
            return False
        
        interaction_type = self._get_interaction_type(message.content_type)
        if not interaction_type:
            return False
        
        response = self.preset_manager.get_preset_response(interaction_type, message.name)
        if response:
            self._log_message(f"[Preset]{self.config.get_value('bot.myNickname', 'AI')}: {response}")
            
            if self.config.get_value('adb.autoSend', True):
                delay = random.uniform(
                    self.config.get_value('adb.sendDelay.min', 1.0),
                    self.config.get_value('adb.sendDelay.max', 3.0)
                )
                time.sleep(delay)
                self.adb_controller.send_text(response)
            
            return False  # Don't generate AI response for presets
        
        return True
    
    def _get_interaction_type(self, content_type: Optional[int]) -> Optional[str]:
        """Get interaction type from content type."""
        if content_type is None:
            return None
        
        type_map = {
            2: 'like',
            3: 'gift',
            4: 'follow',
            8: 'join'
        }
        return type_map.get(content_type)
    
    def _generate_response_sync(self, message: MessageItem, context: List[Dict[str, str]]) -> Optional[str]:
        """Generate response synchronously."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Get character prompt from character loader
            character_prompt = None
            if self.character_loader:
                character_prompt = self.character_loader.get_character()
            
            response = loop.run_until_complete(
                self.response_generator.generate_response(
                    message.msg,
                    message.name,
                    context,
                    character_prompt
                )
            )
            
            loop.close()
            self.logger.debug(f"Generated response for {message.name}: {response}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error in response generation: {e}")
            return None
    
    def _handle_response(self, response: str, original_message: MessageItem):
        """Handle generated response."""
        bot_name = self.config.get_value('bot.myNickname', 'AI')
        self._log_message(f"[AI]{bot_name}: {response}")
        
        if self.config.get_value('adb.autoSend', True):
            delay = random.uniform(
                self.config.get_value('adb.sendDelay.min', 1.0),
                self.config.get_value('adb.sendDelay.max', 3.0)
            )
            self.logger.debug(f"Waiting {delay:.1f}s before sending response...")
            time.sleep(delay)
            if self.adb_controller.send_text(response):
                self.logger.debug("Response sent successfully")
            else:
                self.logger.error("Failed to send response via ADB")
    
    def _log_message(self, message: str):
        """Log message to output queue."""
        self.output_queue.put(message)
        self.logger.info(message)
    
    def _log_error(self, error: str):
        """Log error message."""
        self.output_queue.put(f"[Error] {error}")
        self.logger.error(error)
    
    def get_output_message(self) -> Optional[str]:
        """Get message from output queue."""
        try:
            return self.output_queue.get_nowait()
        except Empty:
            return None
    
    def clear_history(self):
        """Clear message history and processed sets."""
        self.processed_messages.clear()
        self.processed_content.clear()
        self.recent_context.clear()
    
    def get_stats(self) -> dict:
        """Get processing statistics."""
        return {
            'processed_messages': len(self.processed_messages),
            'context_length': len(self.recent_context),
            'queue_size': self.message_queue.qsize(),
            'is_running': self.is_running
        }