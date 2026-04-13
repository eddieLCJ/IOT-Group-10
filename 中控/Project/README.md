## 项目正确运行方式
```bash
# 1. 创建虚拟环境
python3 -m venv .venv
# 2.1 激活（macOS / bash / zsh）
source .venv/bin/activate
# 2.2 激活（cmd）
.\.venv\Scripts\activate.bat
# 3. 可选：升级 pip
pip install --upgrade pip setuptools wheel --ignore-installed  


```bash
# 4. 安装所有的包
pip install paho-mqtt==1.6.1 flask requests pyttsx3 speechrecognition openai-whisper  pyaudio
```

```bash
# 5. 运行接口
python voice_control.py
python app.py
```

```bash
# 6. 运行网页
http://localhost:4040 //本地
```