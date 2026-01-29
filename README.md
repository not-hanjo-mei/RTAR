# RTAR (REALITY Auto Reply Tool)

AI-powered automated chat system for REALITY App live streams.

## Features

- **Smart AI Responses**: Generates contextual, engaging replies using OpenAI-compatible APIs
- **Full Conversation Context**: Maintains chat history for coherent multi-turn conversations
- **Preset Responses**: Automatic replies for joins, likes, follows, and gifts
- **Customizable Personality**: Define your bot's character and response style
- **Real-time Processing**: Handles live chat messages via WebSocket
- **ADB Integration**: Direct device control for message sending
- **MCP Protocol Support**: Integrates with Claude/Cursor via Model Context Protocol
- **REST API**: Full HTTP API for programmatic control
- **Gradio WebUI**: User-friendly web interface for monitoring and configuration
- **Pure Async**: Architecture built on asyncio for high performance
- **Text-to-Speech (TTS)**: Bot can speak responses with configurable voices and per-response-type control


## Architecture

RTAR features a modular, event-driven architecture:

```
+-----------------------------------------------------------------------------+
|                                   RTAR                                      |
+-----------------------------------------------------------------------------+
|                                                                             |
|  +-----------+    +---------------------------------------------+           |
|  |  Gradio   |<-->|              FastAPI Backend                |           |
|  |  WebUI    |    |        REST API + WebSocket events          |           |
|  +-----------+    +---------------------------------------------+           |
|                   |                                             |           |
|  +-----------+    |  +---------------------------------------+  |           |
|  |    MCP    |<-->|  |          MCP Protocol Layer           |  |           |
|  |  Server   |    |  |       Tools, Resources, Prompts       |  |           |
|  +-----------+    |  +---------------------------------------+  |           |
|                   +---------------------------------------------+           |
|                                      |                                      |
|                   +------------------+------------------+                   |
|                   v                  v                  v                   |
|  +-------------------+ +-------------------+ +-------------------+          |
|  |   Service Layer   | |   Service Layer   | |   Service Layer   |          |
|  | Chat Service      | |   AI Service      | |   Device Service  |          |
|  | - WebSocket       | | - LLM Client      | | - ADB Control     |          |
|  | - Message Queue   | | - TTS/ASR Ready   | | - Input Simulation|          |
|  | - Context Mgmt    | |                   | |                   |          |
|  +-------------------+ +-------------------+ +-------------------+          |
|                                      |                                      |
|                   +------------------+------------------+                   |
|                   v                                     v                   |
|  +---------------------------------+ +---------------------------------+    |
|  |        Core Layer               | |        Infrastructure           |    |
|  |      Models (Pydantic)          | |     Config & Logging System     |    |
|  |      Event Bus (Pub/Sub)        | |     Dependency Injection        |    |
|  +---------------------------------+ +---------------------------------+    |
|                                                                             |
+-----------------------------------------------------------------------------+
```

## Project Structure

```
rtar/
├── fix_adb_kbd.py              # ADB Keyboard fix script for BlueStacks Emulator
├── main.py                     # Application entry point
├── pyproject.toml              # Project dependencies
├── START.bat                   # Windows start script (cmd)
├── START.ps1                   # Windows start script (PowerShell)
├── config/
│   ├── config.yaml             # Configuration file
│   ├── character.md            # AI personality definition
│   └── presets.yaml            # Preset responses
│
├── src/
│   ├── api/                    # REST API Layer
│   │   ├── app.py              # FastAPI application factory
│   │   ├── routes/             # API endpoints
│   │   ├── websocket/          # WebSocket event handlers
│   │   └── dependencies.py     # Dependency injection
│   │
│   ├── mcp/                    # MCP Protocol Layer
│   │   ├── server.py           # MCP Server implementation
│   │   ├── tools/              # MCP Tools (chat/AI/device/config)
│   │   ├── resources/          # MCP Resources
│   │   └── prompts/            # MCP Prompt templates
│   │
│   ├── services/               # Service Layer
│   │   ├── chat/               # Chat orchestration
│   │   ├── ai/                 # AI services (LLM/TTS/ASR)
│   │   └── device/             # Device control
│   │
│   ├── core/                   # Core Layer
│   │   ├── models/             # Domain models (Pydantic)
│   │   └── events/             # Event bus (pub/sub)
│   │
│   └── infra/                  # Infrastructure
│       ├── config.py           # Configuration loader
│       ├── logging.py          # Logging setup
│       └── container.py        # DI container
│
└── ui/                         # Gradio WebUI
    ├── app.py                  # Gradio app definition
    └── components/             # UI components


```

## Installation

### Prerequisites

