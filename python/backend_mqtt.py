from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# 修改 SocketIO 配置
socketio = SocketIO(app, 
    cors_allowed_origins="*",
    async_mode='threading',  # 使用threading模式
    logger=True,  # 啟用日誌
    engineio_logger=True  # 啟用 Engine.IO 日誌
)

# MQTT 設置
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "bike/+/data"

# 資料庫設置
DB_FILE = "bike_data.db"

# 初始化資料庫
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 創建最後狀態表 (以 device_id 為鍵)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS last_status (
        device_id TEXT PRIMARY KEY,
        speed REAL,
        timestamp TEXT
    )
    ''')
    
    # 創建歷史記錄表 (保存最近 1000 筆資料)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS history_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        speed REAL,
        timestamp TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

# 更新最後狀態
def update_last_status(device_id, speed):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute('''
    INSERT OR REPLACE INTO last_status (device_id, speed, timestamp)
    VALUES (?, ?, ?)
    ''', (device_id, speed, timestamp))
    
    conn.commit()
    conn.close()

# 添加歷史記錄
def add_history_data(device_id, speed):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    # 插入新記錄
    cursor.execute('''
    INSERT INTO history_data (device_id, speed, timestamp)
    VALUES (?, ?, ?)
    ''', (device_id, speed, timestamp))
    
    # 保留最新的 1000 筆記錄
    cursor.execute('''
    DELETE FROM history_data 
    WHERE id NOT IN (
        SELECT id FROM history_data 
        ORDER BY id DESC 
        LIMIT 1000
    )
    ''')
    
    conn.commit()
    conn.close()

# 獲取設備最後狀態
def get_last_status(device_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT speed, timestamp FROM last_status
    WHERE device_id = ?
    ''', (device_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "speed": result[0],
            "timestamp": result[1]
        }
    else:
        return {
            "speed": -1,
            "timestamp": -1
        }

# API 端點 - 獲取設備最後狀態
@app.route('/api/device/status', methods=['GET'])
def device_status():
    device_id = request.args.get('device_id')
    
    if not device_id:
        return jsonify({"error": "Missing device_id parameter"}), 400
    
    status = get_last_status(device_id)
    return jsonify(status)

# MQTT 回調函數
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        # 從主題中提取 device_id (假設格式為 "bike/{device_id}/data")
        topic_parts = msg.topic.split('/')
        if len(topic_parts) >= 3:
            device_id = topic_parts[1]
            
            # 只提取 speed 數據
            if 'speed' in data:
                speed = data['speed']
                
                # 更新資料庫
                update_last_status(device_id, speed)
                add_history_data(device_id, speed)
            
            # 發送到 WebSocket (保持原有功能，發送完整數據)
            socketio.emit('mqtt_message', data)
        else:
            print(f"Invalid topic format: {msg.topic}")
    except Exception as e:
        print(f"Error processing message: {e}")

# 初始化資料庫
init_db()

# 設置 MQTT 客戶端
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# 連接到 MQTT Broker
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()  # 在背景執行 MQTT 循環
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")

if __name__ == '__main__':
    socketio.run(app, 
        debug=True, 
        port=5000,
        host='0.0.0.0',  # 允許外部訪問
        allow_unsafe_werkzeug=True  # 允許在開發環境使用
    ) 