#!/usr/bin/env python3
"""
DoctoBot main application module.
This Code May contain errors but all of them are fixed on the rasberry pi , 
and not retreaved back to main repo

MongoDB is beaing used so it can be easely transported to a cloud database if needed,
and also to store user profiles and session data in a structured way.

Most of code has been coded by humans then been sent to ai to do last touches and fixes

the agent is too connected to our api which is nota good practice to be shared so we are sorry because you couldn't access it

If any code is not clear or you have any questions about it please let us know and we will be happy to explain it to you in more details.
team email : teamspinels@gmail.com

you may need to change some paths and API keys in the .env file to make it work on your machine,
 Cause we use linux commands and paths in this code,
 so if you are using a different OS you may need to adjust some parts of the code to make it work on your system.

 
if you want to let app pathes to be correct you need to setup the same project tree
/Files
    /DOCTOBOT
        /ShowcaseCode
            DOCTOBOT.py
            DOCTOBOT.ino
            /voices
                FP.mp3
            /Faces
                Base.gif
                Blink.gif
                ToLeft.gif
                ToRight.gif
                gamza.gif
                BlinkFast.gif
                fp.gif
            .env
            uv.lock
            pyproject.toml

then run ``` uv sync ``` to install the dependencies and then run the DOCTOBOT.py file to start the application.
after compiling the DOCTOBOT.ino file and uploading it to the arduino with the correct serial port and baud rate settings in the .env file.
also connecting the sensors to the arduino as per the instructions in the DOCTOBOT.ino file.
"""

import json
import multiprocessing
import os
import secrets
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import cv2 #type: ignore this is because of the type hints in the cv2 library which are not well captured by type hints
from google import genai 
import serial
import vlc #type: ignore this is because of the type hints in the vlc library which are not accurate
from dotenv import load_dotenv
from elevenlabs import play as el_play
from elevenlabs.client import ElevenLabs
from pymongo import MongoClient

load_dotenv()

SERIAL_PORT: str = os.getenv("SERIAL_PORT", "/dev/ttyACM0")
SERIAL_BAUD: int = int(os.getenv("SERIAL_BAUD", "115200"))
MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "doctobot")
ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_AGENT_ID: str = os.getenv("ELEVENLABS_AGENT_ID", "")
ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "Josh")
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

IDLE_INTERVAL = 60
WAIT_INTERVAL = 15

client: MongoClient = MongoClient(MONGODB_URI) #type: ignore "Partially unknown type returned by MongoClient constructor, but we know it's correct"
db: Any = client[MONGODB_DB_NAME] #type: ignore "The type of db is dynamic and depends on the MongoDB setup, so we use Any here for flexibility"
users_col: Any = db["users"]
sessions_col: Any = db["sessions"]

genai.configure(api_key=GOOGLE_API_KEY) #type: ignore "void like function to configure the genai library, we just need to call it with the API key and it sets up the global configuration"
gemini_model: genai.GenerativeModel = genai.GenerativeModel("gemini-1.5-flash") #type: ignore "the genai library has some dynamic typing that is not well captured by type hints, we know this is how you create a model instance"

el_client: ElevenLabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)


class AnimationManager:
    """Manages playing gif animations using chafa in a separate process."""

    def __init__(self) -> None:
        """Initialize the animation manager."""
        self.process: Optional[multiprocessing.Process] = None
        self.current_key: Optional[str] = None

    def play(self, key: str) -> None:
        """Start playing an animation for the given environment key.
           we used env key to save animations for some chafa related purposes."""
        if self.process:
            self.stop()
        self.current_key = key
        self.process = multiprocessing.Process(target=self._run_chafa, args=(key,))
        self.process.start()

    def _run_chafa(self, key: str) -> None:
        columns, lines = shutil.get_terminal_size()
        file_path: Optional[str] = os.getenv(key)
        if not file_path:
            return
        while True:
            subprocess.run(
                [
                    "/usr/bin/chafa",
                    f"--size={columns+6}x{lines}",
                    "--align",
                    "center",
                    "--speed",
                    "10",
                    file_path,
                ],
                check=False,
            )
            time.sleep(1)

    def stop(self) -> None:
        """Stop the currently playing animation."""
        if self.process:
            self.process.terminate()
            subprocess.run(["/usr/bin/pkill", "chafa"], capture_output=True, check=False)
            subprocess.run(["/usr/bin/clear"], capture_output=True, check=False)
            self.process = None


anim: AnimationManager = AnimationManager()


def play_audio(path: Union[str, Path]) -> None:
    """Play an audio file using VLC."""
    p: vlc.MediaPlayer = vlc.MediaPlayer(str(path)) #type: ignore this is because of the type hints in the vlc library which are not accurate
    p.play()
    time.sleep(0.5)
    while p.is_playing():
        time.sleep(0.1)


def speak_eleven(text: str) -> None:
    """Generate and play speech using ElevenLabs."""
    audio: Any = el_client.generate( #type: ignore the ElevenLabs library has some dynamic typing that is not well captured by type hints
        text=text, voice=ELEVENLABS_VOICE_ID, model="eleven_multilingual_v2"
    )
    el_play(audio) #type: ignore 


