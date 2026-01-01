import asyncio
import logging
import os
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import database as db

# ===== НАСТРОЙКИ =====
BOT_TOKEN = os.environ.get('BOT_TOKEN', '5525317765:AAHkmoxUk46uErcGp37zhUIaIk7XXP3Po1c')
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'https://ВАШ_GITHUB_USERNAME.github.io/express37-game')

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

📊 *Коэффициенты:*
• 1 номер → ×35
• 2 номера → ×17  
• 3 номера → ×11
• 12 номеров → ×2.9
• 18 номеров → ×2

💵 Номиналы: 100₽, 500₽, 1000₽

Нажмите кнопку ниже, чтобы начать! 👇
    """
    
    # Ссылка на игру с токеном
    game_url = f"{WEBAPP_URL}?token={auth_token}"
    
    keyboard = [
        [InlineKeyboardButton(
            "🎮 ИГРАТЬ",
            web_app=WebAppInfo(url=game_url)
        )],
        [
            InlineKeyboardButton("💰 Баланс", callback_data="balance"),
            InlineKeyboardButton("📊 История", callback_data="history")
        ],
        [InlineKeyboardButton("ℹ️ Правила", callback_data="rules")]
    ]
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    logger.info(f"User {user.id} started bot. Token: {auth_token[:20]}...")

async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user_by_telegram_id(user.id)
    
    if user_data:
        await update.message.reply_text(
            f"💰 Ваш баланс: *{user_data['balance']:,.0f} ₽*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Вы не зарегистрированы. Используйте /start"
        )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🎰 *ЭКСПРЕСС 37 - Помощь*

*Команды:*
/start - Начать игру
/balance - Проверить баланс
/help - Это сообщение

*Как играть:*
1. Нажмите "ИГРАТЬ"
2. Выберите номинал фишки
3. Кликните на номера для ставки
4. Нажмите "КРУТИТЬ"
5. Получите выигрыш! 🎉

*Коэффициенты:*
1 номер = ×35
2 номера = ×17
3 номера = ×11
12 номеров = ×2.9
18 номеров = ×2

Удачи! 🍀
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    if not BOT_TOKEN or BOT_TOKEN == 'YOUR_BOT_TOKEN':
        logger.error("BOT_TOKEN not set!")
        return
        
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance_cmd))
    application.add_handler(CommandHandler("help", help_cmd))
    
    logger.info(f"🤖 Bot starting...")
    logger.info(f"📱 WebApp URL: {WEBAPP_URL}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
