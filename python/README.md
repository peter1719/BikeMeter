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

## 模擬器使用說明

本專案包含一個腳踏車數據模擬器，可用於測試和開發：

```
python simulator.py
```

模擬器預設會模擬一台腳踏車，發送速度數據到 MQTT Broker。若要模擬多台腳踏車，可修改 simulator.py 最後一行的參數：

```python
if __name__ == "__main__":
    main(bike_count=10)  # 模擬10台腳踏車
```

### 模擬器特性

- 每台腳踏車每 0.3 秒發送一次數據
- 速度在 10-30 之間隨機變化
- 每 3-8 秒會更新一次目標速度
- 速度變化平滑，模擬真實騎乘情況

## MQTT 數據格式

### 發布主題格式

腳踏車數據發布到以下主題格式：
```
bike/{device_id}/data
```

例如：`bike/bike_001/data`

### 數據格式

數據以 JSON 格式發送，結構如下：

```json
{
  "timestamp": 1634567890123,  // 時間戳（毫秒）
  "device_id": "bike_001",     // 設備ID
  "speed": 25.75               // 當前速度（km/h）
}
```

## 資料庫結構

本專案使用 SQLite 資料庫 (`bike_data.db`) 儲存腳踏車數據。資料庫包含兩個表：

### 1. last_status 表

儲存每台腳踏車的最新狀態：

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| device_id | TEXT | 主鍵，設備ID |
| speed | REAL | 最新速度 |
| timestamp | TEXT | 時間戳（ISO格式） |

### 2. history_data 表

儲存腳踏車的歷史數據（最多保留1000筆記錄）：

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| id | INTEGER | 主鍵，自動遞增 |
| device_id | TEXT | 設備ID |
| speed | REAL | 速度 |
| timestamp | TEXT | 時間戳（ISO格式） |

## 資料庫操作範例

### 查詢設備最新狀態

```python
def get_device_status(device_id):
    conn = sqlite3.connect("bike_data.db")
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT speed, timestamp FROM last_status
    WHERE device_id = ?
    ''', (device_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "device_id": device_id,
            "speed": result[0],
            "timestamp": result[1]
        }
    else:
        return None
```

### 更新設備狀態

```python
def update_device_status(device_id, speed):
    conn = sqlite3.connect("bike_data.db")
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute('''
    INSERT OR REPLACE INTO last_status (device_id, speed, timestamp)
    VALUES (?, ?, ?)
    ''', (device_id, speed, timestamp))
    
    conn.commit()
    conn.close()
```

### 查詢設備歷史數據

```python
def get_device_history(device_id, limit=100):
    conn = sqlite3.connect("bike_data.db")
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT speed, timestamp FROM history_data
    WHERE device_id = ?
    ORDER BY id DESC
    LIMIT ?
    ''', (device_id, limit))
    
    results = cursor.fetchall()
    conn.close()
    
    retur

## 產生 requirements.txt

如果你更新了專案依賴，請更新 requirements.txt：

```
pip freeze > requirements.txt
```

## 環境要求
- Python 3.8 或更高版本
- pip 