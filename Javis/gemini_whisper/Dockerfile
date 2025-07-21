FROM python:3.9-slim

WORKDIR /app

# 系統級依賴（CA證書等）
RUN apt update && \
    apt install -y --no-install-recommends ca-certificates build-essential \
    libportaudio2 portaudio19-dev && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 假設你的 requirements.txt 只有 transformers, accelerate, sounddevice, webrtcvad
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install \
    numpy \
    transformers \
    accelerate \
    sounddevice \
    webrtcvad

COPY . .

CMD ["bash"]
