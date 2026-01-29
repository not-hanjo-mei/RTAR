import gradio as gr

from ui.utils import api_get, api_post, api_put


def create_config_panel() -> gr.Blocks:
    with gr.Blocks() as config_panel:
        gr.Markdown("## Configuration")

        with gr.Tabs():
            with gr.Tab("REALITY Settings"):
                media_id = gr.Number(label="Media ID", precision=0, minimum=100000000, maximum=999999999)
                vlive_id = gr.Textbox(label="VLive ID", type="password")
                gid = gr.Textbox(label="GID (Group ID)", type="password")
                auth = gr.Textbox(label="Auth Token (Bearer ...)", type="password")

                save_reality_btn = gr.Button("Save REALITY Settings", variant="primary")

            with gr.Tab("Bot Settings"):
                nickname = gr.Textbox(label="Bot Nickname", value="RTAR Assistant")
                response_rate = gr.Slider(
                    label="Response Rate",
                    minimum=0.0,
                    maximum=1.0,
                    step=0.01,
                    value=1.0,
                )
                context_length = gr.Number(label="Context Length", value=20)

                save_bot_btn = gr.Button("Save Bot Settings")

            with gr.Tab("ADB Settings"):
                adb_host = gr.Textbox(label="ADB Host", value="127.0.0.1")
                adb_port = gr.Number(label="ADB Port", value=5555)
                auto_send = gr.Checkbox(label="Auto Send", value=True)

                with gr.Row():
                    input_x = gr.Number(label="Input Box X", value=540)
                    input_y = gr.Number(label="Input Box Y", value=1800)

                with gr.Row():
                    send_x = gr.Number(label="Send Button X", value=980)
                    send_y = gr.Number(label="Send Button Y", value=1800)

                save_adb_btn = gr.Button("Save ADB Settings")

            with gr.Tab("AI Settings"):
                api_base = gr.Textbox(label="API Base URL")
                api_key = gr.Textbox(label="API Key", type="password")
                model = gr.Textbox(label="Model Name")
                temperature = gr.Slider(
                    label="Temperature",
                    minimum=0.0,
                    maximum=2.0,
                    step=0.1,
                    value=0.7,
                )

                save_ai_btn = gr.Button("Save AI Settings")

            with gr.Tab("Character"):
                character_text = gr.Code(
                    label="Character Definition (character.md)",
                    language="markdown",
                    lines=20
                )
                save_character_btn = gr.Button("Save Character", variant="primary")

            with gr.Tab("Presets"):
                presets_text = gr.Code(
                    label="Preset Responses (presets.yaml)",
                    language="yaml",
                    lines=20
                )
                save_presets_btn = gr.Button("Save Presets", variant="primary")

        result_text = gr.Textbox(label="Result", interactive=False)

        async def load_config():
            try:
                config = await api_get("/config/")
                character_data = await api_get("/config/files/character")
                presets_data = await api_get("/config/files/presets")

                reality = config.get("reality", {})
                bot = config.get("bot", {})
                adb = config.get("adb", {})
                ai = config.get("ai", {}).get("llm", {})

                return (
                    reality.get("media_id", 0),
                    reality.get("vlive_id", ""),
                    reality.get("gid", ""),
                    reality.get("auth", ""),
                    bot.get("nickname", ""),
                    bot.get("response_rate", 1.0),
                    bot.get("context_length", 20),
                    adb.get("host", "127.0.0.1"),
                    adb.get("port", 5555),
                    adb.get("auto_send", True),
                    adb.get("input_box", [540, 1800])[0],
                    adb.get("input_box", [540, 1800])[1],
                    adb.get("send_button", [980, 1800])[0],
                    adb.get("send_button", [980, 1800])[1],
                    ai.get("api_base", ""),
                    ai.get("api_key", ""),
                    ai.get("model", ""),
                    ai.get("temperature", 0.7),
                    character_data.get("content", ""),
                    presets_data.get("content", ""),
                )
            except Exception:
                return (
                    0,
                    "",
                    "",
                    "",
                    "",
                    1.0,
                    20,
                    "127.0.0.1",
                    5555,
                    True,
                    540,
                    1800,
                    980,
                    1800,
                    "",
                    "",
                    "",
                    0.7,
                    "",
                    "",
                )

        async def save_reality_settings(mid, vid, g, a):
            try:
                await api_put("/config/", {"key": "reality.media_id", "value": int(mid)})
                await api_put("/config/", {"key": "reality.vlive_id", "value": vid})
                await api_put("/config/", {"key": "reality.gid", "value": g})
                await api_put("/config/", {"key": "reality.auth", "value": a})
                return "REALITY settings saved!"
            except Exception as e:
                return f"Error: {e}"

        async def save_bot_settings(nick, rate, ctx_len):
            try:
                await api_put("/config/", {"key": "bot.nickname", "value": nick})
                await api_put("/config/", {"key": "bot.response_rate", "value": rate})
                await api_put("/config/", {"key": "bot.context_length", "value": int(ctx_len)})
                return "Bot settings saved!"
            except Exception as e:
                return f"Error: {e}"

        async def save_adb_settings(host, port, auto, ix, iy, sx, sy):
            try:
                await api_put("/config/", {"key": "adb.host", "value": host})
                await api_put("/config/", {"key": "adb.port", "value": int(port)})
                await api_put("/config/", {"key": "adb.auto_send", "value": auto})
                await api_put("/config/", {"key": "adb.input_box", "value": [int(ix), int(iy)]})
                await api_put("/config/", {"key": "adb.send_button", "value": [int(sx), int(sy)]})
                return "ADB settings saved!"
            except Exception as e:
                return f"Error: {e}"

        async def save_ai_settings(base, key, mdl, temp):
            try:
                await api_put("/config/", {"key": "ai.llm.api_base", "value": base})
                await api_put("/config/", {"key": "ai.llm.api_key", "value": key})
                await api_put("/config/", {"key": "ai.llm.model", "value": mdl})
                await api_put("/config/", {"key": "ai.llm.temperature", "value": temp})
                return "AI settings saved!"
            except Exception as e:
                return f"Error: {e}"

        async def save_character_content(content):
            try:
                await api_post("/config/files/character", {"content": content})
                return "Character saved!"
            except Exception as e:
                return f"Error: {e}"

        async def save_presets_content(content):
            try:
                await api_post("/config/files/presets", {"content": content})
                return "Presets saved!"
            except Exception as e:
                return f"Error: {e}"

        config_panel.load(
            load_config,
            outputs=[
                media_id,
                vlive_id,
                gid,
                auth,
                nickname,
                response_rate,
                context_length,
                adb_host,
                adb_port,
                auto_send,
                input_x,
                input_y,
                send_x,
                send_y,
                api_base,
                api_key,
                model,
                temperature,
                character_text,
                presets_text,
            ],
        )

        save_reality_btn.click(
            save_reality_settings,
            inputs=[media_id, vlive_id, gid, auth],
            outputs=[result_text],
        )

        save_bot_btn.click(
            save_bot_settings,
            inputs=[nickname, response_rate, context_length],
            outputs=[result_text],
        )

        save_adb_btn.click(
            save_adb_settings,
            inputs=[adb_host, adb_port, auto_send, input_x, input_y, send_x, send_y],
            outputs=[result_text],
        )

        save_ai_btn.click(
            save_ai_settings,
            inputs=[api_base, api_key, model, temperature],
            outputs=[result_text],
        )

        save_character_btn.click(
            save_character_content,
            inputs=[character_text],
            outputs=[result_text],
        )

        save_presets_btn.click(
            save_presets_content,
            inputs=[presets_text],
            outputs=[result_text],
        )

    return config_panel
