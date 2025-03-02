# Python 後端

## 環境建置

1. 建立虛擬環境
```
python -m venv venv
```

2. 啟動虛擬環境
Windows:
```
venv\Scripts\activate
```
Linux/Mac:
```
source venv/bin/activate
```

3. 安裝依賴
```
pip install -r requirements.txt
```

4. 啟動伺服器
```
python backend_mqtt.py
```

## 端口配置

後端服務使用以下端口：

- MQTT Broker: 預設端口 1883（可在 backend_mqtt.py 中配置）
- WebSocket 連接: 預設端口 5000（可在 backend_mqtt.py 中配置）

如需修改端口配置，請編輯 backend_mqtt.py 文件中的相關設置。

## 產生 requirements.txt

如果你更新了專案依賴，請更新 requirements.txt：

```
pip freeze > requirements.txt
```

## 環境要求
- Python 3.8 或更高版本
- pip 