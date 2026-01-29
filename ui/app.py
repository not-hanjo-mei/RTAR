import gradio as gr

from ui.components.chat_panel import create_chat_panel
from ui.components.config_panel import create_config_panel
from ui.components.dashboard import create_dashboard
# from ui.components.logs_panel import create_logs_panel

def create_ui() -> gr.Blocks:
    with gr.Blocks(title="RTAR - REALITY Auto Reply Tool") as app:
        gr.Markdown("# RTAR - REALITY Auto Reply Tool")

        with gr.Tabs():
            with gr.Tab("Dashboard"):
                create_dashboard()

            with gr.Tab("Chat"):
                create_chat_panel()

            with gr.Tab("Configuration"):
                create_config_panel()

            # Logs disabled - using terminal/logs file instead
            # with gr.Tab("Logs"):
            #     create_logs_panel()

    return app
