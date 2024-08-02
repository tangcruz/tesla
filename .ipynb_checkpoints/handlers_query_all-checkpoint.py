# /Users/sulaxd/Documents/Tesla/handlers_query_all.py
import logging
from telegram import Update
from telegram.ext import ContextTypes
from google_sheets import read_sheet

logger = logging.getLogger(__name__)

async def handle_car_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    car_number = update.message.text
    logger.info(f"Received car number: {car_number}")
    
    try:
        data = read_sheet()
        header = data[0]
        col_indices = {
            'car_number': header.index('車號'),
            'status': header.index('狀態'),
            'unit': header.index('單位'),
            'location': header.index('位置')
        }
        
        for row in data[1:]:
            if row[col_indices['car_number']] == car_number:
                row_number = data.index(row) + 1
                car_info = {
                    'status': row[col_indices['status']],
                    'unit': row[col_indices['unit']],
                    'location': row[col_indices['location']]
                }
                context.user_data.update({
                    'car_number': car_number,
                    'row_number': row_number
                })
                
                message = (f"車號: {car_number}\n"
                           f"狀態: {car_info['status']}\n"
                           f"單位: {car_info['unit']}\n"
                           f"位置: {car_info['location']}")
                
                logger.info(f"Found car: {message}")
                await update.message.reply_text(message)
                return
        
        logger.warning(f"No car found with number: {car_number}")
        await update.message.reply_text("沒有找到相關車輛，請重新輸入車號:")
    except Exception as e:
        logger.error(f"Error in handle_car_number: {str(e)}")
        await update.message.reply_text("處理您的請求時發生錯誤，請稍後再試。")

async def query_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Querying all cars")
    
    try:
        data = read_sheet()
        header = data[0]
        col_indices = [header.index('車號'), header.index('狀態'), header.index('單位'), header.index('位置')]
        
        extracted_data = [[row[i] for i in col_indices] for row in data[1:]]
        
        message = "所有車輛:\n\n"
        for row in extracted_data:
            message += f"車號: {row[0]}\n狀態: {row[1]}\n單位: {row[2]}\n位置: {row[3]}\n\n"
        
        if not extracted_data:
            message = "沒有找到任何車輛。"
        
        logger.info(f"Query all cars result: {len(extracted_data)} cars found")
        
        if update.callback_query:
            await update.callback_query.message.reply_text(message)
        else:
            await update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error in query_all: {str(e)}")
        error_message = "查詢所有車輛時發生錯誤，請稍後再試。"
        if update.callback_query:
            await update.callback_query.message.reply_text(error_message)
        else:
            await update.message.reply_text(error_message)

async def query_all_locations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Querying all car locations")
    
    try:
        data = read_sheet()
        if not data:
            logger.error("No data returned from read_sheet()")
            raise ValueError("No valid data returned from API")

        header = data[0]
        if len(header) < 2:
            logger.error(f"Invalid header: {header}")
            raise ValueError("Invalid data structure")

        col_indices = [header.index('車號'), header.index('位置')]
        
        location_dict = {}
        for row in data[1:]:
            if len(row) > max(col_indices):
                location = row[col_indices[1]]
                car_number = row[col_indices[0]]
                location_dict.setdefault(location, []).append(car_number)
            else:
                logger.warning(f"Skipping invalid row: {row}")
        
        message = ""
        for location, car_numbers in location_dict.items():
            message += f"【{location}】\n"
            message += "，".join(car_numbers) + "\n\n"
        
        if not message.strip():
            message = "沒有找到任何車輛位置。"
        
        logger.info(f"Query all locations result: {len(location_dict)} locations found")
        
        if update.callback_query:
            await update.callback_query.message.reply_text(message)
        else:
            await update.message.reply_text(message)
    except ValueError as ve:
        logger.error(f"ValueError in query_all_locations: {str(ve)}")
        error_message = "查詢所有車輛位置時發生數據錯誤，請稍後再試。"
        if update.callback_query:
            await update.callback_query.message.reply_text(error_message)
        else:
            await update.message.reply_text(error_message)
    except Exception as e:
        logger.error(f"Error in query_all_locations: {str(e)}")
        error_message = "查詢所有車輛位置時發生未知錯誤，請稍後再試。"
        if update.callback_query:
            await update.callback_query.message.reply_text(error_message)
        else:
            await update.message.reply_text(error_message)