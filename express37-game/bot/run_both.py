import threading
import subprocess
import os

def run_server():
    """Запуск Flask сервера"""
    port = os.environ.get('PORT', 5000)
    subprocess.run(['gunicorn', 'server:app', '--bind', f'0.0.0.0:{port}'])

def run_bot():
    """Запуск Telegram бота"""
    import bot
    bot.main()

if __name__ == '__main__':
    # Запускаем сервер в отдельном потоке
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Запускаем бота в основном потоке
    run_bot()
