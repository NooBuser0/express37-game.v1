import logging
import os
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import database as db

# ===== НАСТРОЙКИ =====
BOT_TOKEN = os.environ.get('BOT_TOKEN', '5525317765:AAHkmoxUk46uErcGp37zhUIaIk7XXP3Po1c')
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'https://noobuser0.github.io/express37-game.v1')

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

Добро пожаловать, *{user.first_name}*!

💰 Ваш баланс: *{balance:,.0f} ₽*

━━━━━━━━━━━━━━━
🎲 Угадайте номер от 1 до 37!

📊 *Коэффициенты:*
• 1 номер → ×35
• 2 номера → ×17  
• 3 номера → ×11
• 12 номеров → ×2.9
• 18 номеров → ×2

💵 Ставки: 100₽ | 500₽ | 1000₽
━━━━━━━━━━━━━━━

👇 Нажмите кнопку чтобы играть!
    """
    
    game_url = f"{WEBAPP_URL}?token={auth_token}"
    logger.info(f"Game URL for user {user.id}: {game_url}")
    
    keyboard = [
        [InlineKeyboardButton(
            "🎮 ИГРАТЬ",
            web_app=WebAppInfo(url=game_url)
        )],
        [
            InlineKeyboardButton("💰 Баланс", callback_data="balance"),
            InlineKeyboardButton("📊 Правила", callback_data="rules")
        ]
    ]
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_data = db.get_user_by_telegram_id(user.id)
    
    if query.data == "balance":
        if user_data:
            text = f"💰 Ваш баланс: *{user_data['balance']:,.0f} ₽*"
        else:
            text = "❌ Используйте /start для регистрации"
        await query.message.reply_text(text, parse_mode='Markdown')
    
    elif query.data == "rules":
        rules_text = """
📖 *ПРАВИЛА ЭКСПРЕСС 37*

🎲 Во время игры бросаются кубики. Вам нужно угадать номер диапазона от 1 до 37.

*Типы ставок:*
• На 1 номер — коэф. ×35
• На 2 номера — коэф. ×17
• На 3 номера — коэф. ×11
• На 4 номера — коэф. ×8
• На 6 номеров — коэф. ×5
• На 12 номеров — коэф. ×2.9
• На 18 номеров — коэф. ×2

*Номиналы фишек:* 100₽, 500₽, 1000₽

Удачи! 🍀
        """
        await query.message.reply_text(rules_text, parse_mode='Markdown')

async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user_by_telegram_id(user.id)
    
    if user_data:
        await update.message.reply_text(
            f"💰 Ваш баланс: *{user_data['balance']:,.0f} ₽*",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ Используйте /start для регистрации")

def main():
    logger.info(f"🤖 Bot Token: {BOT_TOKEN[:20]}...")
    logger.info(f"🌐 WebApp URL: {WEBAPP_URL}")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("balance", balance_cmd))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("✅ Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
