import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers import start, button, handle_input
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def run_bot(token: str) -> None:
    application = ApplicationBuilder().token(token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    
    # Start the bot
    logger.info("Starting the bot")
    application.run_polling()

if __name__ == "__main__":
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No Telegram bot token provided")
        raise ValueError("No Telegram bot token provided")
    
    logger.info("Bot initialization")
    run_bot(token)