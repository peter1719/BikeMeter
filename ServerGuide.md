# 雲端伺服器部署指南

本文檔提供在雲端伺服器上部署腳踏車監控系統的詳細步驟，包括設置環境、配置網絡和啟動服務。

## 目錄

1. [前置準備](#前置準備)
2. [伺服器設置](#伺服器設置)
3. [安裝 MQTT 服務器](#安裝-mqtt-服務器)
4. [專案部署](#專案部署)
5. [網絡配置](#網絡配置)
6. [前端配置更新](#前端配置更新)
7. [服務啟動](#服務啟動)
8. [設置系統服務](#設置系統服務)
9. [故障排除](#故障排除)

## 前置準備

### 雲端伺服器要求

- 作業系統：Ubuntu 20.04 LTS 或更高版本（推薦）
- 最低配置：1 CPU 核心，2GB RAM，20GB 存儲空間
- 推薦配置：2 CPU 核心，4GB RAM，40GB 存儲空間

### 域名設置（可選）

如果您希望使用域名訪問服務，請提前準備：
- 註冊域名
- 將域名 A 記錄指向您的伺服器 IP 地址

## 伺服器設置

### 1. 更新系統

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. 安裝必要套件

```bash
sudo apt install -y python3-pip python3-venv git ufw nginx
sudo apt-get install nodejs
sudo apt install npm
```

### 3. 設置防火牆

```bash
# 允許 SSH 連接
sudo ufw allow ssh

# 允許 MQTT 端口 (1883)
sudo ufw allow 1883/tcp

# 允許 MQTT WebSocket 端口 (9001，如果使用)
sudo ufw allow 9001/tcp

# 允許 HTTP 端口 (5000，後端 API)
sudo ufw allow 5000/tcp

# 允許 HTTP 端口 (5001，後端 API)
sudo ufw allow 5001/tcp

# 允許 HTTP/HTTPS 端口 (80/443，如果使用 Nginx 反向代理)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 啟用防火牆
sudo ufw enable
```

## 安裝 MQTT 服務器

本專案可以使用內建的 MQTT Broker，但如果您需要更穩定的生產環境設置，可以安裝 Mosquitto MQTT Broker。

### 1. 安裝 Mosquitto

```bash
# 安裝 Mosquitto 伺服器和客戶端工具
sudo apt install -y mosquitto mosquitto-clients
```

### 2. 配置 Mosquitto

創建配置文件：

```bash
sudo nano /etc/mosquitto/conf.d/default.conf
```

添加以下配置以允許匿名訪問並監聽所有網絡接口：

```
# 監聽所有網絡接口的標準 MQTT 端口
listener 1883 0.0.0.0

# 允許匿名訪問（開發環境）
allow_anonymous true

# 如果需要 WebSocket 支持，請啟用以下設定
listener 9001 0.0.0.0
protocol websockets
```

> **注意**：在生產環境中，建議設置用戶名和密碼認證，而不是允許匿名訪問。

### 4. 重啟 Mosquitto 服務

```bash
# 重新啟動 Mosquitto 服務
sudo systemctl restart mosquitto

# 設定開機自動啟動
sudo systemctl enable mosquitto
```

### 5. 驗證 Mosquitto 安裝

檢查 Mosquitto 是否正在運行：

```bash
# 檢查服務狀態
sudo systemctl status mosquitto
```

測試 MQTT 連接（匿名訪問）：

```bash
# 在一個終端訂閱主題（保持此視窗開啟）
mosquitto_sub -h localhost -t "test/topic" -v

# 在另一個終端發布消息
mosquitto_pub -h localhost -t "test/topic" -m "Hello MQTT"
```

## 專案部署

### 1. 克隆專案 (請換成自己要放置的路徑 ex: /home/username/BikeMeter -> /var/www/BikeMeter)

```bash
git clone https://github.com/peter1719/BikeMeter.git
cd BikeMeter

# 設置目錄所有者為 Nginx 用戶
sudo chown -R www-data:www-data /home/username/BikeMeter/user-frontend/dist
sudo chown -R www-data:www-data /home/username/BikeMeter/coach-frontend/dist

# 設置適當的權限
sudo chmod -R 755 /home/username/BikeMeter/user-frontend/dist
sudo chmod -R 755 /home/username/BikeMeter/coach-frontend/dist
chmod +x /home/
chmod +x /home/username/
chmod +x /home/username/BikeMeter
```

### 2. 設置 Python 環境

```bash
cd python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 設置前端環境

```bash
# 用戶前端
cd ../user-frontend
npm install
npm run build

# 教練前端
cd ../coach-frontend
npm install
npm run build
```

## 網絡配置

新增 Nginx 配置文件：(建議註解 default 的設定)

```bash
sudo nano /etc/nginx/conf.d/bike.conf
```

添加以下配置：

```nginx
server {
    listen 80;
    server_name bike;
    index index.html;

    # 前端靜態文件
    location /user/ {
        alias /home/username/BikeMeter/user-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 教練前端
    location /coach/ {
        alias /home/username/BikeMeter/coach-frontend/dist/;
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /socket.io/ {
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header  Host $host;
        proxy_set_header  X-Real-IP  $remote_addr;
        proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header  X-Forwarded-Proto   $scheme;
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

啟用配置並重啟 Nginx：

```bash
# 檢查 Nginx 配置是否有語法錯誤
sudo nginx -t

# 重新啟動 Nginx 服務
sudo systemctl restart nginx
```


## 設置 SSL（可選但推薦）

```bash
# 安裝 Certbot
sudo apt install certbot python3-certbot-nginx

# 獲取並配置 SSL 證書
sudo certbot --nginx -d your-domain.com

# 設置自動續期
sudo systemctl status certbot.timer
```

## 前端配置更新

在部署到生產環境前，需要更新前端代碼中的 WebSocket 服務器 URL。

### 1. 更新教練前端 WebSocket 連接

編輯 `coach-frontend/src/stores/devices.js` 文件：

```bash
nano coach-frontend/src/stores/devices.js
```

找到以下代碼段：

```javascript
// 建立 Socket.IO 連接
const newSocket = io('ws://your-websocket-server-url', {
  transports: ['polling', 'websocket'],
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000
})
```

將 `'ws://your-websocket-server-url'` 替換為您的實際服務器地址，例如：

```javascript
// 建立 Socket.IO 連接
const newSocket = io('ws://your-domain.com', {  // 替換為您的實際域名或IP地址
  transports: ['polling', 'websocket'],
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000
})
```

### 2. 重新構建前端

更新配置後，需要重新構建前端：

```bash
cd coach-frontend
npm run build
```

### 3. 更新用戶前端（如果適用）

如果用戶前端也使用了 WebSocket 連接，請按照類似步驟更新相應文件。

## 服務啟動 (尚未測試過)

### 手動啟動服務

```bash
# 切換到專案目錄
cd /path/to/your-project-folder/python

# 啟動虛擬環境
source venv/bin/activate

# 啟動後端服務
python backend_mqtt.py
```

## 設置系統服務 (尚未測試過)

為了確保服務在伺服器重啟後自動啟動，建議設置系統服務：

### 1. 創建服務文件

```bash
sudo nano /etc/systemd/system/bike-monitor.service
```

### 2. 添加以下內容

```ini
[Unit]
Description=Bike Monitor MQTT Backend
After=network.target

[Service]
User=ubuntu  # 替換為您的用戶名
WorkingDirectory=/path/to/your-project-folder/python
ExecStart=/path/to/your-project-folder/python/venv/bin/python backend_mqtt.py
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=bike-monitor

[Install]
WantedBy=multi-user.target
```

### 3. 啟用並啟動服務

```bash
# 重新載入 systemd 配置
sudo systemctl daemon-reload

# 設定開機自動啟動服務
sudo systemctl enable bike-monitor

# 立即啟動服務
sudo systemctl start bike-monitor
```

### 4. 檢查服務狀態

```bash
# 查看服務運行狀態
sudo systemctl status bike-monitor
```

## 故障排除

### 檢查服務日誌

```bash
# 即時查看服務日誌
sudo journalctl -u bike-monitor -f
```

### 檢查端口是否開放

```bash
# 查看所有監聽中的端口
sudo netstat -tulpn | grep LISTEN
```

### 測試 MQTT 連接

訂閱測試：

```bash
# 訂閱所有腳踏車數據
mosquitto_sub -h localhost -t "bike/+/data" -v
```

發布測試：

```bash
# 發送測試數據
mosquitto_pub -h localhost -t "bike/test_device/data" -m '{"device_id": "test_device", "speed": 25.5, "timestamp": 1634567890123}'
```

### 常見問題

1. **服務無法啟動**
   - 檢查 Python 依賴是否正確安裝
   - 確認 backend_mqtt.py 中的端口未被佔用
   - 檢查日誌中的錯誤訊息

2. **無法從外部訪問 MQTT**
   - 確認防火牆已開放 1883 端口
   - 檢查雲服務提供商的安全組設置
   - 確認 MQTT Broker 綁定到 0.0.0.0 而非 localhost

3. **前端無法連接後端**
   - 檢查 API 端點配置是否正確
   - 確認 CORS 設置允許前端域名訪問
   - 檢查網絡連接是否穩定

4. **MQTT 連接問題**
   - 檢查 Mosquitto 服務是否正在運行
   - 確認認證設置是否正確
   - 檢查 MQTT 客戶端配置是否與服務器配置匹配
   - 確認防火牆未阻擋 MQTT 通訊 