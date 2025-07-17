import whisper
import sounddevice as sd
import numpy as np
import webrtcvad
import queue
import sys
import threading
import os
import tempfile
import wave

# 初始化模型（CPU）
model = whisper.load_model("base")

# 音频设置
SAMPLE_RATE = 16000
FRAME_DURATION = 30  # 毫秒
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION / 1000)
CHANNELS = 1

# 队列与VAD
q = queue.Queue()
vad = webrtcvad.Vad(3)

def record_audio():
    def callback(indata, frames, time, status):
        if status:
            print(f"⚠️ 录音状态警告: {status}", file=sys.stderr)
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=FRAME_SIZE,
                           dtype='int16', channels=CHANNELS, callback=callback):
        print("✅ 开始监听语音...")
        while True:
            pass  # 主线程只维持回调运行

def vad_collector():
    voiced_frames = []
    triggered = False
    silence_counter = 0
    max_silence = int(1000 / FRAME_DURATION * 0.8)

    while True:
        frame = q.get()
        if vad.is_speech(frame, SAMPLE_RATE):
            if not triggered:
                triggered = True
                print("🎤 语音开始")
            voiced_frames.append(frame)
            silence_counter = 0
        else:
            if triggered:
                silence_counter += 1
                if silence_counter > max_silence:
                    print("🛑 语音结束，开始识别...")
                    triggered = False
                    yield b''.join(voiced_frames)
                    voiced_frames = []
                    silence_counter = 0

def save_wav(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wf = wave.open(f.name, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_bytes)
        wf.close()
        return f.name

def recognize_from_wav(path):
    result = model.transcribe(path)
    print("📝 识别结果:", result['text'])

if __name__ == "__main__":
    threading.Thread(target=record_audio, daemon=True).start()

    for speech in vad_collector():
        wav_path = save_wav(speech)
        recognize_from_wav(wav_path)
        os.remove(wav_path)
