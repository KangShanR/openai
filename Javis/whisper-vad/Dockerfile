# 使用官方轻量 Python 镜像
FROM python:3.10-slim

# 安装依赖
RUN apt update && apt install -y \
    ffmpeg \
    portaudio19-dev \
    libasound2-dev \
    build-essential \
    libsndfile1 \
    git \
    && apt clean && rm -rf /var/lib/apt/lists/*

# 安装 Whisper（含 torch）
RUN pip install --upgrade pip
RUN pip install numpy
RUN pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install git+https://github.com/openai/whisper.git
RUN pip install sounddevice webrtcvad
RUN pip install soundfile

# 创建目录用于挂载音频文件
COPY . /app
WORKDIR /app

CMD ["bash"]
