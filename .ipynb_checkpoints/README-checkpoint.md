# Tesla Telegram 機器人

## 專案簡介

這是一個專為管理和查詢 Tesla 車輛資訊設計的 Telegram 機器人。它與 Google Sheets 整合，用於儲存和檢索車輛數據。

## 主要功能

- 查詢車輛狀態
- 更新車輛狀態和位置
- 列出所有車輛
- 按狀態、單位或車號搜尋車輛

## 系統要求

- Python 3.9 或更高版本
- Docker（可選）
- 已啟用 Sheets API 的 Google Cloud Platform 帳戶
- Telegram Bot Token

## 安裝指南

### 1. 克隆儲存庫

```bash
git clone https://github.com/yourusername/tesla-telegram-bot.git
cd tesla-telegram-bot
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 設置環境變數

在專案根目錄創建 `.env` 文件，並添加以下變數：

```
TELEGRAM_BOT_TOKEN=你的_telegram_bot_token
GOOGLE_SPREADSHEET_ID=你的_google_spreadsheet_id
```

### 4. 設置 Google Sheets API

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建新專案或選擇現有專案
3. 啟用 Google Sheets API
4. 創建服務帳戶並下載 JSON 金鑰
5. 將下載的 JSON 檔案重命名為 `credentials.json` 並放置在專案根目錄

## 使用方法

### 本地運行

```bash
python bot.py
```

### 使用 Docker

1. 構建 Docker 鏡像：

```bash
docker build -t tesla-telegram-bot .
```

2. 運行容器：

```bash
docker run --env-file .env tesla-telegram-bot
```

## 機器人指令

- `/start`: 開始使用機器人，顯示主菜單
- 查詢車輛狀態：輸入車號即可查詢
- 更新車輛狀態或位置：選擇相應選項後輸入新的狀態或位置
- 查詢所有車輛：顯示所有車輛的資訊
- 查詢特定狀態的車輛：輸入狀態即可查詢
- 查詢特定單位的車輛：輸入單位名稱即可查詢

## 測試

運行測試套件：

```bash
python -m unittest discover tests
```

## 故障排除

1. 如果遇到 Google Sheets API 認證問題：
   - 確保 `credentials.json` 檔案位於正確位置
   - 檢查 Google Cloud Console 中的 API 是否正確啟用

2. 如果 Telegram 機器人無響應：
   - 確認 `TELEGRAM_BOT_TOKEN` 是否正確設置
   - 檢查機器人在 Telegram 中是否已啟動

3. 如果數據更新失敗：
   - 確認 `GOOGLE_SPREADSHEET_ID` 是否正確
   - 檢查 Google Sheets 的權限設置
