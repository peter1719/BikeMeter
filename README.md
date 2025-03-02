# 多前端 Python 後端專案

這是一個包含兩個前端應用程式和一個 Python 後端的專案。

## 專案結構

- **coach-frontend**: 教練端前端應用程式 (Vue 3 + Vite)
- **user-frontend**: 使用者端前端應用程式 (Vue 3 + Vite)
- **python**: Python 後端服務 (MQTT)

## 快速開始

### 後端設置

1. 進入 Python 後端目錄
```
cd python
```

2. 建立並啟動虛擬環境
```
python -m venv venv
```

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

4. 啟動後端服務
```
python backend_mqtt.py
```

後端服務將在指定端口啟動（詳見 python/README.md 中的端口配置說明）

### 前端設置

#### 教練端前端

1. 進入教練端目錄
```
cd coach-frontend
```

2. 安裝依賴
```
npm install
```

3. 啟動開發伺服器
```
npm run dev
```

#### 使用者端前端

1. 進入使用者端目錄
```
cd user-frontend
```

2. 安裝依賴
```
npm install
```

3. 啟動開發伺服器
```
npm run dev
```

## 環境要求

- Node.js 16.x 或更高版本
- npm 7.x 或更高版本
- Python 3.8 或更高版本
- pip

## 詳細文檔

每個子專案都有自己的 README 文件，包含更詳細的設置和使用說明：

- [教練端前端文檔](./coach-frontend/README.md)
- [使用者端前端文檔](./user-frontend/README.md)
- [Python 後端文檔](./python/README.md) 