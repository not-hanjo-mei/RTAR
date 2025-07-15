# Configuration Guide

This directory contains all configuration files for RTAR. You can customize these to fit your specific needs.

## 📁 Configuration Files

### Core Files
- **`config.json.example`** - Main configuration template (copy to `config.json`)
- **`presets.json.example`** - Preset response templates (copy to `presets.json`)
- **`character.md.example`** - AI personality definition (copy to `character.md`)

### Quick Setup
1. Copy the `.example` files to remove the `.example` extension
2. Edit the values to match your setup
3. Never commit your actual configuration files to version control

## 🔧 Configuration Sections

### REALITY App Settings
Configure your REALITY App connection:
- `mediaId`: Target live stream ID
- `vLiveId`, `gid`, `auth`: Get these from browser developer tools

### OpenAI Settings
Set up your AI provider:
- `apiKey`: Your OpenAI API key
- `model`: free:QwQ-32B (default) or gpt-4
- `temperature`: 0.1-2.0 (lower = more focused)

### ADB Settings
Configure device connection:
- `host`: Usually 127.0.0.1 for local ADB
- `port`: 5555 for bluestacks
- `inputBox`/`sendButton`: Coordinates for your specific device

### Bot Settings
Customize bot behavior:
- `myNickname`: Display name in chat
- `responseRate`: 0.0-1.0 (probability of responding)
- `contextLength`: Messages to use as context

## 📋 Getting Credentials

### REALITY App Credentials

**TO BE DONE**
1. Open REALITY App in browser
2. Press F12 to open developer tools
3. Go to Network tab
4. Look for WebSocket connections
5. Find headers: `X-WFLE-vLiveID`, `X-WFLE-GID`, `Authorization`
**TO BE DONE**

### ADB Setup
1. Enable USB debugging on Android device
2. Connect via USB and run: `adb tcpip 5555`
3. Find device IP: `adb shell ip route`
4. Connect wirelessly: `adb connect DEVICE_IP:5555`
5. Calibrate coordinates using: `adb shell input tap x y`

## 🔍 Troubleshooting

### Common Issues
- **"Connection failed"**: Check REALITY App credentials
- **"ADB not connected"**: Verify ADB setup and coordinates
- **"API key invalid"**: Check OpenAI account and billing

### Debug Mode
Enable debug mode in config.json to see detailed logs:
```json
"debug": {"value": true}
```

## 📝 Best Practices

1. **Always backup** your working configuration
2. **Test changes** in a controlled environment first
3. **Document customizations** for future reference
4. **Use environment variables** for sensitive data in production
5. **Regular updates** when REALITY App changes their API

## 🚀 Quick Start

1. Copy example files:
   ```bash
   cp config.json.example config.json
   cp presets.json.example presets.json
   cp character.md.example character.md
   ```

2. Edit with your actual values
3. Start the application