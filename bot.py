import nest_asyncio
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers import start, button, handle_status_selection, handle_input

# 设置日志级别
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def run_bot():
    nest_asyncio.apply()
    
    application = ApplicationBuilder().token('7291139880:AAHPcfpuFQGN-_WOMfKBLRtXKrQft-ycVhc').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CallbackQueryHandler(handle_status_selection, pattern='^(未整備車輛|已整備車輛|出租車輛|車主使用)$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

    application.run_polling()