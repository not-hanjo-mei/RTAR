#!/usr/bin/env python
"""
Setup and enable ADBKeyboard for RTAR text input.
Run this when BlueStacks resets IME settings.
"""

import sys
import time
import urllib.request
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command synchronously and return exit code, stdout, stderr."""
    import subprocess

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def get_default_device() -> str | None:
    """Get the default device address, preferring emulator."""
    code, stdout, stderr = run_command(["adb", "devices"])
    if code != 0:
        return None

    for line in stdout.strip().split("\n"):
        if "emulator" in line:
            parts = line.split()
            if parts:
                return parts[0]

    return None


def download_adbkeyboard(save_path: Path) -> bool:
    """Download ADBKeyboard.apk from GitHub releases."""
    url = "https://raw.githubusercontent.com/senzhk/ADBKeyBoard/refs/heads/master/ADBKeyboard.apk"

    print(f"Downloading ADBKeyboard from GitHub...")
    try:
        urllib.request.urlretrieve(url, save_path)
        print(f"Downloaded: {save_path}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to download ADBKeyboard: {e}")
        return False


def check_adb_keyboard_installed() -> bool:
    """Check if ADBKeyboard is installed on the device."""
    code, stdout, stderr = run_command(device_prefix + ["shell", "pm", "list", "packages"])

    if code == 0:
        return "com.android.adbkeyboard" in stdout or "ADBKeyboard" in stdout
    return False


def install_adb_keyboard(apk_path: Path) -> bool:
    """Install ADBKeyboard APK from given path."""
    if not apk_path.exists():
        print(f" ERROR: APK file not found: {apk_path}")
        return False

    print(f"Installing ADBKeyboard from: {apk_path}")
    code, stdout, stderr = run_command(device_prefix + ["install", "-r", str(apk_path)])

    if code == 0:
        print("ADBKeyboard installed successfully")
        return True
    else:
        print(f"Installation failed: {stderr}")
        return False


def setup_adb_keyboard() -> None:
    """Setup and enable ADBKeyboard."""
    global device_prefix
    device_id = get_default_device()

    if not device_id:
        print("ERROR: No ADB device connected")
        sys.exit(1)

    device_prefix = ["adb", "-s", device_id]

    print("=" * 60)
    print("ADBKeyboard Setup for RTAR")
    print("=" * 60)
    print(f"Target device: {device_id}")
    print()
    print()

    print("Checking for ADBKeyboard installation...")
    if check_adb_keyboard_installed():
        print("ADBKeyboard is already installed")
    else:
        print("ADBKeyboard is NOT installed")
        print("Searching for adb-related packages...")

        code, stdout, _ = run_command(
            device_prefix + ["shell", "pm", "list", "packages", "|", "grep", "-i", "adb"]
        )
        if stdout.strip():
            print("Found packages:")
            print(stdout)
        print()

        choice = input("Download and install ADBKeyboard from GitHub? [y/N]: ").strip().lower()

        if choice == "y":
            apk_path = Path("ADBKeyboard.apk")
            if not download_adbkeyboard(apk_path):
                sys.exit(1)

            if not install_adb_keyboard(apk_path):
                sys.exit(1)

            apk_path.unlink(missing_ok=True)
            print()
        else:
            print("Setup cancelled. You can install ADBKeyboard manually.")
            print("Download from: https://github.com/senzhk/ADBKeyBoard")
            sys.exit(0)

    print("Resetting IME settings...")
    code, stdout, stderr = run_command(device_prefix + ["shell", "ime", "reset"])

    if code == 0:
        print("IME reset successful")
    else:
        print(f"Warning: IME reset failed: {stderr}")
    print()

    print("Enabling ADBKeyboard...")
    code, stdout, stderr = run_command(
        device_prefix + ["shell", "ime", "enable", "com.android.adbkeyboard/.AdbIME"]
    )

    if code == 0:
        print("ADBKeyboard enabled")
    else:
        print(f"ERROR: Failed to enable ADBKeyboard: {stderr}")
        sys.exit(1)
    print()

    print("Setting ADBKeyboard as default IME...")
    code, stdout, stderr = run_command(
        device_prefix + ["shell", "ime", "set", "com.android.adbkeyboard/.AdbIME"]
    )

    if code == 0:
        print("ADBKeyboard set as default IME")
    else:
        print(f"ERROR: Failed to set ADBKeyboard: {stderr}")
        sys.exit(1)
    print()

    print("Verifying current IME...")
    code, stdout, stderr = run_command(device_prefix + ["shell", "ime", "list", "-s"])

    if code == 0 and "com.android.adbkeyboard/.AdbIME" in stdout:
        print("Current IME: ADBKeyboard")
    else:
        print("Current IME:")
        print(stdout)
        print("WARNING: ADBKeyboard may not be the active IME")
    print()

    print("=" * 60)
    print("ADBKeyboard setup completed!")
    print("Please enable screen keyboard in BlueStacks emulator settings if needed.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        setup_adb_keyboard()
    except KeyboardInterrupt:
        print("\nSetup cancelled by user")
        sys.exit(1)
