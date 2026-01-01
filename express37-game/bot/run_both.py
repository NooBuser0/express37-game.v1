import threading
import subprocess
import os
import sys
import time

def run_server():
    """Запуск Flask сервера"""
    port = os.environ.get('PORT', 8080)
    os.system(f'gunicorn server:app --bind 0.0.0.0:{port} --timeout 120')

def run_bot():
    """Запуск Telegram бота"""
    time.sleep(5)  # Ждем запуска сервера
    print("🤖 Starting Telegram bot...")
    
    try:
        import bot
        bot.main()
    except Exception as e:
        print(f"❌ Bot error: {e}")

if __name__ == '__main__':
    print("🚀 Starting Express 37...")
    
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем сервер в основном потоке
    run_server()
