import sounddevice as sd
import soundfile as sf
from datetime import datetime
import os
import threading
import queue
from pynput import keyboard
import re

def sanitize_folder_name(name):
    # Replace spaces and special characters with underscores
    return re.sub(r'[^\w\-]', '_', name.strip())


SAMPLERATE = 192000
CHUNK_DURATION = 1
CHANNELS = 1
DTYPE = 'float32'
SUBTYPE = 'FLOAT'
CHUNK_SAMPLES = int(SAMPLERATE * CHUNK_DURATION)

def start_recording_session(session_info):
    stop_flag = [False]
    audio_queue = queue.Queue()
    chunk_metadata = []

    # === SESSION FOLDER SETUP ===
    session_folder_name = sanitize_folder_name(session_info["session_name"])
    session_path = os.path.join("recordings", session_folder_name)

    os.makedirs(session_path, exist_ok=True)

    # === INSTANCE FOLDER SETUP ===
    instance_time = datetime.now().strftime("%H%M%S")
    instance_folder_name = f"instance_{session_info['fault_status']}_{instance_time}_{session_info['mic_position']}"
    instance_path = os.path.join(session_path, instance_folder_name)
    chunks_path = os.path.join(instance_path, "chunks")
    os.makedirs(chunks_path, exist_ok=True)

    # === KEYBOARD LISTENER ===
    def on_press(key):
        if key == keyboard.Key.esc:
            stop_flag[0] = True
            print("🛑 ESC pressed. Stopping recording...")

    # === AUDIO CALLBACK ===
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"⚠️ {status}")
        audio_queue.put(indata.copy())

    # === RECORDING LOOP ===
    def record_loop():
        print("🎙️ Recording started. Press 'esc' to stop.")
        stream = sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS,
                                dtype=DTYPE, callback=audio_callback,
                                blocksize=CHUNK_SAMPLES)
        stream.start()

        try:
            while not stop_flag[0]:
                audio_chunk = audio_queue.get()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(chunks_path, f"chunk_{timestamp}.wav")
                sf.write(filename, audio_chunk, SAMPLERATE, subtype=SUBTYPE)

                chunk_metadata.append({
                    "Filename": filename,
                    "Timestamp": timestamp
                })

                print(f"🎧 Saved chunk: {filename}")
        finally:
            stream.stop()
            stream.close()
            print("✅ Recording session ended.")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    recording_thread = threading.Thread(target=record_loop)
    recording_thread.start()
    recording_thread.join()

    return session_path, instance_folder_name, chunk_metadata
