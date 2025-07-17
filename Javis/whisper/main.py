import whisper
import tempfile
import os
import soundfile as sf
from vad_utils import VADAudio

model = whisper.load_model("base")
vad_audio = VADAudio()

print("✅ 正在监听，请说话...")

buffer = b''
for frame in vad_audio.vad_collector():
    if frame is not None:
        buffer += frame
    else:
        if len(buffer) > 0:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                file_path = f.name
                sf.write(file_path, buffer, vad_audio.sample_rate, subtype='PCM_16')
            print("🎧 正在识别...")
            try:
                result = model.transcribe(file_path)
                print("📝 识别结果：", result["text"])
            except Exception as e:
                print("❌ 识别失败：", e)
            os.remove(file_path)
            buffer = b''
