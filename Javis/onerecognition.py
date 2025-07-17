
import speech_recognition as sr

r = sr.Recognizer()
with sr.Microphone() as source:
    print("✅ 正在监听，请说话...")
    audio = r.listen(source)
    print("🎧 正在识别，请稍候...")

    try:
        text = r.recognize_google(audio, language='en-US')
        print("✅ 识别结果：", text)
    except sr.UnknownValueError as e:
        print("❌ 无法识别语音:{e}")
    except sr.RequestError as e:
        print(f"❌ 请求识别服务失败: {e}")
    except Exception as e:
        print(f"❌ 失败: {e}")
