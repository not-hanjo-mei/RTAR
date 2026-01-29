import gradio as gr


def create_logs_panel() -> gr.Blocks:
    with gr.Blocks() as logs_panel:
        gr.Markdown("## Logs")

        log_output = gr.Textbox(
            label="Application Logs",
            lines=20,
            max_lines=50,
            interactive=False,
        )

        with gr.Row():
            refresh_btn = gr.Button("Refresh Logs")
            clear_btn = gr.Button("Clear Display")

        log_level = gr.Dropdown(
            label="Log Level Filter",
            choices=["ALL", "DEBUG", "INFO", "WARNING", "ERROR"],
            value="INFO",
        )

        def refresh_logs(level: str):
            return f"Logs will be displayed here when the application is running.\nFilter: {level}\n\nConnect to WebSocket at ws://localhost:7860/ws/events for real-time updates."

        def clear_logs():
            return ""

        refresh_btn.click(refresh_logs, inputs=[log_level], outputs=[log_output])
        clear_btn.click(clear_logs, outputs=[log_output])

        logs_panel.load(refresh_logs, inputs=[log_level], outputs=[log_output])

    return logs_panel
