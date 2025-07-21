import sounddevice as sd
import webrtcvad
import numpy as np
from transformers import pipeline
import collections
import torch
import sys

# --- 配置參數 ---
# ReSpeaker Mic Array 參數
SAMPLE_RATE = 16000  # ReSpeaker 麥克風通常是 16kHz
FRAME_DURATION_MS = 30  # VAD 處理的幀長度（毫秒），推薦 10, 20 或 30
CHUNK_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000) # 每個音頻塊的採樣點數

# VAD 參數
VAD_MODE = 3  # VAD 模式：0 (積極), 1 (普通), 2 (溫和), 3 (最溫和)
# 語音活動的最小幀數閾值，例如：在 `_active_window` 中需要至少 `N` 個語音幀才判斷為語音開始
MIN_SPEECH_FRAMES = 8 # 8 * 30ms = 240ms 的語音

# Whisper 參數
WHISPER_MODEL = "openai/whisper-tiny" # 或 "openai/whisper-base", "openai/whisper-small" 等
# 你可能需要指定語言以提高準確性，例如： "zh" 表示中文
WHISPER_LANGUAGE = "zh"

# 音頻緩衝區大小 (決定一次性處理多長的音頻進行 Whisper 識別)
# 例如：收集最多 10 秒的音頻進行識別
MAX_AUDIO_BUFFER_SECONDS = 10
MAX_AUDIO_BUFFER_SAMPLES = SAMPLE_RATE * MAX_AUDIO_BUFFER_SECONDS

# --- 初始化 VAD 和 Whisper ---
vad = webrtcvad.Vad(VAD_MODE)
print(f"Loading Whisper model: {WHISPER_MODEL}...")
# 為了支持實時處理，通常使用 "automatic-speech-recognition" pipeline
asr_pipeline = pipeline("automatic-speech-recognition", model=WHISPER_MODEL, device=0 if torch.cuda.is_available() else -1)
print("Whisper model loaded.")

# --- 音頻輸入設備查找 (ReSpeaker) ---
def find_respeaker_device():
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        # 根據 ReSpeaker 的實際名稱判斷，可能需要調整
        if "respeaker" in dev['name'].lower() and dev['max_input_channels'] > 0:
            print(f"Found ReSpeaker device: {dev['name']} (ID: {i})")
            return i
    print("ReSpeaker device not found. Listing all input devices:")
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"  ID: {i}, Name: {dev['name']}, Channels: {dev['max_input_channels']}")
    return None # 或者返回默認設備 None

input_device_id = find_respeaker_device()
if input_device_id is None:
    print("Error: ReSpeaker device not found or no input device available. Exiting.")
    sys.exit(1)

# --- 主音頻流處理函數 ---
def audio_callback(indata, frames, time, status):
    """
    Sounddevice 回調函數，當有新的音頻數據時被調用。
    """
    global frames_buffer, voiced_frames_count, current_speech_audio
    if status:
        print(status, file=sys.stderr)

    # 音頻數據轉換為 16-bit PCM 格式，VAD 需要
    pcm_data = (indata * 32767).astype(np.int16).tobytes()

    # VAD 處理
    is_speech = vad.is_speech(pcm_data, SAMPLE_RATE)

    if is_speech:
        voiced_frames_count += 1
        current_speech_audio.append(pcm_data)
        print("Voice detected!")
    else:
        voiced_frames_count = 0 # 重置語音計數

    # 如果語音活動達到閾值，開始收集語音片段
    if voiced_frames_count >= MIN_SPEECH_FRAMES:
        # 當檢測到語音活動時，將當前音頻幀添加到緩衝區
        # 這裡的邏輯是，只要持續有語音，就持續添加到 current_speech_audio
        pass # 數據已經在 `current_speech_audio` 中追加了

    # 如果有語音數據，且緩衝區超過一定大小，或者靜音了一段時間，則處理
    # 這個邏輯需要更精細地控制語音片段的開始和結束
    # 更常見的實時 VAD 實現是使用一個小的滑動窗口來判斷語音的開始和結束
    # 這裡我們簡化處理：只要有語音，就追加；如果靜音，且 current_speech_audio 有內容，就處理
    if not is_speech and len(current_speech_audio) > 0:
        # 靜音且有積累的語音數據，則進行語音識別
        process_current_speech_segment()
        current_speech_audio.clear() # 清空已處理的語音片段
        voiced_frames_count = 0


# --- 語音片段處理和識別 ---
def process_current_speech_segment():
    global current_speech_audio

    if not current_speech_audio:
        return

    combined_audio_data = b"".join(current_speech_audio)

    # 將 Bytes 轉換回 NumPy array (Whisper 需要)
    # 這裡假設你的 `combined_audio_data` 是 16-bit PCM 格式
    audio_np = np.frombuffer(combined_audio_data, dtype=np.int16).astype(np.float32) / 32767.0

    if len(audio_np) > 0:
        print(f"\nProcessing a speech segment of length: {len(audio_np)/SAMPLE_RATE:.2f} seconds...")
        try:
            # 使用 Whisper 進行識別
            # 注意：這裡 `chunk_length_s` 和 `stride` 參數在 pipeline 中通常不需要手動設置
            # pipeline 會處理音頻分割，但如果音頻太長，它會自動分塊
            transcription = asr_pipeline(audio_np, chunk_length_s=30,
                                         generate_kwargs={"language": WHISPER_LANGUAGE})
            print(f"識別結果: {transcription['text']}")
        except Exception as e:
            print(f"Whisper 識別失敗: {e}", file=sys.stderr)
    else:
        print("No audio data in segment to process.")

# --- 主程序循環 ---
print(f"Starting audio stream from device ID: {input_device_id}...")
print(f"Sample Rate: {SAMPLE_RATE}, Frame Duration: {FRAME_DURATION_MS}ms, Chunk Size: {CHUNK_SIZE}")

# 全局變量用於緩衝音頻
frames_buffer = collections.deque(maxlen=int(MAX_AUDIO_BUFFER_SAMPLES / CHUNK_SIZE))
voiced_frames_count = 0
current_speech_audio = [] # 用於累積檢測到的語音片段

try:
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=CHUNK_SIZE,
        device=input_device_id,
        dtype='float32', # sounddevice 默認是 float32
        channels=1, # ReSpeaker 雖然多通道，但這裡只用一個通道
        callback=audio_callback
    ):
        print("\nListening for speech... Press Ctrl+C to stop.")
        # 保持程序運行，直到用戶中斷
        while True:
            sd.sleep(1000) # 每秒檢查一次
except KeyboardInterrupt:
    print("\nStopping audio stream.")
except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
finally:
    print("Program finished.")