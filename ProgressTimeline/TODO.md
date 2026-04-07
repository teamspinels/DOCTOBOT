
# 🩺 Medical Robot Implementation Roadmap
**Target Hardware:** Raspberry Pi 3 A+ & Arduino Mega  
**Tech Stack:** Python, ElevenLabs (Agent/TTS), Gemini API, SQLite, Chafa

## 📡 Phase 1: Hardware & Communication (The "Nervous System")
- [ ] **Sensor Wiring:** Connect R503 (Fingerprint), MAX30102 (Heart/SpO2), and MLX90614 (Temp) to the Arduino Mega.
- [ ] **Arduino Firmware:** - Create a sketch that handles Fingerprint matching.
    - Write an I2C polling routine for biometrics.
    - Implement a JSON Serial output: `{"fp_id": 1, "temp": 36.8, "spo2": 98, "hr": 72}`.
- [ ] **Pi-Arduino Bridge:** Write a Python `serial` script to capture and parse the Arduino's JSON data.

## 🧠 Phase 2: AI & Data Setup (The "Brain")
- [ ] **Environment Setup:** - Install dependencies: `pip install elevenlabs google-genai pyserial`.
    - Install system tools: `sudo apt install chafa ffplay`.
- [x] **ElevenLabs Configuration:**
    - Create the "Doctor" Agent in the dashboard.
    - Upload your medical RAG (Reference Material).
- [ ] **Gemini API:** Set up the Google GenAI client for the final summarization step.
- [ ] **Database Initialization:** - Create `clinic.db` with tables for `Patients` (ID, Name) and `Visits` (ID, Summary, Raw_Log).

## 🎭 Phase 3: Visuals & Audio (The "Face")
- [x] **Animation Library:** Store your `.gif` or `.ascii` assets for `{Blink}`, `{Look}`, and `{Wink}`.
- [ ] **Chafa Integration:** Test triggering animations using `subprocess.Popen(["chafa", "anim.gif"])`.
- [ ] **Audio Test:** Ensure the Pi 3 A+ can play ElevenLabs TTS audio via the speakers without lag.

## 🔄 Phase 4: Core Logic Integration (The "Flow")
- [ ] **Step 1: Identification:** - Logic to check if `fp_id` exists in SQLite.
    - If **New:** Trigger "Ask for Name" flow.
    - If **Existing:** Retrieve last 3 visit summaries.
- [ ] **Step 2: Contextual Injection:** - Format biometrics + history into a text string.
    - Send as a `contextual_update` to the ElevenLabs Agent.
- [ ] **Step 3: Interactive Session:** - Run the ElevenLabs session in text-only mode.
    - Convert AI text responses to speech using ElevenLabs TTS.
    - **Logging:** Append every message (User & AI) to a Python `chat_log` list.

## 📝 Phase 5: Closing & Persistence (The "Memory")
- [ ] **Step 4: Summarization:** - Send the `chat_log` list to Gemini API with a "Medical Scribe" prompt.
- [ ] **Step 5: DB Update:** Save the Gemini summary and raw log into the `Visits` table.
- [ ] **Step 6: Final Interaction:** Play the "Goodbye" audio and trigger the `{Wink}` animation.

---

### 💡 Pro-Tips for your Pi 3 A+
* **Memory Management:** Since you have 512MB RAM, use `gemini-1.5-flash` for the summary—it's faster and lighter.
* **Threading:** Use Python's `threading` module to keep the `{Blink}` animation running in the background while the AI is thinking.
* **Audio Latency:** If `ffplay` is slow, try using `aplay` or `mpg123` for faster playback on Linux.


