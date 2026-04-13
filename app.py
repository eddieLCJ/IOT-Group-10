
# AIoT智慧城市项目 - 同学D专属Python后台
# 功能：MQTT消息监听、指令转发、Web服务支撑、数据存储
import paho.mqtt.client as mqtt
import time
from flask import Flask, render_template, request, jsonify

# 原有MQTT配置完全复用，保证与原有设备兼容
MQTT_HOST = "broker.emqx.io"
MQTT_PORT = 1883
# 订阅原有设备状态主题
SUB_TOPICS = ["city/status/a", "city/status/b", "city/status/c", "city/all/cmd"]
# 发布原有控制指令主题
PUB_TOPICS = {
    "A": "city/device_A/cmd",
    "C": "city/device_C/cmd",
    "ALL": "city/all/cmd"
}

# 全局存储设备状态，与原有状态标识一致
device_status = {
    "A": "正常关闭",
    "B": "正常",
    "C": "已关闭",
    "emergency": False
}
# 存储历史操作日志
history_log = []

# Flask Web应用初始化
app = Flask(__name__)

# MQTT消息接收回调函数
def on_message(client, userdata, msg):
    global device_status
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    # 更新对应设备状态
    if topic == "city/status/a":
        device_status["A"] = payload
    elif topic == "city/status/b":
        device_status["B"] = payload
        device_status["emergency"] = (payload == "火警触发")
    elif topic == "city/status/c":
        device_status["C"] = payload
    # 记录日志
    log_info = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "topic": topic,
        "data": payload
    }
    history_log.append(log_info)
    print(f"接收消息：{topic} → {payload}")

# MQTT客户端初始化
def init_mqtt_client():
    client = mqtt.Client("AIoT_Control_D")
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    # 订阅所有预设主题
    for topic in SUB_TOPICS:
        client.subscribe(topic)
    return client

# Web接口：获取设备实时状态
@app.route('/api/status')
def get_device_status():
    return jsonify(device_status)

# Web接口：下发控制指令
@app.route('/api/send_cmd', methods=['POST'])
def send_control_cmd():
    data = request.json
    target_device = data.get("target")
    cmd_content = data.get("cmd")
    if target_device in PUB_TOPICS:
        print(f"下发指令：{PUB_TOPICS[target_device]} → {cmd_content}")
        result = mqtt_client.publish(PUB_TOPICS[target_device], cmd_content)
        # result.wait_for_publish()
        return jsonify({"status": "success", "msg": f"指令已下发：{target_device} - {cmd_content}"})
    return jsonify({"status": "fail", "msg": "目标设备不存在"}), 400

# Web主页：访问可视化面板
@app.route('/')
def index_page():
    return render_template('index.html', status=device_status)

# Web接口：获取历史日志
@app.route('/api/logs')
def get_history_logs():
    return jsonify(history_log[-20:])

# 主程序运行
if __name__ == '__main__':
    # 初始化MQTT客户端
    mqtt_client = init_mqtt_client()
    # 后台线程运行MQTT监听
    import threading
    mqtt_thread = threading.Thread(target=mqtt_client.loop_forever, daemon=True)
    mqtt_thread.start()
    # 启动Web服务
    print("="*50)
    print("AIoT智能后台启动成功！")
    print("Web管控面板访问地址：http://localhost:4040")
    print("="*50)
    app.run(host='0.0.0.0', port=4040, debug=True)
    