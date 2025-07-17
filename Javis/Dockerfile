FROM python:3.10-slim

# 设置环境变量防止 pyaudio 编译失败
ENV DEBIAN_FRONTEND=noninteractive

# 安装必要系统包
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    ffmpeg \
    alsa-utils \
    pulseaudio \
    curl \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 安装 Python 包
RUN pip install --no-cache-dir \
    SpeechRecognition \
    PyAudio \
    pyttsx3 \
    PyAutoGUI \
    openai \
    numpy

# 创建工作目录
WORKDIR /app

# 将你自己的语音助手代码复制进去（你后续的 Python 脚本）
COPY . /app

# 设置默认执行命令（可以改为你的主脚本）
# CMD ["python", "main.py"]
CMD ["bash"]
