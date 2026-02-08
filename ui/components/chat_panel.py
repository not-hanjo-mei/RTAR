from datetime import UTC, datetime

import gradio as gr

from ui.utils import api_delete, api_get, api_post


def create_chat_panel() -> gr.Blocks:
    with gr.Blocks() as chat_panel:
        gr.Markdown("## Chat Monitor")

        with gr.Row():
            with gr.Column(scale=3):
                chat_history = gr.Dataframe(
                    headers=["Time", "User", "Message"],
                    column_widths=["25%", "25%", "50%"],
                    label="Chat History",
                    interactive=False,
                )

                refresh_btn = gr.Button("Refresh")
                clear_btn = gr.Button("Clear History", variant="stop")

            with gr.Column(scale=1):
                gr.Markdown("### Send Message")
                message_input = gr.Textbox(
                    label="Message",
                    placeholder="Enter message to send...",
                )
                send_btn = gr.Button("Send", variant="primary")
                send_result = gr.Textbox(label="Result", interactive=False)

                gr.Markdown("### Generate Response")
                gen_message = gr.Textbox(label="Message")
                gen_username = gr.Textbox(label="Username", value="User")
                gen_btn = gr.Button("Generate")
                gen_result = gr.Textbox(label="Generated Response", interactive=False)

        async def refresh_chat():
            try:
                data = await api_get("/chat/context?limit=50")
                messages = data.get("messages", [])
                rows = []
                for msg in messages:
                    ts_str = msg.get("timestamp", "")
                    if ts_str:
                        try:
                            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=UTC)
                            dt_local = dt.astimezone()
                            time_str = dt_local.strftime("%Y-%m-%d %H:%M:%S")
                        except (ValueError, AttributeError):
                            time_str = ts_str[:19]
                    else:
                        time_str = ""
                    user = msg.get("display_name", "")
                    content = msg.get("content", "")
                    rows.append([time_str, user, content])
                return rows
            except Exception:
                return []

        async def send_message(msg):
            if not msg:
                return "Please enter a message"
            try:
                result = await api_post("/chat/send", {"message": msg})
                if result.get("success"):
                    return "Message sent!"
                return "Failed to send"
            except Exception as e:
                return f"Error: {e}"

        async def clear_history():
            try:
                await api_delete("/chat/history")
                return []
            except Exception:
                return []

        async def generate_response(msg, user):
            if not msg:
                return "Please enter a message"
            try:
                result = await api_post(
                    "/ai/generate",
                    {
                        "message": msg,
                        "username": user or "User",
                        "include_context": True,
                    },
                )
                return result.get("response", "")
            except Exception as e:
                return f"Error: {e}"

        refresh_btn.click(refresh_chat, outputs=[chat_history])
        clear_btn.click(clear_history, outputs=[chat_history])
        send_btn.click(send_message, inputs=[message_input], outputs=[send_result])
        gen_btn.click(
            generate_response,
            inputs=[gen_message, gen_username],
            outputs=[gen_result],
        )

        chat_panel.load(refresh_chat, outputs=[chat_history])

    return chat_panel
