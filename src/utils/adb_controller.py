"""
ADB (Android Debug Bridge) controller for device interaction.
"""

import base64
import subprocess
import time
import random
import os
from typing import Optional


class ADBController:
    """Controls Android device via ADB for sending messages."""
    
    def __init__(self, config_manager):
        """Initialize ADB controller."""
        self.config = config_manager
        self.is_connected = False
        self.device_address = "127.0.0.1:5555"
        self._update_config()
    
    def _update_config(self):
        """Update configuration from config manager."""
        host = self.config.get_value('adb.host', '127.0.0.1')
        port = self.config.get_value('adb.port', '5555')
        self.device_address = f"{host}:{port}"
        
        self.input_x = self.config.get_value('adb.inputBox.x', 0)
        self.input_y = self.config.get_value('adb.inputBox.y', 0)
        self.send_x = self.config.get_value('adb.sendButton.x', 0)
        self.send_y = self.config.get_value('adb.sendButton.y', 0)
    
    def connect(self) -> bool:
        """Connect to ADB device."""
        try:
            cmd = f"adb connect {self.device_address}"
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8'
            )
            
            output = result.stdout.strip()
            self.is_connected = "connected" in output.lower()
            return self.is_connected
            
        except subprocess.CalledProcessError:
            self.is_connected = False
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from ADB device."""
        try:
            cmd = f"adb disconnect {self.device_address}"
            subprocess.run(
                cmd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8'
            )
            
            self.is_connected = False
            return True
            
        except subprocess.CalledProcessError:
            return False
    
    def test_connection(self) -> bool:
        """Test ADB connection."""
        try:
            cmd = f"adb -s {self.device_address} shell echo test"
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8'
            )
            
            return result.stdout.strip() == "test"
            
        except subprocess.CalledProcessError:
            return False
    
    def send_text(self, text: str) -> bool:
        """Send text to device via ADB."""
        if not self.is_connected and not self.connect():
            return False
        
        if len(text) > 90:
            return self._send_long_text(text)
        else:
            return self._send_short_text(text)
    
    def _send_short_text(self, text: str) -> bool:
        """Send short text (under 90 chars)."""
        try:
            # Click input box
            if not self._adb_command(f"shell input tap {self.input_x} {self.input_y}"):
                return False
            
            time.sleep(0.3)
            
            # Send text via broadcast
            text_b64 = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            if not self._adb_command(f'shell am broadcast -a ADB_INPUT_B64 --es msg "{text_b64}"'):
                return False
            
            time.sleep(0.3)
            
            # Click send button
            if not self._adb_command(f"shell input tap {self.send_x} {self.send_y}"):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _send_long_text(self, text: str) -> bool:
        """Send long text by splitting."""
        parts = self._split_text(text, 90)
        
        all_success = True
        for i, part in enumerate(parts):
            if i > 0:
                delay = random.uniform(0.25, 0.5)
                time.sleep(delay)
            
            if not self._send_short_text(part):
                all_success = False
                break
        
        return all_success
    
    def _split_text(self, text: str, max_length: int) -> list[str]:
        """Split text into parts at natural breakpoints."""
        if len(text) <= max_length:
            return [text]
        
        parts = []
        while text:
            if len(text) <= max_length:
                parts.append(text.strip())
                break
            
            # Find best split position
            split_pos = max_length
            breakpoints = ['。', '.', '，', ',', '！', '!', '？', '?', ' ', ':', ';']
            
            for bp in breakpoints:
                pos = text.rfind(bp, max_length // 2, max_length)
                if pos != -1:
                    split_pos = pos + 1
                    break
            
            part = text[:split_pos].strip()
            if part:
                parts.append(part)
            text = text[split_pos:].strip()
        
        return parts
    
    def _adb_command(self, command: str) -> bool:
        """Execute ADB command."""
        try:
            full_cmd = f"adb -s {self.device_address} {command}"
            
            # Use appropriate shell for the OS
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    full_cmd,
                    shell=True,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='utf-8'
                )
            else:  # Linux/macOS
                result = subprocess.run(
                    full_cmd,
                    shell=True,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding='utf-8'
                )
            return True
            
        except subprocess.CalledProcessError:
            return False
    
    def get_device_info(self) -> Optional[str]:
        """Get device information."""
        try:
            cmd = f"adb -s {self.device_address} shell getprop ro.product.model"
            result = subprocess.run(
                cmd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8'
            )
            
            return result.stdout.strip()
            
        except subprocess.CalledProcessError:
            return None