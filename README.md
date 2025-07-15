# REALITY Auto Reply Tool

AI-powered automated chat responses for REALITY App live streams.

## 🚀 Features

- **Smart AI Responses**: Uses OpenAI API to generate contextual, engaging replies
- **Preset Responses**: Automatic replies for joins, likes, follows, and gifts
- **Customizable Personality**: Define your bot's character and response style
- **Real-time Processing**: Handles live chat messages in real-time
- **ADB Integration**: Direct device control for message sending
- **WebSocket Connection**: Reliable connection to REALITY App
- **Command Interface**: Interactive command-line interface
- **Health Monitoring**: Automatic reconnection and connection health checks

## 📁 Project Structure

```
RTAR/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── START.bat              # Windows startup script
├── START.sh               # Linux/macOS startup script
├── config/                # Configuration files
│   ├── config.json        # Main configuration
│   ├── presets.json       # Preset response templates
│   └── character.md       # AI personality definition
├── src/                   # Source code
│   ├── core/             # Core functionality
│   │   ├── config_manager.py
│   │   ├── websocket_client.py
│   │   ├── message_processor.py
│   │   └── response_generator.py
│   ├── models/           # Data models
│   │   ├── message.py
│   │   └── config_models.py
│   ├── utils/            # Utility modules
│   │   ├── adb_controller.py
│   │   ├── preset_manager.py
│   │   ├── character_loader.py
│   │   ├── url_parser.py
│   │   └── user_filter.py
│   └── handlers/         # Command handlers
│       ├── command_handler.py
│       └── input_handler.py
├── tests/                # Test files
└── .gitignore            # Git ignore rules
```

## 🛠️ Installation

### Prerequisites
- Python 3.12 or higher
- ADB (Android Debug Bridge) installed and configured
- REALITY App installed on your Android device / emulator

### Quick Setup

1. **Clone/Download the project**
2. **Run the startup script**
3. **Install dependencies** (automatic on first run):
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

### Basic Setup

1. **Edit `config/config.json`**:
   - Set your REALITY App credentials
   - Configure OpenAI API settings
   - Adjust bot behavior parameters

2. **Customize `config/character.md`**:
   - Define your bot's personality
   - Set response style guidelines

3. **Modify `config/presets.json`**:
   - Customize preset responses
   - Add new interaction types

### Key Configuration Options

```json
{
  "reality": {
    "mediaId": 123456789,
    "vLiveId": "your-vlive-id",
    "gid": "your-gid",
    "auth": "Bearer your-token"
  },
  "openai": {
    "apiKey": "your-openai-key",
    "apiBase": "https://api.openai.com/v1",
    "model": "gpt-4o",
    "temperature": 0.7
  },
  "bot": {
    "myNickname": "RTAT Assistant",
    "responseRate": 1.0,
    "contextLength": 20
  }
}
```

**Configuration Notes:**
- `mediaId`: Target live stream ID
- `vLiveId`: Your REALITY vLive ID
- `gid`: Group ID
- `auth`: Authentication token (Bearer format)
- `apiKey`: Your OpenAI API key
- `model`: AI model to use (gpt-4o, gpt-4o-mini, etc.)
- `temperature`: Response creativity (0.0-1.0)
- `myNickname`: Bot display name in chat
- `responseRate`: Probability of responding (0.0-1.0)
- `contextLength`: Number of messages to keep for context

## 🎯 Usage

### Starting the Application

```bash
python main.py
```

### Interactive Commands

Once running, use these commands:

- `/help` - Show all available commands
- `/stats` - Display processing statistics
- `/rate 0.5` - Set response probability to 50%
- `/send Hello everyone!` - Send a manual message
- `/config` - Show current configuration
- `/clear` - Clear message history
- `/exit` - Exit the application

### ADB Setup

1. **Enable USB Debugging** on your Android device:
   - Settings > Developer Options > USB Debugging

2. **Connect your device**:
   ```bash
   adb devices
   adb tcpip 5555
   adb connect YOUR_DEVICE_IP:5555
   ```

3. **Configure coordinates** in `config.json`:
   - Use `adb shell input tap x y` to find correct coordinates
   - Update `inputBox` and `sendButton` coordinates

## 🔧 Advanced Configuration

### Custom Character Personality

Edit `config/character.md` to define your bot's personality:

```markdown
# AI Assistant Personality

You are a friendly gaming stream chat bot...
- Keep responses under 100 characters
- Use emojis appropriately
- Focus on gaming-related discussions
```

### Custom Preset Responses

Modify `config/presets.json`:

```json
{
  "custom_event": {
    "description": "Custom event description",
    "replies": [
      "Custom response 1 for {username}",
      "Custom response 2 for {username}"
    ]
  }
}
```

## 🐛 Troubleshooting

### Common Issues

**Connection Issues**:
- Check REALITY App credentials in config
- Verify WebSocket URL accessibility
- Ensure proper network connection

**ADB Problems**:
- Confirm ADB is installed: `adb version`
- Check device connection: `adb devices`
- Verify device authorization

**API Issues**:
- Validate OpenAI API key
- Check API rate limits
- Verify model availability

## 📊 Monitoring

The application provides real-time monitoring:

- Message processing statistics
- WebSocket connection health
- ADB connection status
- AI response generation metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is provided as-is for educational and personal use.

## 🔗 Related Resources

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Android ADB Documentation](https://developer.android.com/studio/command-line/adb)
- [REALITY App](https://reality.app)