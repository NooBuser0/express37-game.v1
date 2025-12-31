from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import os
import database as db

app = Flask(__name__)
CORS(app)

# Коэффициенты
COEFFICIENTS = {
    1: 35,
    2: 17,
    3: 11,
    4: 8,
    6: 5,
    12: 2.9,
    18: 2
}

@app.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'message': 'Express 37 API is running!'
    })

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    telegram_id = data.get('telegram_id')
    username = data.get('username')
    first_name = data.get('first_name')
    
    if not telegram_id:
        return jsonify({'success': False, 'error': 'telegram_id required'}), 400
    
    user_id, auth_token = db.register_user(telegram_id, username, first_name)
    user = db.get_user_by_telegram_id(telegram_id)
    
    return jsonify({
        'success': True,
        'token': auth_token,
        'user': {
            'id': user['id'],
            'balance': user['balance'],
            'username': user['username'],
            'first_name': user['first_name']
        }
    })

@app.route('/api/user', methods=['GET'])
def get_user():
    token = request.args.get('token')
    
    if not token:
        return jsonify({'success': False, 'error': 'Token required'}), 400
    
    user = db.get_user_by_token(token)
    
    if user:
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'first_name': user['first_name'],
                'balance': user['balance']
            }
        })
    return jsonify({'success': False, 'error': 'User not found'}), 404

@app.route('/api/balance', methods=['GET'])
def get_balance():
    token = request.args.get('token')
    user = db.get_user_by_token(token)
    
    if user:
        return jsonify({'success': True, 'balance': user['balance']})
    return jsonify({'success': False, 'error': 'User not found'}), 404

@app.route('/api/spin', methods=['POST'])
def spin():
    data = request.json
    token = data.get('token')
    bets = data.get('bets', [])
    
    user = db.get_user_by_token(token)
    
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Считаем общую сумму ставок
    total_bet = sum(bet.get('amount', 0) for bet in bets)
    
    if total_bet > user['balance']:
        return jsonify({'success': False, 'error': 'Insufficient balance'}), 400
    
    # Списываем ставку
    db.update_balance(user['id'], -total_bet)
    
    # Бросаем кубики
    while True:
        dice1_throw1 = random.randint(1, 6)
        dice2_throw1 = random.randint(1, 6)
        dice1_throw2 = random.randint(1, 6)
        dice2_throw2 = random.randint(1, 6)
        
        # Проверяем на 6-6-6-6
        if not (dice1_throw1 == 6 and dice2_throw1 == 6 and 
                dice1_throw2 == 6 and dice2_throw2 == 6):
            break
    
    # Определяем выигрышный номер (1-37)
    combo_sum = dice1_throw1 + dice2_throw1 + dice1_throw2 + dice2_throw2
    winning_number = ((combo_sum - 4) % 37) + 1
    
    # Обрабатываем ставки
    total_win = 0
    results = []
    
    for bet in bets:
        bet_numbers = bet.get('numbers', [])
        amount = bet.get('amount', 0)
        
        if winning_number in bet_numbers:
            coefficient = COEFFICIENTS.get(len(bet_numbers), 35)
            win_amount = amount * coefficient
            total_win += win_amount
            results.append({
                'numbers': bet_numbers,
                'amount': amount,
                'won': True,
                'win_amount': win_amount
            })
        else:
            results.append({
                'numbers': bet_numbers,
                'amount': amount,
                'won': False,
                'win_amount': 0
            })
    
    # Начисляем выигрыш
    if total_win > 0:
        db.update_balance(user['id'], total_win)
    
    new_balance = db.get_balance(user['id'])
    
    # Сохраняем раунд
    db.save_game_round(
        user['id'],
        dice1_throw1, dice2_throw1,
        dice1_throw2, dice2_throw2,
        winning_number,
        total_bet,
        total_win
    )
    
    return jsonify({
        'success': True,
        'dice': {
            'throw1': {'dice1': dice1_throw1, 'dice2': dice2_throw1},
            'throw2': {'dice1': dice1_throw2, 'dice2': dice2_throw2}
        },
        'winning_number': winning_number,
        'total_win': total_win,
        'new_balance': new_balance,
        'results': results
    })

@app.route('/api/demo', methods=['POST'])
def demo_register():
    """Демо-регистрация без Telegram"""
    demo_id = random.randint(100000, 999999)
    user_id, auth_token = db.register_user(demo_id, f'demo_{demo_id}', 'Demo User')
    user = db.get_user_by_telegram_id(demo_id)
    
    return jsonify({
        'success': True,
        'token': auth_token,
        'user': {
            'id': user['id'],
            'balance': user['balance'],
            'first_name': 'Demo User'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)