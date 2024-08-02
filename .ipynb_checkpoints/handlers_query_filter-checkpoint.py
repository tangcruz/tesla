# /Users/sulaxd/Documents/Tesla/handlers_query_filter.py

import logging
from telegram import Update
from telegram.ext import ContextTypes
from google_sheets import read_sheet

logger = logging.getLogger(__name__)

# 查詢特定狀態的車輛
async def query_by_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    status_query = context.user_data.get('status_query')
    logger.info(f"Querying cars by status: {status_query}")
    if status_query:
        data = read_sheet()
        header = data[0]
        col_indices = [header.index('車號'), header.index('狀態'), header.index('單位'), header.index('位置')]
        extracted_data = [[row[col_indices[0]], row[col_indices[1]], row[col_indices[2]], row[col_indices[3]]] for row in data[1:]]

        message = f"狀態為 {status_query} 的車輛:\n\n"
        for row in extracted_data:
            if row[1] == status_query:
                message += "車號: " + row[0] + "\n狀態: " + row[1] + "\n單位: " + row[2] + "\n位置: " + row[3] + "\n\n"

        if not message.strip():
            message = "沒有找到相關車輛。"
    else:
        message = "請輸入狀態。"

    if update.callback_query:
        await update.callback_query.message.reply_text(message)
    else:
        await update.message.reply_text(message)

# 查詢特定車輛位置
async def query_by_car_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    car_number_query = context.user_data.get('car_number_query')
    logger.info(f"Querying car by number: {car_number_query}")
    if car_number_query:
        data = read_sheet()
        header = data[0]
        car_number_index = header.index('車號')
        location_index = header.index('位置')
        location = None
        for row in data:
            if row[car_number_index] == car_number_query:
                location = row[location_index]
                break

        message = f"車號 {car_number_query} 的位置: {location}" if location else "沒有找到相關車輛位置。"
    else:
        message = "請輸入車號。"

    if update.callback_query:
        await update.callback_query.message.reply_text(message)
    else:
        await update.message.reply_text(message)

# 查詢特定單位的車輛
async def query_by_unit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    unit_query = context.user_data.get('unit_query')
    logger.info(f"Querying cars by unit: {unit_query}")
    if unit_query:
        data = read_sheet()
        header = data[0]
        col_indices = [header.index('車號'), header.index('狀態'), header.index('單位'), header.index('位置')]
        extracted_data = [[row[col_indices[0]], row[col_indices[1]], row[col_indices[2]], row[col_indices[3]]] for row in data[1:]]

        message = f"單位為 {unit_query} 的車輛:\n\n"
        for row in extracted_data:
            if row[2] == unit_query:
                message += "車號: " + row[0] + "\n狀態: " + row[1] + "\n單位: " + row[2] + "\n位置: " + row[3] + "\n\n"

        if not message.strip():
            message = "沒有找到相關車輛。"
    else:
        message = "請輸入單位。"

    if update.callback_query:
        await update.callback_query.message.reply_text(message)
    else:
        await update.message.reply_text(message)