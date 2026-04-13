
# AIoT智慧城市项目 - 同学D专属AI语音控制模块
# 功能：语音识别、指令转换、MQTT指令下发、语音反馈
import speech_recognition as sr
import pyttsx3
import paho.mqtt.client as mqtt
import requests

# 沿用原有MQTT配置，保证兼容
MQTT_HOST = "broker.emqx.io"
MQTT_PORT = 1883
PUB_TOPICS = {
    "A": "city/device_A/cmd",
    "C": "city/device_C/cmd",
    "ALL": "city/all/cmd"
}

# 语音合成初始化，用于语音反馈
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # 设置语速

# MQTT客户端初始化
mqtt_client = mqtt.Client("AIoT_Voice_D")
mqtt_client.connect(MQTT_HOST, MQTT_PORT, 60)
mqtt_client.loop_start()

# 语音指令映射表，对应原有控制指令
voice_cmd_map = {
    "打开外卖柜": ("A", "UNLOCK"),
    "关闭外卖柜": ("A", "LOCK"),
    "打开路政灯": ("C", "LIGHT_ON"),
    "关闭路政灯": ("C", "LIGHT_OFF"),
    "触发火警": ("ALL", "EMERGENCY_FIRE"),
    "解除火警": ("ALL", "EMERGENCY_STOP"),
    "查看设备状态": ("STATUS", "")
}

# 语音播报函数
def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

# 语音识别函数
def listen_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("请说出指令...")
        speak("请说出指令")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
    try:
        # 离线中文语音识别
        text = recognizer.recognize_whisper(audio, language="Chinese")
        print(f"识别结果：{text}")
        return text
    except Exception as e:
        print("语音识别失败，请重试")
        speak("没听清，请再说一遍")
        return ""

# 执行语音指令
def execute_cmd(voice_text):
    for key, (target, cmd) in voice_cmd_map.items():
        if key in voice_text:
            if target == "STATUS":
                # 语音播报设备状态
                try:
                    res = requests.get("http://localhost:5000/api/status")
                    status_data = res.json()
                    status_msg = f"外卖柜状态：{status_data['A']}，应急状态：{status_data['B']}，路政灯状态：{status_data['C']}"
                    print(status_msg)
                    speak(status_msg)
                except:
                    speak("获取状态失败，请检查后台运行")
            else:
                # 下发MQTT指令
                mqtt_client.publish(PUB_TOPICS[target], cmd)
                speak(f"已执行：{key}")
            return
    # 未识别到有效指令
    speak("未识别到有效指令，请重新说出指令")

# 主循环
if __name__ == '__main__':
    print("="*50)
    print("AI语音控制模块启动成功！")
    print("支持指令：打开外卖柜、关闭外卖柜、打开路政灯、关闭路政灯、触发火警、解除火警、查看设备状态")
    print("="*50)
    speak("AI语音控制已启动，可说出指令控制设备")
    while True:
        voice_text = listen_voice()
        if voice_text:
            execute_cmd(voice_text)