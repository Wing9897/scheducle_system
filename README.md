# 課程系統

這是一個用於管理課程的系統，旨在幫助用戶輕鬆創建、查看和管理課程事件。

## 安裝

1. 確保已安裝 Python 3.x。
2. 克隆此存儲庫：
   ```bash
   git clone https://github.com/yourusername/schedule_system.git
   ```
3. 進入項目目錄：
   ```bash
   cd schedule_system
   ```
4. 安裝所需的依賴項：
   ```bash
   pip install -r requirements.txt
   ```

## 環境配置

1. 安裝 MongoDB：
   - 參考 [MongoDB 官方文檔](https://docs.mongodb.com/manual/installation/) 進行安裝。
2. 啟動 MongoDB 服務：
   ```bash
   mongod
   ```
3. 在 `app.py` 中配置 MongoDB 連接：
   ```python
   from pymongo import MongoClient

   client = MongoClient('mongodb://localhost:27017/')
   db = client['your_database_name']
   ```

## 使用

1. 啟動應用程序：
   ```bash
   python app.py
   ```
2. 打開瀏覽器並訪問 `http://127.0.0.1:5000`。

## 授權

此項目使用 MIT 許可證。詳情請參閱 LICENSE 文件。
