# 時間管理系統

這是一個用於管理時間的系統，旨在幫助用戶輕鬆創建、查看和管理事件。此系統提供直觀的界面，使用戶能夠高效地組織和安排時間。

## 功能概述

1. **用戶認證**: 用戶可以註冊新帳號並登入系統。系統使用 bcrypt 加密用戶密碼以確保安全性。
2. **事件管理**: 用戶可以創建、查看和刪除事件。所有事件都存儲在 MongoDB 中，並且每個用戶都有獨立的事件集合。
3. **API 接口**: 系統提供多個 API 接口，允許用戶通過前端或其他應用程序管理事件。

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

### 用戶界面

- **首頁**: 用戶可以在首頁註冊新帳號或登入。
- **註冊頁面**: 用戶需要提供電子郵件和密碼來註冊。
- **登入頁面**: 用戶使用電子郵件和密碼登入系統。
- **儀表板**: 登入後，用戶可以查看日曆，添加新事件，並導出事件。

### API 接口

- **GET /api/events**: 獲取用戶的所有事件。
- **POST /api/events**: 創建新事件。
- **DELETE /api/events/<event_id>**: 刪除指定事件。

## 授權

此項目使用 MIT 許可證。詳情請參閱 LICENSE 文件。
