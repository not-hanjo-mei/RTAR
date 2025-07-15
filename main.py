#!/usr/bin/env python3
"""
RTAR - Reality Auto Reply Tool
Main application entry point.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config_manager import ConfigManager
from src.core.websocket_client import WebSocketClient
from src.core.message_processor import MessageProcessor
from src.core.response_generator import ResponseGenerator
from src.utils.adb_controller import ADBController
from src.utils.character_loader import CharacterLoader
from src.utils.preset_manager import PresetManager
from src.utils.url_parser import URLParser
from src.handlers.command_handler import CommandHandler
from src.handlers.input_handler import InputHandler


class RTARApplication:
    """Main RTAR application class."""
    
    def __init__(self):
        """Initialize RTAR application."""
        self.config = ConfigManager()
        self.character_loader = CharacterLoader()
        self.preset_manager = PresetManager()
        
        # Core components
        self.ws_client = WebSocketClient(self.config)
        self.response_generator = ResponseGenerator(self.config)
        self.adb_controller = ADBController(self.config)
        self.message_processor = MessageProcessor(self.config, self.response_generator, self.character_loader)
        
        # Handlers
        self.command_handler = CommandHandler(
            self.config, self.ws_client, self.message_processor,
            self.adb_controller, self.character_loader, self.preset_manager,
            self.response_generator
        )
        self.input_handler = InputHandler(self.command_handler)
    
    def setup_windows_console(self):
        """Setup Windows console for proper UTF-8 support."""
        if os.name == 'nt':
            os.system('chcp 65001 > nul')
            os.system('cls')
            os.system('color')
    
    def setup_linux_console(self):
        """Setup Linux console for proper UTF-8 support."""
        if os.name == 'posix':
            os.system('clear')
            # Set UTF-8 locale
            os.environ['LANG'] = 'en_US.UTF-8'
            os.environ['LC_ALL'] = 'en_US.UTF-8'
    
    def detect_os_and_setup(self):
        """Detect OS and setup appropriate console settings."""
        if os.name == 'nt':
            self.setup_windows_console()
        elif os.name == 'posix':
            self.setup_linux_console()
    
    def print_banner(self):
        """Print application banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                 RTAR - REALITY Auto Reply Tool                   ║
║                                                                  ║
║       AI-powered automated chat responses for REALITY App        ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def print_config_summary(self):
        """Print configuration summary."""
        media_id = self.config.get_value('reality.mediaId')
        model = self.config.get_value('openai.model')
        nickname = self.config.get_value('bot.myNickname')
        
        print(f"Media ID: {media_id}")
        print(f"AI Model: {model}")
        print(f"Bot Nickname: {nickname}")
        print(f"Response Rate: {self.config.get_value('bot.responseRate') * 100}%")
        print(f"Auto-send: {'ON' if self.config.get_value('adb.autoSend') else 'OFF'}")
        print("-" * 50)
    
    def prompt_for_media_id(self):
        """Prompt user to set media ID."""
        current_id = self.config.get_value('reality.mediaId')
        print(f"\033[90mCurrent Media ID: {current_id}\033[0m")
        
        while True:
            user_input = input("Enter media ID or share URL (Enter to keep current): ").strip()
            
            if not user_input:
                print(f"Using current Media ID: {current_id}")
                break
            
            media_id = URLParser.extract_media_id(user_input)
            if media_id:
                media_id = int(media_id)
                self.config.set_value('reality.mediaId', media_id)
                self.config.save_config()
                print(f"Updated Media ID: {media_id}")
                break
            else:
                print("Invalid format! Please enter a numeric ID or valid share URL")
                print("Examples:")
                print("  - Numeric ID: 101234567")
                print("  - Share URL: https://REALITY.app/viewer/101234567")
    
    def setup_callbacks(self):
        """Setup component callbacks."""
        # WebSocket callbacks
        self.ws_client.set_callbacks(
            on_message=self.message_processor.add_message,
            on_connect=lambda: self.message_processor.set_connection_time(time.time()),
            on_disconnect=lambda code, msg: print(f"[WS] Disconnected: {code} - {msg}"),
            on_error=lambda e: print(f"[WS] Error: {e}")
        )
        
        # Command handler output callback
        self.command_handler.set_output_callback(
            lambda msg: print(f"[RTAR] {msg}")
        )
        
        # Input handler prompt callback
        self.input_handler.set_prompt_callback(
            lambda: "\033[92mRTAR\033[0m \u003e "
        )
    
    def initialize_components(self):
        """Initialize all application components."""
        print("Initializing components...")
        
        # Auto-connect to ADB device
        print("Connecting to ADB device...")
        if self.adb_controller.connect():
            print("✓ ADB connected automatically")
            device_info = self.adb_controller.get_device_info()
            if device_info:
                print(f"  Device: {device_info}")
        else:
            print("Warning: ADB auto-connection failed. Manual mode only.")
        
        # Start message processor
        self.message_processor.start_processing()
        print("✓ Message processor started")
        
        # Start WebSocket connection
        print("Connecting to REALITY App...")
        self.ws_client.connect()
        
        # Start input handler
        self.input_handler.start()
        print("✓ Input handler started")
        
        print("\nRTAR is ready! Type /help for commands.")
    
    def run(self):
        """Run the RTAR application."""
        try:
            self.detect_os_and_setup()
            self.print_banner()
            
            # Validate configuration
            if not self.config.validate_config():
                print("Configuration validation failed!")
                print("Please check your config.json file")
                return
            
            self.print_config_summary()
            self.prompt_for_media_id()
            
            self.setup_callbacks()
            self.initialize_components()
            
            # Keep main thread alive
            self.input_handler.wait_for_input()
            
        except KeyboardInterrupt:
            print("\n\nShutting down RTAR...")
            self.shutdown()
        except Exception as e:
            print(f"\nFatal error: {e}")
            self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown the application."""
        print("Cleaning up...")
        
        # Stop components
        self.input_handler.stop()
        self.message_processor.stop_processing()
        self.ws_client.disconnect()
        self.adb_controller.disconnect()
        
        print("RTAR shutdown complete.")


def main():
    """Main entry point."""
    app = RTARApplication()
    app.run()


if __name__ == "__main__":
    main()