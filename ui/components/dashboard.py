import gradio as gr

from ui.utils import api_get, api_post


def create_dashboard() -> gr.Blocks:
    with gr.Blocks() as dashboard:
        gr.Markdown("## RTAR Dashboard")

        with gr.Row():
            with gr.Column(scale=1):
                status_text = gr.Textbox(
                    label="Status",
                    value="Not Connected",
                    interactive=False,
                )

                with gr.Row():
                    start_btn = gr.Button("Start Bot", variant="primary")
                    stop_btn = gr.Button("Stop Bot", variant="stop")

                refresh_btn = gr.Button("Refresh Status")

            with gr.Column(scale=2):
                stats_json = gr.JSON(label="System Stats")

        async def refresh_status():
            try:
                status = await api_get("/config/control/status")
                running = status.get("running", False)
                ws = status.get("ws_connected", False)
                adb = status.get("adb_connected", False)

                status_str = f"Running: {'Yes' if running else 'No'} | WS: {'Connected' if ws else 'Disconnected'} | ADB: {'Connected' if adb else 'Disconnected'}"
                return status_str, status
            except Exception as e:
                return f"Error: {e}", {}

        async def start_bot():
            try:
                await api_post("/config/control/start")
                return await refresh_status()
            except Exception as e:
                return f"Error: {e}", {}

        async def stop_bot():
            try:
                await api_post("/config/control/stop")
                return await refresh_status()
            except Exception as e:
                return f"Error: {e}", {}

        refresh_btn.click(refresh_status, outputs=[status_text, stats_json])
        start_btn.click(start_bot, outputs=[status_text, stats_json])
        stop_btn.click(stop_bot, outputs=[status_text, stats_json])

        dashboard.load(refresh_status, outputs=[status_text, stats_json])

    return dashboard
