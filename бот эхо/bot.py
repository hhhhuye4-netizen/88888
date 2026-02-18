import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен вашего бота
TOKEN = '8593494306:AAGJT0e-8TfoySHCglSMM6-QLlFE7_tFBSU'

# Хранилище состояний пользователей (в реальном проекте лучше использовать базу данных)
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет стартовое сообщение с кнопкой при команде /start."""
    user_id = update.effective_user.id
    
    # Сбрасываем состояние пользователя
    user_states[user_id] = 'waiting_for_start'
    
    # Создаем клавиатуру с кнопкой
    keyboard = [
        [InlineKeyboardButton("начать", callback_data='start_button')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем сообщение с кнопкой
    await update.message.reply_text(
        "Привет! Я бот Эхо. Отправь мне любое сообщение, и я его точно повторю.",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает нажатие на кнопку 'начать'."""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Отвечаем на нажатие кнопки
    await query.answer()
    
    # Меняем состояние пользователя
    user_states[user_id] = 'ready_to_echo'
    
    # Изменяем сообщение или отправляем новое
    await query.edit_message_text(text="Отлично! Начинаем. Напиши любое слово, и я его повторю.")
    
    # Также можно отправить новое сообщение:
    # await query.message.reply_text("Отлично! Начинаем. Напиши любое слово, и я его повторю.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает текстовые сообщения от пользователя."""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Проверяем состояние пользователя
    if user_id not in user_states:
        # Если пользователь не нажал "начать", отправляем стартовое сообщение
        keyboard = [
            [InlineKeyboardButton("начать", callback_data='start_button')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Привет! Я бот Эхо. Отправь мне любое сообщение, и я его точно повторю.\n\n"
            "Сначала нажми кнопку 'начать'",
            reply_markup=reply_markup
        )
        user_states[user_id] = 'waiting_for_start'
        return
    
    if user_states[user_id] == 'ready_to_echo':
        # Повторяем сообщение пользователя
        await update.message.reply_text(f"Эхо: {text}")
    else:
        # Пользователь еще не нажал "начать"
        keyboard = [
            [InlineKeyboardButton("начать", callback_data='start_button')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Сначала нажми кнопку 'начать' чтобы начать",
            reply_markup=reply_markup
        )

async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Альтернативная команда /echo для быстрого старта."""
    user_id = update.effective_user.id
    user_states[user_id] = 'ready_to_echo'
    
    await update.message.reply_text("Отлично! Начинаем. Напиши любое слово, и я его повторю.")

def main() -> None:
    """Запуск бота."""
    # Создаем приложение и передаем токен
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("echo", echo_command))
    application.add_handler(CallbackQueryHandler(button_callback, pattern='start_button'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    print("Бот запущен! Отправьте /start в Telegram")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()