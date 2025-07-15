"""
Input handler for user commands and interactions.
"""

import threading
import time
from typing import Optional, Callable

from .command_handler import CommandHandler


class InputHandler:
    """Handles user input and command processing."""
    
    def __init__(self, command_handler: CommandHandler):
        """Initialize input handler."""
        self.command_handler = command_handler
        self.is_running = False
        self.input_thread: Optional[threading.Thread] = None
        self.prompt_callback: Optional[Callable[[], str]] = None
    
    def start(self):
        """Start input handling thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()
    
    def stop(self):
        """Stop input handling thread."""
        self.is_running = False
        
        if self.input_thread and self.input_thread.is_alive():
            try:
                self.input_thread.join(timeout=1)
            except:
                pass
    
    def set_prompt_callback(self, callback: Callable[[], str]):
        """Set callback for generating input prompt."""
        self.prompt_callback = callback
    
    def _input_loop(self):
        """Main input handling loop."""
        time.sleep(1)  # Wait for startup
        
        while self.is_running:
            try:
                # Get prompt
                prompt = "> "
                if self.prompt_callback:
                    prompt = self.prompt_callback()
                
                # Get user input
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Process command
                if user_input.startswith('/'):
                    parts = user_input.split(maxsplit=1)
                    command = parts[0]
                    args = parts[1] if len(parts) > 1 else ""
                    
                    self.command_handler.execute_command(command, args)
                else:
                    self.command_handler.execute_command('/send', user_input)
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                self.command_handler.execute_command('/exit')
                break
            except Exception as e:
                self.command_handler.execute_command('/help')
    
    def wait_for_input(self):
        """Wait for input thread to complete."""
        if self.input_thread and self.input_thread.is_alive():
            try:
                self.input_thread.join()
            except KeyboardInterrupt:
                self.command_handler.execute_command('/exit')