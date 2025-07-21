FROM python:3.9-slim

WORKDIR /app

# 系統級依賴（CA證書等）
RUN apt update && \
    apt install -y --no-install-recommends ca-certificates && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 假設你的 requirements.txt 只有 transformers, accelerate, sounddevice, webrtcvad
RUN pip install --no-cache-dir \
    "torch+cpu" -f https://download.pytorch.org/whl/torch_stable.html && \
    pip install --no-cache-dir \
    numpy \
    transformers \
    accelerate \
    sounddevice \
    webrtcvad

COPY . .

CMD ["bash"]