class DoctoBot:
    """Main robot logic controller."""

    def __init__(self) -> None:
        """Initialize the robot with serial connection and state."""
        self.ser: serial.Serial = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
        self.current_user: Optional[Dict[str, Any]] = None
        self.last_fp_time: float = 0.0

    def start(self) -> None:
        """Start the main robot loop."""
        while True:
            if self.ser.in_waiting:
                line: str = self.ser.readline().decode("utf-8").strip()
                if line.startswith("FINGERPRINT_FOUND:"):
                    fpid: int = int(line.split(":")[1])
                    self.handle_known_user(fpid)
                elif line == "NEW_FINGERPRINT_DETECTED":
                    self.handle_new_user()

            if time.time() - self.last_fp_time > IDLE_INTERVAL:
                anim.play("ANIMATION_PATH0")
                play_audio("./voices/FP.mp3")
                self.last_fp_time = time.time()

            time.sleep(0.1)

    def handle_known_user(self, fpid: int) -> None:
        """Handle an interaction with a recognized user."""
        user: Optional[Dict[str, Any]] = users_col.find_one({"fpid": fpid})
        if not user:
            return

        self.current_user = user
        name: str = user.get("name", "Friend")

        anim.play("ANIMATION_PATH1")
        speak_eleven(f"Welcome {name}, please put on the sensors.")

        self.ser.write(b"START_SENSORS\n")

        start_wait: float = time.time()
        while time.time() - start_wait < WAIT_INTERVAL:
            anim.play(secrets.choice(["ANIMATION_PATH1", "ANIMATION_PATH2"]))
            time.sleep(3)

        while not self.ser.in_waiting:
            time.sleep(0.1)

        sensor_json: str = self.ser.readline().decode("utf-8").strip()
        sensor_data: Dict[str, Any] = json.loads(sensor_json)

        anim.play("ANIMATION_PATH5")
        time.sleep(1)
        anim.play("ANIMATION_PATH4")
        time.sleep(1)
        anim.play("ANIMATION_PATH1")

        self.save_sensor_data(sensor_data)
        self.evaluate_medical_data(sensor_data)
        self.start_agent_session()

    def handle_new_user(self) -> None:
        """Handle the creation of a new user profile."""
        anim.play("ANIMATION_PATH0")
        speak_eleven("I don't recognize you. Let's create a profile. What is your name?")

        name: str = "New User"

        cam: cv2.VideoCapture = cv2.VideoCapture(0) #type: ignore this is because of the type hints in the cv2 library which are not well captured by type hints
        ret, frame = cam.read() #type: ignore "the same reason as above"
        if ret:
            cv2.imwrite("user_new.jpg", frame) #type: ignore "the same reason as above"
        cam.release() #type: ignore "the same reason as above"

        fpid: int = secrets.randbelow(900) + 100
        users_col.insert_one({"fpid": fpid, "name": name})
        speak_eleven(f"Profile created for {name}. Please place your finger again.")
        self.ser.write(b"RESET_SESSION\n")

    def save_sensor_data(self, data: Dict[str, Any]) -> None:
        """Save sensor readings to the current user's database record."""
        if self.current_user:
            users_col.update_one(
                {"fpid": self.current_user["fpid"]},
                {"$push": {"readings": {**data, "time": time.time()}}},
            )

    def evaluate_medical_data(self, data: Dict[str, Any]) -> None:
        """Evaluate sensor data using Gemini and set LED status on Arduino."""
        prompt: str = (
            f"Evaluate these medical readings: Temp: {data['temp']}, "
            f"BPM: {data['bpm']}, SpO2: {data['spo2']}. "
            "Return only one word: DANGEROUS, MEDIUM, or NORMAL."
        )
        response: Any = gemini_model.generate_content(prompt) #type: ignore the genai library has some dynamic typing that is not well captured by type hints
        status: str = response.text.strip().upper() #type: ignore "the same reason as above"

        if "DANGEROUS" in status:
            self.ser.write(b"LIGHT_RED\n")
        elif "MEDIUM" in status:
            self.ser.write(b"LIGHT_YELLOW\n")
        else:
            self.ser.write(b"LIGHT_GREEN\n")

    def start_agent_session(self) -> None:
        """Start an interactive chat session with the ElevenLabs agent."""
        if not self.current_user:
            return

        # Fetch last 3 sessions for context (if needed by agent)
        _history: List[Dict[str, Any]] = list(
            sessions_col.find({"fpid": self.current_user["fpid"]})
            .sort("time", -1)
            .limit(3)
        )

        messages: List[Dict[str, str]] = []
        chat_active: bool = True

        while chat_active:
            anim.play(
                secrets.choice(
                    ["ANIMATION_PATH1", "ANIMATION_PATH2", "ANIMATION_PATH3"]
                )
            )

            user_input: str = "Hello"
            if "thank you" in user_input.lower():
                chat_active = False

            messages.append({"role": "user", "text": user_input})

            # REAL API CALL FOR CONVERSATIONAL AGENT
            try:
                response = el_client.conversational_ai.get_response( #type: ignore
                    agent_id=ELEVENLABS_AGENT_ID,
                    text=user_input
                )
                agent_text: str = response.text #type: ignore 
            except Exception as e:
                print(f"Error calling ElevenLabs Agent: {e}")
                agent_text = "I'm having trouble connecting to my brain right now."

            messages.append({"role": "agent", "text": agent_text})
            speak_eleven(agent_text) #type: ignore "the same reason as before, by type hints"

            if not chat_active:
                break

        # Summarize
        summary_prompt: str = f"Summarize this conversation: {json.dumps(messages)}"
        summary: str = gemini_model.generate_content(summary_prompt).text #type: ignore the genai library has some dynamic typing that is not well captured by type hints

        sessions_col.insert_one(
            {
                "fpid": self.current_user["fpid"],
                "time": time.time(),
                "messages": messages,
                "summary": summary,
            }
        )

        anim.play("ANIMATION_PATH6")
        time.sleep(2)
        self.ser.write(b"RESET_SESSION\n")
        anim.play("ANIMATION_PATH0")


if __name__ == "__main__":
    bot: DoctoBot = DoctoBot()
    bot.start()
