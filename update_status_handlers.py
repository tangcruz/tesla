# /Users/sulaxd/Documents/Tesla/update_status_handlers.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from google_sheets import read_sheet, update_sheet

logger = logging.getLogger(__name__)

# 處理狀態更新
async def handle_update_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    car_number = update.message.text
    logger.info(f"Handling status update for car number: {car_number}")
    context.user_data['car_number'] = car_number

    data = read_sheet()
    header = data[0]
    car_number_index = header.index('車號')
    row_number = next((data.index(row) + 1 for row in data if row[car_number_index] == car_number), None)

    if row_number:
        context.user_data['row_number'] = row_number
        keyboard = [
            [InlineKeyboardButton("更改狀態", callback_data='update_status_selection')],
            [InlineKeyboardButton("更改位置", callback_data='update_location_selection')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        logger.info("Sending update options to the user")
        await update.message.reply_text("請選擇一個操作:", reply_markup=reply_markup)
    else:
        logger.warning("No car found with the given number for update")
        await update.message.reply_text("沒有找到相關車輛，請重新輸入車號:")

# 更新車輛狀態或位置到 Google Sheets
async def update_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    car_number = context.user_data.get('car_number')
    # query = update.callback_query
    new_value = update.message.text 
    action = context.user_data.get('action')
    # new_value = update.message.text
    print(action)
    print(new_value)
    print(car_number)
    row_number = context.user_data.get('row_number')

    if row_number:
        data = read_sheet()
        header = data[0]
        # 確保 row_number 是對的
        if 1 <= row_number < len(data):
            index = header.index('狀態') if action == 'update_status' else header.index('位置')
            update_sheet(row_number, chr(index + 65), new_value)
            logger.info(f"Updated car number {car_number} to {action}: {new_value}")
            await update.message.reply_text(f"車號 {car_number} 的{action}已更新為 {new_value}。")
        else:
            logger.error(f"Invalid row number: {row_number}")
            await update.message.reply_text("發生錯誤：無效的行號。")
    else:
        logger.error("Row number not found in context.user_data")
        await update.message.reply_text("發生錯誤：未找到行號。")