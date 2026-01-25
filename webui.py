import gradio as gr
import sys
import os
import threading
import time
import logging
import queue
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config_manager import ConfigManager
from src.core.websocket_client import WebSocketClient
from src.core.message_processor import MessageProcessor
from src.core.response_generator import ResponseGenerator
from src.utils.adb_controller import ADBController
from src.utils.character_loader import CharacterLoader
from src.utils.preset_manager import PresetManager
from src.models.message import MessageItem

# Setup logging
log_queue = queue.Queue()

class QueueHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            log_queue.put(msg)
        except Exception:
            self.handleError(record)

# Initialize logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
queue_handler = QueueHandler()
queue_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(queue_handler)


class BotState:
    def __init__(self):
        self.config = ConfigManager()
        self.running = False
        
        # Components
        self.character_loader = CharacterLoader()
        self.preset_manager = PresetManager()
        self.ws_client = None
        self.response_generator = None
        self.adb_controller = None
        self.message_processor = None
        
        self.logs = []

    def initialize(self):
        self.config.load_config()
        # Re-attach queue handler as ConfigManager.setup_logging() clears existing handlers
        logging.getLogger().addHandler(queue_handler)
        
        self.ws_client = WebSocketClient(self.config)
        self.response_generator = ResponseGenerator(self.config)
        self.adb_controller = ADBController(self.config)
        self.message_processor = MessageProcessor(self.config, self.response_generator, self.character_loader)
        
        # Setup callbacks
        self.ws_client.set_callbacks(
            on_message=self.on_message_received,
            on_connect=self.on_ws_connect,
            on_disconnect=lambda c, m: logger.info(f"[WS] Disconnected: {c} - {m}"),
            on_error=lambda e: logger.error(f"[WS] Error: {e}")
        )

    def on_ws_connect(self):
        logger.info("[WS] Connected")
        if self.message_processor:
            self.message_processor.set_connection_time(time.time())

    def on_message_received(self, msg_item: MessageItem):
        self.message_processor.add_message(msg_item)
        # Log/Display logic handled by processor mostly, but we can hook here if needed
        pass

    def start_bot(self):
        if self.running:
            return "Bot is already running."
        
        logger.info("Starting RTAR Bot...")
        self.initialize()
        
        # Connect ADB
        if self.adb_controller.connect():
            logger.info("ADB connected automatically.")
        else:
            logger.warning("ADB connection failed.")

        # Start Processing
        self.message_processor.start_processing()
        
        # Connect WebSocket
        self.ws_client.connect()
        
        self.running = True
        return "Bot started."

    def stop_bot(self):
        if not self.running:
            return "Bot is not running."
        
        logger.info("Stopping RTAR Bot...")
        if self.message_processor:
            self.message_processor.stop_processing()
        if self.ws_client:
            self.ws_client.disconnect()
        if self.adb_controller:
            self.adb_controller.disconnect()
            
        self.running = False
        return "Bot stopped."

    def get_logs(self):
        new_logs = []
        while not log_queue.empty():
            new_logs.append(log_queue.get())
        
        if new_logs:
            self.logs.extend(new_logs)
            # Keep last 1000 lines
            if len(self.logs) > 1000:
                self.logs = self.logs[-1000:]
            
        return "\n".join(self.logs)

bot_state = BotState()

def save_configuration(media_id, vlive_id, gid, auth, api_key, api_base, model, response_rate, auto_send):
    config = bot_state.config
    config.set_value('reality.mediaId', int(media_id) if media_id else 0)
    config.set_value('reality.vLiveId', vlive_id)
    config.set_value('reality.gid', gid)
    config.set_value('reality.auth', auth)
    config.set_value('openai.apiKey', api_key)
    config.set_value('openai.apiBase', api_base)
    config.set_value('openai.model', model)
    config.set_value('bot.responseRate', float(response_rate))
    config.set_value('adb.autoSend', auto_send)
    
    if config.save_config():
        return "Configuration saved successfully."
    else:
        return "Failed to save configuration."

def load_configuration():
    config = bot_state.config
    # reloading config from file
    config.load_config()
    return [
        config.get_value('reality.mediaId'),
        config.get_value('reality.vLiveId'),
        config.get_value('reality.gid'),
        config.get_value('reality.auth'),
        config.get_value('openai.apiKey'),
        config.get_value('openai.apiBase'),
        config.get_value('openai.model'),
        config.get_value('bot.responseRate'),
        config.get_value('adb.autoSend')
    ]

# Build UI
with gr.Blocks(title="RTAR WebUI", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# RTAR - Reality Auto Reply Tool")
    
    with gr.Tabs():
        with gr.TabItem("Dashboard"):
            with gr.Row():
                start_btn = gr.Button("Start Bot", variant="primary")
                stop_btn = gr.Button("Stop Bot", variant="stop")
            
            status_output = gr.Textbox(label="Status", interactive=False)
            
            logs_output = gr.TextArea(label="Logs", interactive=False, lines=20, max_lines=20, autoscroll=True)
            
            # Auto-refresh logs
            demo.load(None, None, None) # Init
            
            # Timer for log update
            log_timer = gr.Timer(1)
            log_timer.tick(bot_state.get_logs, outputs=logs_output)
            
            start_btn.click(bot_state.start_bot, outputs=status_output)
            stop_btn.click(bot_state.stop_bot, outputs=status_output)

        with gr.TabItem("Configuration"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### REALITY Settings")
                    c_media_id = gr.Textbox(label="Media ID")
                    c_vlive_id = gr.Textbox(label="vLive ID", type="password")
                    c_gid = gr.Textbox(label="GID", type="password")
                    c_auth = gr.Textbox(label="Auth Token", type="password")
                
                with gr.Column():
                    gr.Markdown("### OpenAI Settings")
                    c_api_key = gr.Textbox(label="API Key", type="password")
                    c_api_base = gr.Textbox(label="API Base URL")
                    c_model = gr.Textbox(label="Model")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Bot Settings")
                    c_response_rate = gr.Slider(minimum=0.0, maximum=1.0, label="Response Rate")
                    c_auto_send = gr.Checkbox(label="ADB Auto Send")

            with gr.Row():
                load_btn = gr.Button("Load Config")
                save_btn = gr.Button("Save Config", variant="primary")
                config_status = gr.Label(label="Config Status")

            load_btn.click(
                load_configuration, 
                outputs=[c_media_id, c_vlive_id, c_gid, c_auth, c_api_key, c_api_base, c_model, c_response_rate, c_auto_send]
            )
            
            save_btn.click(
                save_configuration,
                inputs=[c_media_id, c_vlive_id, c_gid, c_auth, c_api_key, c_api_base, c_model, c_response_rate, c_auto_send],
                outputs=config_status
            )

    # Initial Load
    demo.load(
        load_configuration, 
        outputs=[c_media_id, c_vlive_id, c_gid, c_auth, c_api_key, c_api_base, c_model, c_response_rate, c_auto_send]
    )

if __name__ == "__main__":
    bot_state.initialize() # Pre-load config
    # Ensure handler is attached for startup logs
    logging.getLogger().addHandler(queue_handler)
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, inbrowser=True)
