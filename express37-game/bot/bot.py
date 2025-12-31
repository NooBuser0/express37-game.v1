import asyncio
import logging
import os
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import database as db

# Настройки - замените на свои!
BOT_TOKEN = os.environ.get('BOT_TOKEN', '5525317765:AAHkmoxUk46uErcGp37zhUIaIk7XXP3Po1c')
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'https://YOUR_GITHUB_USERNAME.github.io/express37-game')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Регистрация пользователя
    user_id, auth_token = db.register_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    
    user_data = db.get_user_by_telegram_id(user.id)
    balance = user_data['balance']
    
    welcome_text = f"""
🎰 *ЭКСПРЕСС 37* 🎰

Добро пожаловать, {user.first_name}!

💰 Ваш баланс: *{balance:,.0f} ₽*

🎲 Угадайте номер диапазона от 1 до 37!
💵 Коэффициенты от x2 до x35

Нажмите кнопку ниже, чтобы начать игру!
    """
    
    keyboard = [
        [InlineKeyboardButton(
            "🎮 ИГРАТЬ",
            web_app=WebAppInfo(url=f"{WEBAPP_URL}?token={auth_token}")
        )],
        [InlineKeyboardButton("💰 Баланс", callback_data="balance")]
    ]
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user_by_telegram_id(user.id)
    
    if user_data:
        await update.message.reply_text(
            f"💰 Ваш баланс: *{user_data['balance']:,.0f} ₽*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("Используйте /start для регистрации")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance))
    
    logger.info("Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()