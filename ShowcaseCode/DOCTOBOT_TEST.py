#!/usr/bin/env python3
"""
DoctoBot test script with Mock Serial and Mocked APIs.
"""

import sys
from unittest.mock import MagicMock

# Pre-mocking modules that might be missing
mock_cv2 = MagicMock()
sys.modules["cv2"] = mock_cv2
mock_vlc = MagicMock()
sys.modules["vlc"] = mock_vlc
mock_serial = MagicMock()
sys.modules["serial"] = mock_serial
mock_pymongo = MagicMock()
sys.modules["pymongo"] = mock_pymongo
mock_genai = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = mock_genai
mock_elevenlabs = MagicMock()
sys.modules["elevenlabs"] = mock_elevenlabs
sys.modules["elevenlabs.client"] = mock_elevenlabs

import json
import multiprocessing
import os
import secrets
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

# Re-importing to use the mocked versions in the script
import serial
import vlc
import cv2
import google.generativeai as genai
from elevenlabs.client import ElevenLabs
from elevenlabs import play as el_play
from pymongo import MongoClient

# Mocking External Dependencies for Testing
class MockSerial:
    def __init__(self, port, baud, timeout=1):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.in_waiting = 0
        self.buffer = []
        self.is_open = True

    def readline(self):
        if self.buffer:
            line = self.buffer.pop(0)
            self.in_waiting = len(self.buffer)
            return line.encode('utf-8')
        return b""

    def write(self, data):
        cmd = data.decode('utf-8').strip()
        print(f"[MOCK SERIAL] Received command: {cmd}")
        if cmd == "START_SENSORS":
            # Simulate sensor data after a short delay
            time.sleep(1)
            response = json.dumps({"temp": 37.5, "bpm": 80, "spo2": 98})
            self.buffer.append(response)
            self.in_waiting = 1
        return len(data)

    def close(self):
        self.is_open = False

# Patching serial.Serial
serial.Serial = MockSerial

# Mocking other hardware/API calls
vlc.MediaPlayer = MagicMock()
cv2.VideoCapture = MagicMock()
cv2.imwrite = MagicMock()
el_play = MagicMock()
ElevenLabs = MagicMock()
MongoClient = MagicMock()
genai.configure = MagicMock()
genai.GenerativeModel = MagicMock()

# --- Original Logic Starts Here (Simplified for Test Run) ---

load_dotenv()

SERIAL_PORT: str = os.getenv("SERIAL_PORT", "/dev/ttyACM0")
SERIAL_BAUD: int = int(os.getenv("SERIAL_BAUD", "115200"))
MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "doctobot")
ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_AGENT_ID: str = os.getenv("ELEVENLABS_AGENT_ID", "")
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

IDLE_INTERVAL = 5 # Reduced for test
WAIT_INTERVAL = 2 # Reduced for test

# Mock DB Collections
db_mock = MagicMock()
users_col = db_mock['users']
sessions_col = db_mock['sessions']
users_col.find_one.return_value = {"fpid": 1, "name": "Test User"}

# Mock Gemini Response
gemini_model = MagicMock()
gemini_model.generate_content.return_value.text = "NORMAL"

el_client = MagicMock()

class AnimationManager:
    def __init__(self) -> None:
        self.process = None
        self.current_key = None

    def play(self, key: str) -> None:
        print(f"[ANIMATION] Playing: {key}")
        self.current_key = key

    def stop(self) -> None:
        print("[ANIMATION] Stopped")

anim: AnimationManager = AnimationManager()

def play_audio(path: Union[str, Path]) -> None:
    print(f"[AUDIO] Playing: {path}")

def speak_eleven(text: str) -> None:
    print(f"[TTS] Speaking: {text}")

class DoctoBot:
    def __init__(self) -> None:
        self.ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
        self.current_user: Optional[Dict[str, Any]] = None
        self.last_fp_time: float = 0.0

    def start_test(self) -> None:
        print("Starting DoctoBot Test Sequence...")
        
        # 1. Simulate Idle State
        print("\n--- Phase 1: Idle ---")
        anim.play("ANIMATION_PATH0")
        play_audio("./voices/FP.mp3")
        
        # 2. Simulate Fingerprint Found
        print("\n--- Phase 2: User Detected ---")
        fpid = 1
        self.ser.buffer.append(f"FINGERPRINT_FOUND:{fpid}")
        self.ser.in_waiting = 1
        
        # Process the input
        line = self.ser.readline().decode("utf-8").strip()
        if line.startswith("FINGERPRINT_FOUND:"):
            self.handle_known_user(fpid)

        print("\nTest Sequence Completed Successfully.")

    def handle_known_user(self, fpid: int) -> None:
        user = users_col.find_one({"fpid": fpid})
        if not user:
            print("User not found")
            return

        self.current_user = user
        name = user.get("name", "Friend")

        anim.play("ANIMATION_PATH1")
        speak_eleven(f"Welcome {name}, please put on the sensors.")

        self.ser.write(b"START_SENSORS\n")

        print(f"Waiting {WAIT_INTERVAL}s for sensors...")
        time.sleep(WAIT_INTERVAL)

        # Get sensor data from mock buffer
        while not self.ser.in_waiting:
            time.sleep(0.1)

        sensor_json = self.ser.readline().decode("utf-8").strip()
        sensor_data = json.loads(sensor_json)
        print(f"Received sensor data: {sensor_data}")

        anim.play("ANIMATION_PATH5")
        anim.play("ANIMATION_PATH4")
        anim.play("ANIMATION_PATH1")

        self.save_sensor_data(sensor_data)
        self.evaluate_medical_data(sensor_data)
        self.start_agent_session()

    def save_sensor_data(self, data: Dict[str, Any]) -> None:
        print(f"[DB] Saving sensor data for user {self.current_user['fpid']}")

    def evaluate_medical_data(self, data: Dict[str, Any]) -> None:
        print("[GEMINI] Evaluating medical data...")
        status = gemini_model.generate_content("test").text.strip().upper()
        print(f"[STATUS] {status}")
        
        if "DANGEROUS" in status:
            self.ser.write(b"LIGHT_RED\n")
        elif "MEDIUM" in status:
            self.ser.write(b"LIGHT_YELLOW\n")
        else:
            self.ser.write(b"LIGHT_GREEN\n")

    def start_agent_session(self) -> None:
        print("\n--- Phase 3: Agent Session ---")
        messages = [{"role": "user", "text": "Hello"}, {"role": "agent", "text": "I am the agent response."}]
        
        print(f"[AGENT] Chat history: {messages}")
        speak_eleven(messages[1]['text'])

        print("[GEMINI] Summarizing session...")
        summary = "Session summarized."
        print(f"[SUMMARY] {summary}")

        sessions_col.insert_one({"fpid": self.current_user["fpid"], "summary": summary})

        anim.play("ANIMATION_PATH6")
        self.ser.write(b"RESET_SESSION\n")
        anim.play("ANIMATION_PATH0")

if __name__ == "__main__":
    bot = DoctoBot()
    bot.start_test()
