import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers_query_all import handle_car_number, query_all, query_all_locations
from handlers_query_filter import query_by_status, query_by_car_number, query_by_unit
from update_status_handlers import update_status, handle_update_status, handle_update_selection

logger = logging.getLogger(__name__)

KEYBOARD = [
    [InlineKeyboardButton("查詢車輛狀態", callback_data='query_status')],
    [InlineKeyboardButton("查詢所有車輛", callback_data='query_all')],
    [InlineKeyboardButton("查詢所有車輛位置", callback_data='query_all_locations')],
    [InlineKeyboardButton("查詢特定車輛位置", callback_data='query_by_car_number')],
    [InlineKeyboardButton("查詢特定狀態的車輛", callback_data='query_by_status')],
    [InlineKeyboardButton("查詢特定單位的車輛", callback_data='query_by_unit')],
    [InlineKeyboardButton("更新車輛狀態或位置", callback_data='update_status')]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Start command received")
    reply_markup = InlineKeyboardMarkup(KEYBOARD)
    await update.message.reply_text("請選擇一個操作:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    logger.info(f"Callback data: {query.data}")
    context.user_data['callback_data'] = query.data
    
    if query.data == 'query_status':
        await query.message.reply_text("請輸入車號:")
        context.user_data['operation'] = 'query_status'
    elif query.data == 'query_all':
        await query_all(update, context)
    elif query.data == 'query_all_locations':
        await query_all_locations(update, context)
    elif query.data == 'query_by_car_number':
        await query.message.reply_text("請輸入車號:")
        context.user_data['operation'] = 'query_by_car_number'
    elif query.data == 'query_by_status':
        await query.message.reply_text("請輸入狀態:")
        context.user_data['operation'] = 'query_by_status'
    elif query.data == 'query_by_unit':
        await query.message.reply_text("請輸入單位:")
        context.user_data['operation'] = 'query_by_unit'
    elif query.data == 'update_status':
        await query.message.reply_text("請輸入車號:")
        context.user_data['operation'] = 'update_status'
    elif query.data in ['update_status_selection', 'update_location_selection']:
        await handle_update_selection(update, context)
    else:
        logger.warning(f"Unhandled callback query: {query.data}")
        await query.message.reply_text("無效的操作，請重新選擇。")

async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    operation = context.user_data.get('operation')
    logger.info(f"Handling input for operation: {operation}")
    
    try:
        if operation == 'query_status':
            await handle_car_number(update, context)
        elif operation == 'update_status':
            if 'car_number' not in context.user_data:
                await handle_update_status(update, context)
            else:
                action = context.user_data.get('action', 'update_status')
                context.user_data[f'new_{action.split("_")[1]}'] = update.message.text
                await update_status(update, context)
        elif operation == 'query_by_status':
            context.user_data['status_query'] = update.message.text
            await query_by_status(update, context)
        elif operation == 'query_by_unit':
            context.user_data['unit_query'] = update.message.text
            await query_by_unit(update, context)
        elif operation == 'query_by_car_number':
            context.user_data['car_number_query'] = update.message.text
            await query_by_car_number(update, context)
        else:
            logger.warning(f"Unhandled operation: {operation}")
            await update.message.reply_text("無效的操作，請重新選擇。")
    except Exception as e:
        logger.error(f"Error in handle_input: {str(e)}")
        await update.message.reply_text("處理您的輸入時發生錯誤，請稍後再試。")