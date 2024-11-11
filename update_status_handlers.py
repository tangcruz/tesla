import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from google_sheets import read_sheet, update_sheet

logger = logging.getLogger(__name__)

async def handle_update_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    car_number = update.message.text
    logger.info(f"Handling status update for car number: {car_number}")
    context.user_data['car_number'] = car_number
    
    try:
        data = read_sheet()
        header = data[0]
        car_number_index = header.index('車號')
        
        row_number = next((data.index(row) + 1 for row in data if row[car_number_index] == car_number), None)
        logger.info(f"row_num:{row_number}, {header}, car_number_index: {car_number_index}, data:{data}")        
        if row_number:
            context.user_data['row_number'] = row_number
            keyboard = [
                [InlineKeyboardButton("更改狀態", callback_data='update_status_selection')],
                [InlineKeyboardButton("更改位置", callback_data='update_location_selection')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            logger.info("Sending update options to the user")
            await update.message.reply_text("請選擇要更新的內容:", reply_markup=reply_markup)
        else:
            logger.warning(f"No car found with number: {car_number}")
            await update.message.reply_text("沒有找到相關車輛，請重新輸入車號:")
    except Exception as e:
        logger.error(f"Error in handle_update_status: {str(e)}")
        await update.message.reply_text("處理您的請求時發生錯誤，請稍後再試。")

async def update_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    car_number = context.user_data.get('car_number')
    new_value = update.message.text 
    action = context.user_data.get('action')
    row_number = context.user_data.get('row_number')
    
    logger.info(f"Updating {action} for car number {car_number} to {new_value}")
    
    try:
        if row_number and action:
            data = read_sheet()
            header = data[0]
            
            if 1 <= row_number < len(data):
                if action == 'update_status':
                    index = header.index('狀態')
                    column = '狀態'
                elif action == 'update_location':
                    index = header.index('位置')
                    column = '位置'
                else:
                    raise ValueError(f"Invalid action: {action}")
                
                update_sheet(row_number, chr(index + 65), new_value)
                logger.info(f"Updated car number {car_number} {column} to {new_value}")
                await update.message.reply_text(f"車號 {car_number} 的{column}已更新為 {new_value}。")
                
                # Clear the action after successful update
                context.user_data.pop('action', None)
            else:
                logger.error(f"Invalid row number: {row_number}")
                await update.message.reply_text("發生錯誤：無效的行號。")
        else:
            logger.error(f"Missing data: row_number={row_number}, action={action}")
            await update.message.reply_text("發生錯誤：缺少必要的更新信息。")
    except Exception as e:
        logger.error(f"Error in update_status: {str(e)}")
        await update.message.reply_text("更新狀態或位置時發生錯誤，請稍後再試。")

async def handle_update_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    action = 'update_status' if query.data == 'update_status_selection' else 'update_location'
    context.user_data['action'] = action
    
    prompt = "請輸入新的狀態:" if action == 'update_status' else "請輸入新的位置:"
    await query.message.reply_text(prompt)
