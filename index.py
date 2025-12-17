import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Токен бота и ID для уведомлений
BOT_TOKEN = "8250642305:AAFYNFumehjQlyXHK0Myt92I2GQS8ReJMKU"
YOUR_CHAT_ID = 6369347678
SECOND_CHAT_ID = 973645913  # Второй получатель уведомлений

# Переменная для хранения данных анкеты
user_data = {}

# Команда /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Привет я помогу тебе купить машину твоей мечты!')

# Команда /buy - начало заполнения анкеты
async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {'step': 1}  # Начинаем заполнение анкеты
    
    question = """Заполни эту анкету.
Отправь мне одним сообщением через запятую или с новой строки:
1. Какую марку и модель машины хочешь?
2. Цвет машины?
3. На какой бюджет рассчитываешь?
4. Укажите свой номер телефона для связи.

Пример:
Мерседес S-класс
Черный
5000000 рублей
+7 (999) 123-45-67"""

    await update.message.reply_text(question)

# Обработка текстовых сообщений (ответы на анкету)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Если пользователь начал заполнять анкету
    if user_id in user_data and user_data[user_id]['step'] == 1:
        # Сохраняем данные анкеты
        user_data[user_id]['answers'] = text
        user_data[user_id]['step'] = 2  # Завершаем анкету
        
        # Отправляем подтверждение пользователю
        await update.message.reply_text('Спасибо! Твоя анкета принята. Мы свяжемся с тобой в ближайшее время!')
        
        # Отправляем анкету обоим получателям
        user_info = f"""
📋 Новая анкета на покупку автомобиля:

👤 Пользователь: @{update.effective_user.username} (ID: {user_id})
📝 Ответы:
{text}

---
Для связи: https://t.me/{update.effective_user.username}
        """
        
        try:
            # Отправляем сообщение первому получателю
            await context.bot.send_message(
                chat_id=YOUR_CHAT_ID,
                text=user_info
            )
            
            # Отправляем сообщение второму получателю
            await context.bot.send_message(
                chat_id=SECOND_CHAT_ID,
                text=user_info
            )
            
            logging.info(f"Анкета отправлена обоим получателям от пользователя {user_id}")
            
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения: {e}")
            # Пробуем отправить хотя бы одному получателю
            try:
                await context.bot.send_message(
                    chat_id=YOUR_CHAT_ID,
                    text=f"⚠️ Ошибка отправки второму получателю\n\n{user_info}"
                )
            except:
                pass
        
        # Удаляем данные пользователя после отправки
        del user_data[user_id]
    
    # Если пользователь просто пишет сообщение без команды /buy
    elif user_id not in user_data:
        await update.message.reply_text('Используй команду /buy чтобы заполнить анкету на покупку автомобиля!')

# Обработка ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f'Ошибка: {context.error}')

def main():
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("buy", buy_command))
    
    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("Бот запущен...")
    print(f"Уведомления будут отправляться на ID: {YOUR_CHAT_ID} и {SECOND_CHAT_ID}")
    application.run_polling()

if __name__ == '__main__':
    main()
