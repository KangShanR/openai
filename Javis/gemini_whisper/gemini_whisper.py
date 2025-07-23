import sounddevice as sd
import webrtcvad
import numpy as np
# from transformers import pipeline # 移除此行
from transformers import WhisperProcessor, WhisperForConditionalGeneration # 新增導入
    
import collections
import torch
import sys
import time # 新增導入 time
import socket


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
WHISPER_MODEL = "openai/whisper-tiny.en" # 或 "openai/whisper-base", "openai/whisper-small" 等
# 你可能需要指定語言以提高準確性，例如： "zh" 表示中文
WHISPER_LANGUAGE = "en"

# 音頻緩衝區大小 (決定一次性處理多長的音頻進行 Whisper 識別)
# 例如：收集最多 10 秒的音頻進行識別
MAX_AUDIO_BUFFER_SECONDS = 10
MAX_AUDIO_BUFFER_SAMPLES = SAMPLE_RATE * MAX_AUDIO_BUFFER_SECONDS

# 全局變量用於緩衝音頻
frames_buffer = collections.deque() # 不再限制 maxlen，交由後續邏輯控制
voiced_frames_count = 0
current_speech_audio = []
# 新增 VAD 相關狀態變量
in_speech_segment = False # 是否處於語音片段中
silence_frames_after_speech = 0 # 語音結束後連續的靜音幀數
SILENCE_THRESHOLD_FRAMES = int(0.5 * SAMPLE_RATE / CHUNK_SIZE) # 靜音閾值，例如 0.5 秒的靜音


# --- 初始化 VAD 和 Whisper ---
vad = webrtcvad.Vad(VAD_MODE)
print(f"Loading Whisper model: {WHISPER_MODEL}...")
# 為了支持實時處理，通常使用 "automatic-speech-recognition" pipeline
# asr_pipeline = pipeline("automatic-speech-recognition", model=WHISPER_MODEL, device=0 if torch.cuda.is_available() else -1)
# 直接載入處理器和模型
processor = WhisperProcessor.from_pretrained(WHISPER_MODEL)
model = WhisperForConditionalGeneration.from_pretrained(WHISPER_MODEL)
device = "cpu"
model.to(device)
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
def audio_callback(indata, frames, time_info, status): # 將 time 改為 time_info 避免與 time 模塊衝突
    """
    Sounddevice 回調函數，當有新的音頻數據時被調用。
    """
    global voiced_frames_count, current_speech_audio, in_speech_segment, silence_frames_after_speech

    if status:
        print(status, file=sys.stderr)

    # 音頻數據轉換為 16-bit PCM 格式，VAD 需要
    pcm_data = (indata * 32767).astype(np.int16).tobytes()

    # VAD 處理
    is_speech = vad.is_speech(pcm_data, SAMPLE_RATE)

    if is_speech:
        silence_frames_after_speech = 0 # 重置靜音計數
        current_speech_audio.append(pcm_data)
        if not in_speech_segment:
            voiced_frames_count += 1
            if voiced_frames_count >= MIN_SPEECH_FRAMES:
                in_speech_segment = True
                print("\n--- Speech Start Detected ---")
        # else: continue appending
    else: # is_speech is False (靜音)
        if in_speech_segment:
            # 處於語音片段中，但現在是靜音，開始計數靜音幀
            silence_frames_after_speech += 1
            current_speech_audio.append(pcm_data) # 為了保留語音末尾的少量靜音，方便識別
            if silence_frames_after_speech >= SILENCE_THRESHOLD_FRAMES:
                # 靜音持續時間達到閾值，判斷語音片段結束
                print("--- Speech End Detected (Silence Threshold Reached) ---")
                process_current_speech_segment()
                current_speech_audio.clear()
                in_speech_segment = False
                voiced_frames_count = 0
                silence_frames_after_speech = 0 # 重置所有狀態
        else:
            # 不在語音片段中，且當前是靜音，重置語音計數
            voiced_frames_count = 0
            current_speech_audio.clear() # 清除過長的純靜音緩衝區，避免無用數據積累


# --- 語音片段處理和識別 ---
def process_current_speech_segment():
    global current_speech_audio

    if not current_speech_audio:
        return

    combined_audio_data = b"".join(current_speech_audio)
    audio_np = np.frombuffer(combined_audio_data, dtype=np.int16).astype(np.float32) / 32767.0

    if len(audio_np) > 0:
        print(f"\nProcessing a speech segment of length: {len(audio_np)/SAMPLE_RATE:.2f} seconds...")
        try:
            # 1. 將音頻數據處理為模型輸入格式
            # `return_attention_mask=True` 對於較新版本的模型是必要的
            input_features = processor(audio_np, sampling_rate=SAMPLE_RATE, return_tensors="pt").input_features

            # 2. 將輸入特徵移動到正確的設備 (CPU)
            input_features = input_features.to(device)

            # 3. 生成文本 (使用模型的 generate 方法)
            # 這會利用模型內建的長音頻處理機制
            # 指定語言，並可以加上 return_timestamps=True 獲取更詳細的信息
            predicted_ids = model.generate(input_features, 
                                         return_timestamps=False) # 根據需要是否返回時間戳

            # 4. 將預測的 token ID 解碼為文本
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            send_command_to_host(transcription)
            print(f"識別結果: {transcription}")

        except Exception as e:
            print(f"Whisper 識別失敗: {e}", file=sys.stderr)
    else:
        print("No audio data in segment to process.")

# --- 主程序循環 ---
print(f"Starting audio stream from device ID: {input_device_id}...")
print(f"Sample Rate: {SAMPLE_RATE}, Frame Duration: {FRAME_DURATION_MS}ms, Chunk Size: {CHUNK_SIZE}")

# --- 主機 Socket Server 配置 ---
HOST_IP = 'localhost' # with the --network host parameter in docker run
HOST_PORT = 12345 # 必須與 host_controller.py 中的 PORT 一致

# ... (其餘 send_command_to_host 函數代碼不變)
def send_command_to_host(command):
    """將識別到的命令發送給主機"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"Connecting to {HOST_IP}:{HOST_PORT}...")
            client_socket.connect((HOST_IP, HOST_PORT))
            print(f"Successfully connected to {HOST_IP}:{HOST_PORT}.")

            time.sleep(0.1) # 延遲 100 毫秒，確保服務器準備就緒

            client_socket.sendall(command.encode('utf-8'))
            print(f"Sent command to host: '{command}'")
    except ConnectionRefusedError:
        print(f"Error: Connection refused by host at {HOST_IP}:{HOST_PORT}. Is host_controller.py running?", file=sys.stderr)
    except Exception as e:
        print(f"Error sending command: {e}", file=sys.stderr)



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