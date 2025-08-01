"""
Reset to default IME settings:
adb shell ime reset

Enable ADBKeyBoard from adb:
adb shell ime enable com.android.adbkeyboard/.AdbIME

Switch to ADBKeyBoard from adb (by robertio):
adb shell ime set com.android.adbkeyboard/.AdbIME   
"""

import time
from src.utils.adb_controller import ADBController
from src.core.config_manager import ConfigManager

config = ConfigManager()
adb = ADBController(config)

adb.connect()
time.sleep(2)

adb.adb_command("shell ime reset")
time.sleep(0.5) 
adb.adb_command("shell ime enable com.android.adbkeyboard/.AdbIME")
time.sleep(0.5)
adb.adb_command("shell ime set com.android.adbkeyboard/.AdbIME")
time.sleep(0.5)
adb.adb_command("shell am start -n com.bluestacks.settings/com.bluestacks.settings.InputMethodSettings")
print("Please manually enable onscreen keyboard in BlueStacks settings.")
