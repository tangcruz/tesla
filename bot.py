import logging
import nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from datastore_client import save_car_data, get_car_data, get_all_cars, get_cars_by_status, get_cars_by_unit

# 设置日志级别
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Handle car number input
async def handle_car_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    car_number = update.message.text
    logger.info(f"Received car number: {car_number}")
    car_data = get_car_data(car_number)

    if car_data:
        context.user_data['car_number'] = car_number
        message = f"車號: {car_number}\n狀態: {car_data['status']}\n單位: {car_data['unit']}"
        logger.info(f"Found car: {message}")
        await update.message.reply_text(message)
    else:
        logger.warning("No car found with the given number")
        await update.message.reply_text("沒有找到相關車輛，請重新輸入車號:")

# Handle status update
async def handle_update_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    car_number = update.message.text
    logger.info(f"Handling status update for car number: {car_number}")
    context.user_data['car_number'] = car_number
    car_data = get_car_data(car_number)

    if car_data:
        keyboard = [
            [InlineKeyboardButton("未整備車輛", callback_data='未整備車輛')],
            [InlineKeyboardButton("已整備車輛", callback_data='已整備車輛')],
            [InlineKeyboardButton("出租車輛", callback_data='出租車輛')],
            [InlineKeyboardButton("車主使用", callback_data='車主使用')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        logger.info("Sending status update options to the user")
        await update.message.reply_text("請選擇新的狀態:", reply_markup=reply_markup)
    else:
        logger.warning("No car found with the given number for status update")
        await update.message.reply_text("沒有找到相關車輛，請重新輸入車號:")


# Handle status selection
async def handle_status_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    status = query.data
    car_number = context.user_data.get('car_number')
    if car_number and status:
        save_car_data(car_number, status, get_car_data(car_number)['unit'])
        logger.info(f"Updated car number {car_number} to status {status}")
        await query.message.reply_text(f"車號 {car_number} 的狀態已更新為 {status}。")
    else:
        logger.error("Missing data for update.")
        await query.message.reply_text("請依次輸入車號和狀態。")

# Query all cars
async def query_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Querying all cars")
    cars = get_all_cars()

    message = "所有車輛:\n\n"
    for car in cars:
        message += f"車號: {car.key.name}, 狀態: {car['status']}, 單位: {car['unit']}\n"

    if not cars:
        message = "沒有找到任何車輛。"

    if update.callback_query:
        await update.callback_query.message.reply_text(message)
    else:
        await update.message.reply_text(message)

# Query cars by status
async def query_by_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    status_query = context.user_data.get('status_query')
    logger.info(f"Querying cars by status: {status_query}")
    if status_query:
        cars = get_cars_by_status(status_query)

        message = f"狀態為 {status_query} 的車輛:\n\n"
        for car in cars:
            message += f"車號: {car.key.name}, 狀態: {car['status']}, 單位: {car['unit']}\n"

        if not cars:
            message = "沒有找到相關車輛。"
    else:
        message = "請輸入狀態。"

    if update.callback_query:
        await update.callback_query.message.reply_text(message)
    else:
        await update.message.reply_text(message)


# Query cars by unit
async def query_by_unit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    unit_query = context.user_data.get('unit_query')
    logger.info(f"Querying cars by unit: {unit_query}")
    if unit_query:
        cars = get_cars_by_unit(unit_query)

        message = f"單位為 {unit_query} 的車輛:\n\n"
        for car in cars:
            message += f"車號: {car.key.name}, 狀態: {car['status']}, 單位: {car['unit']}\n"

        if not cars:
            message = "沒有找到相關車輛。"
    else:
        message = "請輸入單位。"

    if update.callback_query:
        await update.callback_query.message.reply_text(message)
    else:
        await update.message.reply_text(message)

# Start menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("查詢車輛狀態", callback_data='query_status')],
        [InlineKeyboardButton("查詢所有車輛", callback_data='query_all')],
        [InlineKeyboardButton("查詢特定狀態的車輛", callback_data='query_by_status')],
        [InlineKeyboardButton("查詢特定單位的車輛", callback_data='query_by_unit')],
        [InlineKeyboardButton("更新車輛狀態", callback_data='update_status')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("請選擇一個操作:", reply_markup=reply_markup)

# Handle menu callbacks
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
    elif query.data == 'query_by_status':
        await query.message.reply_text("請輸入狀態:")
        context.user_data['operation'] = 'query_by_status'
    elif query.data == 'query_by_unit':
        await query.message.reply_text("請輸入單位:")
        context.user_data['operation'] = 'query_by_unit'
    elif query.data == 'update_status':
        await query.message.reply_text("請輸入車號:")
        context.user_data['operation'] = 'update_status'
    else:
        await update_status(update, context)

# Handle user input
async def handle_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    operation = context.user_data.get('operation')
    logger.info(f"Operation: {operation}")

    if operation == 'query_status':
        await handle_car_number(update, context)
    elif operation == 'update_status':
        if 'car_number' not in context.user_data:
            await handle_update_status(update, context)
        elif 'status' not in context.user_data:
            await handle_status_selection(update, context)
    elif operation == 'query_by_status':
        context.user_data['status_query'] = update.message.text
        await query_by_status(update, context)
    elif operation == 'query_by_unit':
        context.user_data['unit_query'] = update.message.text
        await query_by_unit(update, context)

# Main program
def main() -> None:
    nest_asyncio.apply()
    
    application = ApplicationBuilder().token('7291139880:AAHPcfpuFQGN-_WOMfKBLRtXKrQft-ycVhc').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CallbackQueryHandler(handle_status_selection, pattern='^(未整備車輛|已整備車輛|出租車輛|車主使用)$'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))

    application.run_polling()

if __name__ == "__main__":
    main()