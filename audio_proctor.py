from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
import threading
import wave
import pyaudio
import time

app = Flask(__name__)
CORS(app)

# Directory to save recordings
RECORDINGS_DIR = "recordings"
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)

# Audio recording settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 16
OUTPUT_FILENAME = None

# Initialize PyAudio
p = pyaudio.PyAudio()

# Global flag to avoid multiple recordings simultaneously
is_recording = False


def record_audio():
    global OUTPUT_FILENAME, is_recording
    is_recording = True
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording started...")
    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()

    # Save the audio file to the "recordings" directory
    OUTPUT_FILENAME = os.path.join(RECORDINGS_DIR, f"recording_{int(time.time())}.wav")
    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Recording saved to {OUTPUT_FILENAME}")
    is_recording = False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/start-recording", methods=["GET"])
def start_recording():
    global is_recording
    if not is_recording:
        threading.Thread(target=record_audio).start()
        return jsonify({"status": "success", "message": "Recording started."}), 200
    else:
        return jsonify({"status": "error", "message": "Already recording."}), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5500)
