import gradio as gr

from ui.utils import api_post

def create_tts_panel() -> gr.Blocks:
    with gr.Blocks() as tts_panel:
        gr.Markdown("## Text-to-Speech Test")

        with gr.Row():
            with gr.Column(scale=3):
                text_input = gr.Textbox(
                    label="Text to Speak",
                    placeholder="Enter text here...",
                    lines=3,
                )

            with gr.Column(scale=1):
                model_dropdown = gr.Dropdown(
                    choices=["tts-1", "tts-1-hd", "gpt-4o-mini-tts"],
                    value="tts-1",
                    label="Model",
                    allow_custom_value=True,
                    info="TTS model to use",
                )
                # voice_dropdown = gr.Dropdown(
                #     choices=TTS_VOICES,
                #     value="alloy",
                #     label="Voice",
                #     allow_custom_value=True,
                #     info="Select from list or type any voice name",
                # )
                voice_textbox = gr.Textbox(
                    label="Voice",
                    placeholder="e.g., alloy, bella, etc.",
                    value="alloy",
                    info="TTS voice to use",
                )
                speed_slider = gr.Slider(
                    minimum=0.25,
                    maximum=4.0,
                    step=0.05,
                    value=1.0,
                    label="Speed",
                    info="0.25 = slow, 1.0 = normal, 4.0 = fast",
                )
                volume_slider = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    step=0.1,
                    value=1.0,
                    label="Volume",
                )
                instructions_input = gr.Textbox(
                    label="Instructions (Optional)",
                    placeholder="e.g., Speak in a cheerful tone...",
                    info="Only works with gpt-4o-mini-tts",
                    lines=2,
                )
                play_btn = gr.Button("🔊 Generate & Play", variant="primary", size="lg")

        status_text = gr.Textbox(label="Status", value="Ready", interactive=False)

        async def generate_and_play(
            text: str, model: str, voice: str, speed: float, volume: float, instructions: str
        ) -> str:
            if not text:
                return "Please enter some text."

            try:
                payload = {
                    "text": text,
                    "model": model,
                    "voice": voice,
                    "speed": speed,
                    "play": True,
                    "volume": volume,
                }
                if instructions.strip():
                    payload["instructions"] = instructions.strip()

                await api_post("/ai/tts", payload)
                return f"Spoken: {text[:50]}{'...' if len(text) > 50 else ''}"
            except Exception as e:
                return f"Error: {e}"

        play_btn.click(
            generate_and_play,
            inputs=[
                text_input,
                model_dropdown,
                # voice_dropdown,
                voice_textbox,
                speed_slider,
                volume_slider,
                instructions_input,
            ],
            outputs=status_text,
        )

    return tts_panel
