"""
Command handler for processing user commands.
"""

import os
import time
from typing import Optional, Callable, Any
from ..core.config_manager import ConfigManager
from ..core.websocket_client import WebSocketClient
from ..core.message_processor import MessageProcessor
from ..core.response_generator import ResponseGenerator
from ..utils.adb_controller import ADBController
from ..utils.character_loader import CharacterLoader
from ..utils.preset_manager import PresetManager
from ..utils.user_filter import UserFilter


class CommandHandler:
    """Handles user commands and interactions."""
    
    def __init__(self, 
                 config_manager: ConfigManager,
                 websocket_client: WebSocketClient,
                 message_processor: MessageProcessor,
                 adb_controller: ADBController,
                 character_loader: CharacterLoader,
                 preset_manager: PresetManager,
                 response_generator: ResponseGenerator):
        """Initialize command handler."""
        self.config = config_manager
        self.ws_client = websocket_client
        self.message_processor = message_processor
        self.adb_controller = adb_controller
        self.character_loader = character_loader
        self.preset_manager = preset_manager
        self.response_generator = response_generator
        self.user_filter = UserFilter()
        
        # Commands mapping
        self.commands = {
            '/help': self.handle_help,
            '/stats': self.handle_stats,
            '/rate': self.handle_rate,
            '/clear': self.handle_clear,
            '/exit': self.handle_exit,
            '/auto': self.handle_auto,
            '/send': self.handle_send,
            '/adbtest': self.handle_adb_test,
            '/config': self.handle_config,
            '/reload': self.handle_reload,
            '/disconnect': self.handle_disconnect,
            '/reconnect': self.handle_reconnect,
            '/character': self.handle_character,
            '/presets': self.handle_presets,
            '/debug': self.handle_debug,
            '/block': self.handle_block,
            '/unblock': self.handle_unblock,
            '/filters': self.handle_filters,
        }
        
        self.output_callback: Optional[Callable[[str], None]] = None
    
    def set_output_callback(self, callback: Callable[[str], None]):
        """Set callback for command output."""
        self.output_callback = callback
    
    def execute_command(self, command: str, args: str = ""):
        """Execute a command with optional arguments."""
        cmd = command.lower()
        
        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                self._output(f"Error executing command {cmd}: {e}")
        else:
            self._output(f"Unknown command: {cmd}\nType /help for available commands.")
    
    def handle_help(self, args: str = ""):
        """Display help information."""
        help_text = """
RTAR Commands:
  /help                 - Show this help message
  /stats               - Show processing statistics
  /rate [value]        - Show/set response rate (0-1)
  /clear               - Clear message history and stats
  /exit                - Exit the application
  /auto                - Toggle auto-send mode
  /send [text]         - Send message manually
  /adbtest             - Test ADB connection
  /config              - Show current configuration
  /reload              - Reload configuration and reconnect
  /disconnect          - Disconnect WebSocket
  /reconnect           - Reconnect WebSocket
  /character [text]    - Show/set character personality
  /presets             - Show preset responses
  /debug               - Show debug mode status
  /block [vlive_id]    - Block a user by vlive_id
  /unblock [vlive_id]  - Unblock a user by vlive_id
  /filters             - Show blocked users
        """
        self._output(help_text.strip())
    
    def handle_stats(self, args: str = ""):
        """Show processing statistics."""
        stats = self.message_processor.get_stats()
        
        output = f"""
Processing Statistics:
  Processed Messages: {stats['processed_messages']}
  Context Length: {stats['context_length']}
  Queue Size: {stats['queue_size']}
  Is Running: {stats['is_running']}
  Response Rate: {self.config.get_value('bot.responseRate', 1.0)}
  WebSocket Connected: {self.ws_client.is_connected}
  ADB Connected: {self.adb_controller.is_connected}
        """
        self._output(output.strip())
    
    def handle_rate(self, args: str = ""):
        """Handle response rate commands."""
        if args:
            try:
                rate = float(args)
                if 0 <= rate <= 1:
                    self.config.set_value('bot.responseRate', rate)
                    self.config.save_config()
                    self._output(f"Response rate set to: {rate * 100}%")
                else:
                    self._output("Response rate must be between 0 and 1")
            except ValueError:
                self._output("Invalid response rate value")
        else:
            current_rate = self.config.get_value('bot.responseRate', 1.0)
            self._output(f"Current response rate: {current_rate * 100}%")
    
    def handle_clear(self, args: str = ""):
        """Clear message history and statistics."""
        self.message_processor.clear_history()
        
        # Clear screen on Windows
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        
        self._output("History cleared. Ready for new messages.")
    
    def handle_exit(self, args: str = ""):
        """Exit the application."""
        self._output("Shutting down RTAR...")
        
        # Stop message processing
        self.message_processor.stop_processing()
        
        # Disconnect WebSocket
        self.ws_client.disconnect()
        
        # Disconnect ADB
        self.adb_controller.disconnect()
        
        # Exit application
        os._exit(0)
    
    def handle_auto(self, args: str = ""):
        """Toggle auto-send mode."""
        current = self.config.get_value('adb.autoSend', True)
        new_value = not current
        
        self.config.set_value('adb.autoSend', new_value)
        self.config.save_config()
        
        self._output(f"Auto-send mode: {'ON' if new_value else 'OFF'}")
    
    def handle_send(self, args: str = ""):
        """Send message manually."""
        if args:
            message = args.strip()
            if self.adb_controller.send_text(message):
                self._output(f"Sent: {message}")
            else:
                self._output("Failed to send message")
        else:
            self._output("Usage: /send [message]")
    
    def handle_adb_test(self, args: str = ""):
        """Test ADB connection."""
        self._output(f"Testing ADB connection to {self.adb_controller.device_address}...")
        
        if self.adb_controller.test_connection():
            device_info = self.adb_controller.get_device_info()
            self._output(f"✓ ADB connection successful")
            if device_info:
                self._output(f"Device: {device_info}")
        else:
            self._output("✗ ADB connection failed")
    
    def handle_config(self, args: str = ""):
        """Show current configuration."""
        config_text = f"""
Current Configuration:
  Debug Mode: {self.config.get_value('debug', False)}
  
REALITY App:
  Media ID: {self.config.get_value('reality.mediaId')}
  vLive ID: {self.config.get_value('reality.vLiveId')[:10]}...
  GID: {self.config.get_value('reality.gid')[:15]}...
  
OpenAI:
  Model: {self.config.get_value('openai.model')}
  Temperature: {self.config.get_value('openai.temperature')}
  
Bot Settings:
  Nickname: {self.config.get_value('bot.myNickname')}
  Response Rate: {self.config.get_value('bot.responseRate') * 100}%
  Context Length: {self.config.get_value('bot.contextLength')}
  
ADB:
  Device: {self.adb_controller.device_address}
  Auto-send: {self.config.get_value('adb.autoSend')}
  Delay: {self.config.get_value('adb.sendDelay.min')}-{self.config.get_value('adb.sendDelay.max')}s
        """
        self._output(config_text.strip())
    
    def handle_reload(self, args: str = ""):
        """Reload configuration and reconnect."""
        self._output("Reloading configuration...")
        
        # Reload config
        old_media_id = self.config.get_value('reality.mediaId')
        old_vlive_id = self.config.get_value('reality.vLiveId')
        old_gid = self.config.get_value('reality.gid')
        old_auth = self.config.get_value('reality.auth')
        
        self.config.load_config()
        
        # Update dependencies
        self.adb_controller._update_config()
        self.response_generator.reload_client()
        self.character_loader.reload_character()
        self.preset_manager.load_presets()
        
        # Check if reconnection needed
        need_reconnect = (
            old_media_id != self.config.get_value('reality.mediaId') or
            old_vlive_id != self.config.get_value('reality.vLiveId') or
            old_gid != self.config.get_value('reality.gid') or
            old_auth != self.config.get_value('reality.auth')
        )
        
        if need_reconnect:
            self._output("Connection parameters changed, reconnecting...")
            self.ws_client.disconnect()
            time.sleep(1)
            self.ws_client.connect()
        else:
            self._output("Configuration reloaded (no connection changes)")
    
    def handle_disconnect(self, args: str = ""):
        """Disconnect WebSocket."""
        self.ws_client.disconnect()
        self._output("WebSocket disconnected")
    
    def handle_reconnect(self, args: str = ""):
        """Reconnect WebSocket."""
        self._output("Reconnecting WebSocket...")
        self.ws_client.reconnect()
    
    def handle_character(self, args: str = ""):
        """Handle character personality commands."""
        if args:
            # Set new character
            self.character_loader.set_character(args)
            self.character_loader.save_character(args)
            self._output("Character personality updated")
        else:
            # Show current character
            char = self.character_loader.get_character()
            self._output(f"Current character:\n{char}")
    
    def handle_presets(self, args: str = ""):
        """Show preset responses."""
        presets = self.preset_manager.get_all_presets()
        
        output = "Preset Responses:\n"
        for interaction_type, preset_data in presets.items():
            output += f"\n{interaction_type.upper()}:\n"
            output += f"  Description: {preset_data.get('description', 'No description')}\n"
            output += f"  Responses ({len(preset_data.get('replies', []))}):\n"
            for reply in preset_data.get('replies', []):
                output += f"    - {reply}\n"
        
        self._output(output.strip())
    
    def handle_debug(self, args: str = ""):
        """Show debug mode status."""
        debug_status = self.config.get_value('debug', False)
        self._output(f"Debug mode: {'ON' if debug_status else 'OFF'}")
        self._output("Note: Debug mode can only be changed in config.json")
    
    def handle_block(self, args: str = ""):
        """Block a user by vlive_id."""
        if not args:
            self._output("Usage: /block [vlive_id]")
            return
        
        vlive_id = args.strip()
        if self.user_filter.add_blocked_user(vlive_id):
            self._output(f"Blocked user: {vlive_id}")
        else:
            self._output(f"User already blocked: {vlive_id}")
    
    def handle_unblock(self, args: str = ""):
        """Unblock a user by vlive_id."""
        if not args:
            self._output("Usage: /unblock [vlive_id]")
            return
        
        vlive_id = args.strip()
        if self.user_filter.remove_blocked_user(vlive_id):
            self._output(f"Unblocked user: {vlive_id}")
        else:
            self._output(f"User not found in blocked list: {vlive_id}")
    
    def handle_filters(self, args: str = ""):
        """Show blocked users."""
        blocked_users = self.user_filter.get_blocked_users()
        
        if not blocked_users:
            self._output("No users are currently blocked")
        else:
            output = f"Blocked Users ({len(blocked_users)}):\n"
            for user in blocked_users:
                output += f"  - {user}\n"
            self._output(output.strip())
    
    def _output(self, message: str):
        """Output message through callback."""
        if self.output_callback:
            self.output_callback(message)
        else:
            print(message)