- Python 3.11 or higher
- ADB (Android Debug Bridge) installed
- REALITY App on Android device/emulator
- OpenAI-compatible API endpoint

### Quick Start

```bash
# Clone the repository
git clone https://github.com/not-hanjo-mei/RTAR
cd RTAR

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Copy configuration template
cp config/config.yaml.example config/config.yaml
cp config/presets.yaml.example config/presets.yaml
cp config/character.md.example config/character.md

# Edit configuration
# - Set your REALITY credentials
# - Configure AI endpoint
# - Adjust ADB coordinates

# Run the application
python main.py

# WebUI available at: http://localhost:42069/ui
```

### Configuration

Edit `config/config.yaml`:

```yaml
reality:
  media_id: 123456789
  vlive_id: "your-vlive-id"
  gid: "your-gid"
  auth: "Bearer your-token"

ai:
  llm:
    api_base: "https://api.openai.com/v1"
    api_key: "sk-xxx"
    model: "gpt-4o"
    temperature: 0.7
    max_tokens: 8192

adb:
  host: "127.0.0.1"
  port: 5555
  input_box: [540, 1800]
  send_button: [980, 1800]
  auto_send: true
  send_delay: [0.2, 0.5]

bot:
  nickname: "RTAR Assistant"
  vlive_id: "bot-vlive-id"  # Optional: separate bot account
  response_rate: 1.0
  context_length: 20

ai:
  tts:
    enabled: false          # Enable TTS for bot responses
    voice: "alloy"          # Voice: alloy, echo, fable, onyx, nova, shimmer
    volume: 1.0             # Volume (0.0-1.0)
    response_types:
      - "chat"              # TTS enabled for chat responses
      # - "gift"            # Enable for gift responses
      # - "like"            # Enable for like responses
      # - "follow"          # Enable for follow responses
log_level: "WARNING"

```

### ADB Setup

```bash
# Enable USB debugging on device or emulator
# Settings > Developer Options > USB Debugging

# Connect device
adb devices
adb tcpip 5555
adb connect YOUR_DEVICE_IP:5555

# Find coordinates (adjust in config.yaml)
adb shell input tap 540 1800  # Test tap
```

## Usage

### Web Application

Start the web server (default port 42069):

```bash
python main.py
```

Access:
- **API Docs**: http://localhost:42069/docs
- **Gradio UI**: http://localhost:42069/ui

### MCP Server

Run as MCP server (for Claude/Cursor):

```bash
python main.py --mcp
```

Configure in your MCP client (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "rtar": {
      "command": "python",
      "args": ["C:\\path\\to\\RTAR\\main.py", "--mcp"]
    }
  }
}
```

### REST API

#### Chat Endpoints

```bash
# Send message
POST /api/v1/chat/send
{"text": "Hello everyone!"}

# Get context
GET /api/v1/chat/context?limit=20

# Get stats
GET /api/v1/chat/stats

# Clear history
DELETE /api/v1/chat/history
```

#### AI Endpoints

```bash
# Generate response
POST /api/v1/ai/generate
{
  "message": "Hello",
  "username": "Alice",
  "include_context": true
}

# Text to Speech
POST /api/v1/ai/tts
{
  "text": "Hello world!",
  "voice": "alloy",
  "play": true,         # Optional: Play audio locally on server (default: false)
  "volume": 1.0         # Optional: Volume (0.0-1.0, default: 1.0)
}

# Speech to Text
POST /api/v1/ai/asr
{
  "audio_base64": "...",
  "language": "en"
}
```


#### Device Endpoints

```bash
# Connect ADB
POST /api/v1/device/connect

# Get status
GET /api/v1/device/status

# Tap coordinates
POST /api/v1/device/tap
{"x": 540, "y": 1800}

# Input text
POST /api/v1/device/input
{"text": "Hello"}

# Screenshot
GET /api/v1/device/screenshot?format=base64
```

#### Config Endpoints

```bash
# Get all config
GET /api/v1/config/

# Get section
GET /api/v1/config/bot

# Update config
PUT /api/v1/config/
{"key": "bot.response_rate", "value": 0.5}

# Reload from file
POST /api/v1/config/reload
```

#### Control Endpoints

```bash
# Start bot
POST /api/v1/control/start

# Stop bot
POST /api/v1/control/stop

