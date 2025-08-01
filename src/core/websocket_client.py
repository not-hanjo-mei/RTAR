"""
WebSocket client for REALITY App connection.
"""

import json
import ssl
import threading
import time
import logging
import websocket
from typing import Callable, Optional, Any
from ..models.message import MessageItem


class WebSocketClient:
    """WebSocket client for connecting to REALITY App."""
    
    def __init__(self, config_manager):
        """Initialize WebSocket client."""
        self.config = config_manager
        self.ws_app: Optional[websocket.WebSocketApp] = None
        self.ws_thread: Optional[threading.Thread] = None
        self.is_connected = False
        self.connection_time = 0
        self.last_activity = 0
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_base_delay = 2
        self.reconnect_delays = [2, 4, 8, 16, 32]
        self.reconnect_lock = threading.Lock()
        self.is_reconnecting = False
        self.auto_reconnect_enabled = True
        self.connection_stable_time = 0 
        self.stable_connection_threshold = 10  # Threshold for stable connection in seconds
        
        # Permanent error codes that should stop auto-reconnect
        self.permanent_error_codes = {
            4003  # Chatroom has not opened
        }
        
        # Logger
        self.logger = logging.getLogger(__name__)
        
        # Callbacks
        self.on_message_callback: Optional[Callable[[MessageItem], None]] = None
        self.on_connect_callback: Optional[Callable[[], None]] = None
        self.on_disconnect_callback: Optional[Callable[[str, str], None]] = None
        self.on_error_callback: Optional[Callable[[Exception], None]] = None
    
    def set_callbacks(self, 
                     on_message: Optional[Callable[[MessageItem], None]] = None,
                     on_connect: Optional[Callable[[], None]] = None,
                     on_disconnect: Optional[Callable[[str, str], None]] = None,
                     on_error: Optional[Callable[[Exception], None]] = None):
        """Set callback functions for WebSocket events."""
        self.on_message_callback = on_message
        self.on_connect_callback = on_connect
        self.on_disconnect_callback = on_disconnect
        self.on_error_callback = on_error
    
    def _build_url(self) -> str:
        """Build WebSocket URL with media ID."""
        base_url = "wss://comment.REALITY.app"
        media_id = self.config.get_value('reality.mediaId')
        return f"{base_url}?media_id={media_id}"
    
    def _build_headers(self) -> dict:
        """Build WebSocket connection headers."""
        return {
            "X-WFLE-vLiveID": self.config.get_value('reality.vLiveId'),
            "X-WFLE-GID": self.config.get_value('reality.gid'),
            "Authorization": self.config.get_value('reality.auth'),
            "X-WFLE-CLIENT-IDENTIFIER": "viewer",
            "Accept-Charset": "UTF-8",
            "Accept": "*/*",
            "User-Agent": "ktor-client",
            "Sec-WebSocket-Extensions": "permessage-deflate"
        }
    
    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages."""
        self.last_activity = time.time()
        
        try:
            data = json.loads(message)
            msg_item = MessageItem.from_dict(data)
            
            if self.config.is_debug_mode():
                self.logger.debug(f"Received WebSocket message: {data}")
            
            if not msg_item.is_empty and self.on_message_callback:
                self.on_message_callback(msg_item)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            if self.on_error_callback:
                self.on_error_callback(e)
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            if self.on_error_callback:
                self.on_error_callback(e)
    
    def _on_error(self, ws, error):
        """Handle WebSocket errors."""
        self.logger.error(f"WebSocket error: {error}")
        if self.on_error_callback:
            self.on_error_callback(Exception(str(error)))
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close."""
        self.is_connected = False
        self.logger.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        if self.on_disconnect_callback:
            self.on_disconnect_callback(str(close_status_code), close_msg)
        
        # Check for permanent error codes
        if close_status_code in self.permanent_error_codes:
            self.logger.warning(f"Detected permanent error code {close_status_code}: {close_msg}")
            self.logger.warning("This is a permanent error, stopping auto-reconnect")
            self.auto_reconnect_enabled = False
            return

        # Check if the connection is stable enough (to avoid immediate reconnection)
        if hasattr(self, 'connection_time') and self.connection_time > 0:
            connection_duration = time.time() - self.connection_time
            if connection_duration < self.stable_connection_threshold:
                self.logger.warning(f"Connection duration too short ({connection_duration:.1f} seconds), potential issues detected")
                # For unstable connections, we still attempt to reconnect but increase the reconnect count
                self.reconnect_attempts += 1

        # Trigger auto-reconnect if enabled
        if self.auto_reconnect_enabled and self.reconnect_attempts < self.max_reconnect_attempts:
            threading.Thread(target=self._delayed_reconnect, daemon=True).start()
        elif self.reconnect_attempts >= self.max_reconnect_attempts:
            self.logger.warning(f"Reached maximum reconnect attempts ({self.max_reconnect_attempts}), stopping auto-reconnect")
            self.auto_reconnect_enabled = False
    
    def _on_open(self, ws):
        """Handle WebSocket connection open."""
        self.is_connected = True
        self.connection_time = time.time()
        self.last_activity = time.time()
        self.logger.info("WebSocket connection established")
        
        # Start a timer to reset reconnect attempts after stable connection
        threading.Timer(self.stable_connection_threshold, self._reset_reconnect_on_stable_connection).start()
        
        if self.on_connect_callback:
            self.on_connect_callback()
    
    def _on_ping(self, ws, message):
        """Handle ping messages."""
        self.last_activity = time.time()
    
    def _on_pong(self, ws, message):
        """Handle pong messages."""
        self.last_activity = time.time()
    
    def _reset_reconnect_on_stable_connection(self):
        """Reset reconnect attempts counter, only called when connection is stable."""
        if self.is_connected:
            old_attempts = self.reconnect_attempts
            self.reconnect_attempts = 0
            self.auto_reconnect_enabled = True
            if old_attempts > 0:
                self.logger.info(f"Connection stable for {self.stable_connection_threshold} seconds, resetting reconnect attempts (previous: {old_attempts})")

    def _delayed_reconnect(self):
        """Delay reconnection using specified intervals."""
        if self.reconnect_attempts < len(self.reconnect_delays):
            delay = self.reconnect_delays[self.reconnect_attempts]
        else:
            delay = self.reconnect_delays[-1]  # Use the last interval time

        self.logger.info(f"Waiting {delay} seconds before attempting reconnect #{self.reconnect_attempts + 1}...")
        time.sleep(delay)
        self.reconnect()
    
    def connect(self) -> bool:
        """Establish WebSocket connection."""
        try:
            url = self._build_url()
            headers = self._build_headers()
            
            # Enable WebSocket tracing only in debug mode
            websocket.enableTrace(self.config.is_debug_mode())
            
            self.logger.info(f"Connecting to WebSocket: {url}")
            self.ws_app = websocket.WebSocketApp(
                url,
                header=headers,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open,
                on_ping=self._on_ping,
                on_pong=self._on_pong
            )
            
            self.ws_thread = threading.Thread(
                target=self.ws_app.run_forever,
                kwargs={
                    "sslopt": {
                        "cert_reqs": ssl.CERT_NONE,
                        "check_hostname": False
                    }
                },
                daemon=True
            )
            self.ws_thread.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket: {e}")
            if self.on_error_callback:
                self.on_error_callback(e)
            return False
    
    def disconnect(self) -> bool:
        """Close WebSocket connection."""
        if self.ws_app:
            self.ws_app.close()
            self.ws_app = None
            
            if self.ws_thread and self.ws_thread.is_alive():
                try:
                    self.ws_thread.join(timeout=3)
                except RuntimeError:
                    pass
                self.ws_thread = None
            
            self.is_connected = False
            return True
        return False
    
    def reconnect(self) -> bool:
        """Attempt to reconnect WebSocket."""
        with self.reconnect_lock:
            if self.is_reconnecting:
                return False
            self.is_reconnecting = True
        
        try:
            # Check if maximum reconnect attempts reached
            if self.reconnect_attempts >= self.max_reconnect_attempts:
                self.logger.warning(f"Reached maximum reconnect attempts ({self.max_reconnect_attempts}), stopping reconnect")
                self.auto_reconnect_enabled = False
                return False
            
            self.disconnect()

            # Increase reconnect attempts
            self.reconnect_attempts += 1
            self.logger.info(f"Attempting reconnect #{self.reconnect_attempts}/{self.max_reconnect_attempts}...")
            
            # Try to connect
            if self.connect():
                self.logger.info("Reconnected successfully")
                # Don't reset reconnect attempts immediately, wait for stable connection
                return True
            else:
                self.logger.warning(f"Reconnection attempt #{self.reconnect_attempts} failed")
                if self.reconnect_attempts >= self.max_reconnect_attempts:
                    self.logger.error("Reached maximum reconnect attempts, stopping auto-reconnect")
                    self.auto_reconnect_enabled = False
                return False
            
        finally:
            with self.reconnect_lock:
                self.is_reconnecting = False
    
    def send_message(self, message: str) -> bool:
        """Send message through WebSocket."""
        if self.ws_app and self.is_connected:
            try:
                self.ws_app.send(message)
                return True
            except Exception:
                return False
        return False
    
    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
        if not self.is_connected:
            return False
        
        activity_timeout = self.config.get_value('health.activityTimeout', 10)
        return (time.time() - self.last_activity) <= activity_timeout
    
    def reset_reconnect_state(self):
        """Reset reconnect state and re-enable auto-reconnect."""
        with self.reconnect_lock:
            self.reconnect_attempts = 0
            self.auto_reconnect_enabled = True
            self.is_reconnecting = False
        self.logger.info("Reconnection state reset, auto-reconnect re-enabled")
    
    def get_reconnect_status(self) -> dict:
        """Get reconnect status information."""
        return {
            'reconnect_attempts': self.reconnect_attempts,
            'max_reconnect_attempts': self.max_reconnect_attempts,
            'auto_reconnect_enabled': self.auto_reconnect_enabled,
            'is_reconnecting': self.is_reconnecting,
            'is_connected': self.is_connected
        }