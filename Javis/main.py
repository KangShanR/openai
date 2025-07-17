
import speech_recognition as sr
import pyttsx3
import openai
import pyautogui
import os
import time

# ====== 配置 OpenAI API Key ======
# openai.api_key = os.environ.get("OPENAI_API_KEY")  # 推荐从环境变量加载

# ====== 初始化语音引擎 ======
engine = pyttsx3.init()
engine.setProperty("rate", 160)  # 语速
engine.setProperty("volume", 1.0)  # 音量

# ====== 初始化语音识别器 ======
recognizer = sr.Recognizer()

# ====== 选择 ReSpeaker 麦克风设备 ======
mic_index = None
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    if "ReSpeaker" in name or "USB" in name:
        mic_index = i
        break

if mic_index is None:
    print("❌ 没找到 ReSpeaker 麦克风")
    exit(1)

print(f"✅ 使用麦克风设备：{mic_index} - {sr.Microphone.list_microphone_names()[mic_index]}")

# ====== 聊天函数（ChatGPT）======
def chat_with_gpt(prompt):
    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # 或者 gpt-4
            messages=[{"role": "user", "content": prompt}],
            timeout=20
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return "访问 ChatGPT 出错：" + str(e)

# ====== 语音播报函数 ======
def speak(text):
    print(f"💬 回答：{text}")
    engine.say(text)
    engine.runAndWait()

# ====== 本地控制命令 ======
def handle_command(command):
    if "打开浏览器" in command:
        os.system("xdg-open https://www.baidu.com")
        speak("已打开浏览器")
    elif "鼠标上移" in command:
        pyautogui.moveRel(0, -100)
    elif "鼠标下移" in command:
        pyautogui.moveRel(0, 100)
    elif "鼠标左移" in command:
        pyautogui.moveRel(-100, 0)
    elif "鼠标右移" in command:
        pyautogui.moveRel(100, 0)
    elif "点击" in command:
        pyautogui.click()
    elif "关闭窗口" in command:
        pyautogui.hotkey('alt', 'f4')
    else:
        return False
    return True

# ====== 主循环 ======
with sr.Microphone(device_index=mic_index) as source:
    recognizer.adjust_for_ambient_noise(source)
    print("🎙️ 已准备好，请说话（说 '退出' 可关闭）...")

    while True:
        try:
            print("\n🔊 监听中...")
            audio = recognizer.listen(source)

            text = recognizer.recognize_google(audio, language="zh-CN")
            print(f"🗣️ 你说的是：{text}")

            if "退出" in text:
                speak("好的，再见！")
                break

            # 判断是否为命令
            if not handle_command(text):
                # 否则走 ChatGPT 聊天
               #  reply = chat_with_gpt(text)
                speak("todo: chatgpt")

        except sr.UnknownValueError:
            print("🤷 无法识别语音")
        except sr.RequestError as e:
            print(f"🌐 请求出错: {e}")
        except KeyboardInterrupt:
            print("👋 手动中止")
            break