# Get status
GET /api/v1/control/status
```

### MCP Tools

Available MCP tools for AI assistants:

| Tool | Description |
|------|-------------|
| `send_message` | Send message to REALITY chat |
| `get_chat_context` | Get recent chat messages |
| `generate_response` | Generate AI response with context |
| `text_to_speech` | Convert text to speech (TTS) |
| `speech_to_text` | Transcribe audio to text (ASR) |
| `adb_tap` | Tap at screen coordinates |
| `adb_input` | Input text via ADB |
| `screenshot` | Take device screenshot |
| `get_config` | Read configuration |
| `set_config` | Update configuration |
| `start_bot` | Start the bot |
| `stop_bot` | Stop the bot |

## Customization

### Bot Personality

Edit `config/character.md` to define your bot's personality:

```markdown
# AI Assistant Personality

You are a friendly gaming stream chat bot...

## Behavior Guidelines
- Keep responses under 100 characters
- Use appropriate emojis
- Focus on gaming-related discussions
- Maintain conversational context

## Response Style
- Casual and engaging
- Ask follow-up questions
- Reference ongoing stream activities
```

### Preset Responses

Edit `config/presets.yaml`:

```yaml
greetings:
  default:
    - Welcome {user}!
    - Hi {user}, glad you're here!

likes:
  default:
    - Thanks for the like, {user}!
    - {user} sent some love!

gifts:
  default:
    - Wow, thanks {user}!
    - A gift from {user}!
```

### Context Management

The bot maintains conversation history:

- **User messages**: `[Alice]: Hello!`
- **Assistant messages**: `Hi Alice! Welcome!`
- **Alternating pattern**: User → Assistant → User → Assistant
- **Context window**: Configurable (default: 20 messages)
- **Automatic pruning**: Oldest messages removed when limit reached

### Event Bus

All components communicate via async events:

```python
EventType.MESSAGE_RECEIVED
EventType.MESSAGE_PROCESSED
EventType.RESPONSE_GENERATED
EventType.RESPONSE_SENT
EventType.WS_CONNECTED
EventType.LLM_REQUEST
# ... and more
```

### Multiple AI Endpoints

Configure different endpoints for LLM/TTS/ASR:

```yaml
ai:
  llm:
    api_base: "https://api.openai.com/v1"
    model: "gpt-4o"

  tts:  # Optional, inherits from llm if not set
    api_base: "https://different-endpoint.com/v1"
    model: "tts-1"

  asr:  # Optional, inherits from llm if not set
    api_base: "https://another-endpoint.com/v1"
    model: "whisper-1"
```

### TTS Configuration

Enable Text-to-Speech for bot responses:

```yaml
ai:
  tts:
    enabled: true          # Enable bot TTS
    voice: "alloy"          # Voice selection
    volume: 1.0             # Audio volume (0.0-1.0)
    response_types:         # Which response types to speak
      - "chat"             # Chat messages from viewers
      - "gift"             # Gift responses
      - "like"             # Like responses
      - "follow"           # Follow responses
```

**Available Voices:**
- `alloy` (default)
- `echo`
- `fable`
- `onyx`
- `nova`
- `shimmer`

**TTS Playback:**
- Bot automatically speaks responses when `ai.tts.enabled: true`
- Audio plays locally on the host machine
- Configure per-response-type control (e.g., only speak chat messages, not likes)
- Test TTS via the Gradio UI "TTS Test" tab at `http://localhost:42069/ui`

## Troubleshooting


### Connection Issues

**REALITY WebSocket**:
- Verify credentials in `config.yaml`
- Check network connectivity
- Ensure `media_id` and `vlive_id` are correct

**ADB Connection**:
```bash
adb devices  # Check device list
adb tcpip 5555  # Enable TCP mode
adb connect IP:5555  # Connect
```

### AI Not Responding

- Check API key and endpoint
- Verify `response_rate` in config (1.0 = always respond)
- Check logs with `log_level: "DEBUG"`
- Verify `bot.vlive_id` doesn't match your account

### Context Not Working

- Ensure `bot.vlive_id` is set correctly
- Check `context_length` in config
- Verify messages are being sent/received

### No Messages Being Processed

- Check WebSocket connection status
- Verify `response_rate` > 0
- Ensure messages pass type filter (text/join/like/gift/follow)
- Check if bot's own messages are being filtered
- **Note**: Messages received when connection starts are filtered if older than bot start time - this is expected behavior

### TTS Not Playing

- Verify `ai.tts.enabled: true` in config.yaml
- Check that TTS endpoint is configured (inherits from LLM if separate TTS endpoint not set)
- Ensure the response type is in `ai.tts.response_types` list
- Check pygame is installed: `pip list | grep pygame`
- Verify audio output on host machine is working
- Check logs for TTS errors with `log_level: "DEBUG"`
- Test TTS manually via the "TTS Test" tab in Gradio UI


## License

GNU Affero General Public License v3.0 (AGPL-3.0)

See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Related Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Android ADB Documentation](https://developer.android.com/studio/command-line/adb)
- [REALITY App](https://reality.app)
