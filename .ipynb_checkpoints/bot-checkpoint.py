# /Users/sulaxd/Documents/Tesla/bot.py
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers import start, button, handle_input
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot with your token
def run_bot(token: str) -> None:
    application = ApplicationBuilder().token(token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    
    # Start the bot
    logger.info("Starting the bot")
    application.run_polling()

# Main entry point
if __name__ == "__main__":
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No Telegram bot token provided")
        raise ValueError("No Telegram bot token provided")
    
    logger.info("Bot initialization")
    run_bot(token)

# /Users/sulaxd/Documents/Tesla/update_status_handlers.py
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
        if row_number:
            data = read_sheet()
            header = data[0]
            
            if 1 <= row_number < len(data):
                index = header.index('狀態') if action == 'update_status' else header.index('位置')
                update_sheet(row_number, chr(index + 65), new_value)
                logger.info(f"Updated car number {car_number} {action} to {new_value}")
                await update.message.reply_text(f"車號 {car_number} 的{action}已更新為 {new_value}。")
            else:
                logger.error(f"Invalid row number: {row_number}")
                await update.message.reply_text("發生錯誤：無效的行號。")
        else:
            logger.error("Row number not found in context.user_data")
            await update.message.reply_text("發生錯誤：未找到行號。")
    except Exception as e:
        logger.error(f"Error in update_status: {str(e)}")
        await update.message.reply_text("更新狀態或位置時發生錯誤，請稍後再試。")