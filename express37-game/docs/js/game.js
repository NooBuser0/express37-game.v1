// ===== КОНФИГУРАЦИЯ =====
// ВАЖНО: Замените на URL вашего Railway сервера после деплоя!
const API_URL = 'https://bot-rollete.railway.internal'; // Пока пустой, будет работать в демо-режиме

// ===== СОСТОЯНИЕ ИГРЫ =====
let authToken = '';
let currentBalance = 10000;
let selectedChip = 500;
let bets = {};
let isSpinning = false;

// Коэффициенты
const COEFFICIENTS = {
    1: 35, 2: 17, 3: 11, 4: 8, 6: 5, 12: 2.9, 18: 2
};

// Красные номера
const RED_NUMBERS = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36];

// Telegram WebApp
const tg = window.Telegram?.WebApp;

// ===== ИНИЦИАЛИЗАЦИЯ =====
document.addEventListener('DOMContentLoaded', async () => {
    console.log('🎰 Express 37 Loading...');
    
    // Получаем токен из URL
    const urlParams = new URLSearchParams(window.location.search);
    authToken = urlParams.get('token') || '';
    
    // Инициализация Telegram WebApp
    if (tg) {
        tg.ready();
        tg.expand();
        document.body.style.backgroundColor = tg.backgroundColor || '#0d0d0d';
    }
    
    // Инициализация игры
    generateNumbersGrid();
    setupEventListeners();
    
    // Загрузка данных пользователя
    await loadUserData();
    
    // Скрываем загрузку
    setTimeout(() => {
        document.getElementById('loading-screen').classList.add('hidden');
    }, 500);
});

// ===== ГЕНЕРАЦИЯ ПОЛЯ =====
function generateNumbersGrid() {
    const grid = document.getElementById('numbers-grid');
    grid.innerHTML = '';
    
    for (let i = 1; i <= 37; i++) {
        const cell = document.createElement('div');
        cell.className = 'number-cell';
        cell.dataset.number = i;
        
        if (i === 37) {
            cell.classList.add('green');
        } else if (RED_NUMBERS.includes(i)) {
            cell.classList.add('red');
        } else {
            cell.classList.add('black');
        }
        
        cell.innerHTML = `<span>${i}</span>`;
        cell.addEventListener('click', () => handleNumberClick(i));
        grid.appendChild(cell);
    }
}

// ===== ОБРАБОТЧИКИ СОБЫТИЙ =====
function setupEventListeners() {
    // Выбор фишек
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.querySelectorAll('.chip').forEach(c => c.classList.remove('selected'));
            chip.classList.add('selected');
            selectedChip = parseInt(chip.dataset.value);
            vibrate('light');
        });
    });
    
    // Специальные ставки
    document.querySelectorAll('.special-bet').forEach(bet => {
        bet.addEventListener('click', () => handleSpecialBet(bet));
    });
    
    // Кнопки
    document.getElementById('btn-clear').addEventListener('click', clearBets);
    document.getElementById('btn-spin').addEventListener('click', spin);
}

// ===== ЗАГРУЗКА ДАННЫХ =====
async function loadUserData() {
    // Сначала пробуем загрузить с сервера
    if (authToken && API_URL) {
        try {
            const response = await fetch(`${API_URL}/api/user?token=${authToken}`);
            const data = await response.json();
            
            if (data.success) {
                currentBalance = data.user.balance;
                updateBalanceDisplay();
                console.log('✅ User loaded from server');
                return;
            }
        } catch (error) {
            console.log('⚠️ Server unavailable, using demo mode');
        }
    }
    
    // Демо режим
    console.log('🎮 Demo mode active');
    currentBalance = 10000;
    updateBalanceDisplay();
}

// ===== ОБРАБОТКА СТАВОК =====
function handleNumberClick(number) {
    if (isSpinning) return;
    
    const totalBets = Object.values(bets).reduce((sum, val) => sum + val, 0);
    
    if (currentBalance - totalBets < selectedChip && !bets[number]) {
        showNotification('Недостаточно средств!', 'error');
        vibrate('error');
        return;
    }
    
    vibrate('light');
    
    if (bets[number]) {
        bets[number] += selectedChip;
    } else {
        bets[number] = selectedChip;
    }
    
    updateBetsDisplay();
    updateCellDisplay(number);
}

function handleSpecialBet(betElement) {
    if (isSpinning) return;
    
    const numbers = betElement.dataset.numbers.split(',').map(n => parseInt(n));
    const totalBets = Object.values(bets).reduce((sum, val) => sum + val, 0);
    
    if (currentBalance - totalBets < selectedChip) {
        showNotification('Недостаточно средств!', 'error');
        vibrate('error');
        return;
    }
    
    vibrate('light');
    
    const betPerNumber = selectedChip / numbers.length;
    
    numbers.forEach(num => {
        if (bets[num]) {
            bets[num] += betPerNumber;
        } else {
            bets[num] = betPerNumber;
        }
        updateCellDisplay(num);
    });
    
    betElement.classList.add('selected');
    updateBetsDisplay();
}

function updateCellDisplay(number) {
    const cell = document.querySelector(`.number-cell[data-number="${number}"]`);
    if (!cell) return;
    
    let chipEl = cell.querySelector('.chip-on-cell');
    
    if (bets[number]) {
        cell.classList.add('selected');
        
        if (!chipEl) {
            chipEl = document.createElement('div');
            chipEl.className = 'chip-on-cell';
            cell.appendChild(chipEl);
        }
        
        const amount = bets[number];
        chipEl.textContent = amount >= 1000 ? `${(amount/1000).toFixed(1)}k` : Math.round(amount);
    } else {
        cell.classList.remove('selected');
        if (chipEl) chipEl.remove();
    }
}

function updateBalanceDisplay() {
    document.getElementById('balance').textContent = formatMoney(currentBalance);
}

function updateBetsDisplay() {
    const total = Object.values(bets).reduce((sum, val) => sum + val, 0);
    document.getElementById('total-bet').textContent = formatMoney(total);
    
    // Расчет потенциального выигрыша
    const betCount = Object.keys(bets).length;
    let coefficient = COEFFICIENTS[betCount] || COEFFICIENTS[1];
    
    // Для групповых ставок
    if (betCount === 12) coefficient = COEFFICIENTS[12];
    else if (betCount === 18 || betCount === 19) coefficient = COEFFICIENTS[18];
    else if (betCount >= 6) coefficient = COEFFICIENTS[6];
    
    const potentialWin = total * coefficient;
    document.getElementById('potential-win').textContent = formatMoney(potentialWin);
}

function formatMoney(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function clearBets() {
    if (isSpinning) return;
    
    vibrate('light');
    bets = {};
    
    document.querySelectorAll('.number-cell').forEach(cell => {
        cell.classList.remove('selected', 'winner');
        const chip = cell.querySelector('.chip-on-cell');
        if (chip) chip.remove();
    });
    
    document.querySelectorAll('.special-bet').forEach(bet => {
        bet.classList.remove('selected');
    });
    
    updateBetsDisplay();
    document.getElementById('win-info').classList.remove('show');
}

// ===== КРУТИТЬ =====
async function spin() {
    if (isSpinning) return;
    
    const betNumbers = Object.keys(bets).map(n => parseInt(n));
    
    if (betNumbers.length === 0) {
        showNotification('Сделайте ставку!', 'warning');
        vibrate('warning');
        return;
    }
    
    isSpinning = true;
    document.getElementById('btn-spin').disabled = true;
    document.getElementById('win-info').classList.remove('show');
    
    // Списываем ставку
    const totalBet = Object.values(bets).reduce((sum, val) => sum + val, 0);
    currentBalance -= totalBet;
    updateBalanceDisplay();
    
    // Анимация кубиков
    startDiceAnimation();
    vibrate('medium');
    
    // Генерируем результат (локально или с сервера)
    let result;
    
    if (authToken && API_URL) {
        try {
            const betsToSend = Object.entries(bets).map(([num, amount]) => ({
                numbers: [parseInt(num)],
                amount: amount
            }));
            
            const response = await fetch(`${API_URL}/api/spin`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: authToken, bets: betsToSend })
            });
            
            result = await response.json();
            if (!result.success) throw new Error(result.error);
            
            // Обновляем баланс с сервера
            currentBalance = result.new_balance;
        } catch (error) {
            console.log('Using local spin:', error);
            result = localSpin(betNumbers, totalBet);
        }
    } else {
        result = localSpin(betNumbers, totalBet);
    }
    
    // Показываем результат через 2.5 секунды
    setTimeout(() => {
        showResult(result);
    }, 2500);
}

function localSpin(betNumbers, totalBet) {
    // Бросаем кубики
    let dice;
    do {
        dice = {
            throw1: { dice1: randInt(1, 6), dice2: randInt(1, 6) },
            throw2: { dice1: randInt(1, 6), dice2: randInt(1, 6) }
        };
    } while (dice.throw1.dice1 === 6 && dice.throw1.dice2 === 6 && 
             dice.throw2.dice1 === 6 && dice.throw2.dice2 === 6);
    
    // Определяем выигрышный номер
    const sum = dice.throw1.dice1 + dice.throw1.dice2 + dice.throw2.dice1 + dice.throw2.dice2;
    const winningNumber = ((sum - 4) % 37) + 1;
    
    // Проверяем выигрыш
    let totalWin = 0;
    
    betNumbers.forEach(num => {
        if (num === winningNumber) {
            const coefficient = COEFFICIENTS[1];
            totalWin += bets[num] * coefficient;
        }
    });
    
    const newBalance = currentBalance + totalWin;
    currentBalance = newBalance;
    
    return {
        success: true,
        dice,
        winning_number: winningNumber,
        total_win: totalWin,
        new_balance: newBalance
    };
}

function randInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function startDiceAnimation() {
    ['dice1-1', 'dice2-1', 'dice1-2', 'dice2-2'].forEach(id => {
        const dice = document.getElementById(id);
        dice.classList.add('rolling');
        dice.querySelector('.dice-face').textContent = '?';
    });
    
    document.getElementById('result-number').textContent = '?';
}

function showResult(data) {
    const { dice, winning_number, total_win, new_balance } = data;
    
    // Останавливаем кубики
    const diceValues = {
        'dice1-1': dice.throw1.dice1,
        'dice2-1': dice.throw1.dice2,
        'dice1-2': dice.throw2.dice1,
        'dice2-2': dice.throw2.dice2
    };
    
    Object.entries(diceValues).forEach(([id, value]) => {
        const diceEl = document.getElementById(id);
        diceEl.classList.remove('rolling');
        diceEl.querySelector('.dice-face').textContent = getDiceFace(value);
    });
    
    // Показываем выигрышный номер
    document.getElementById('result-number').textContent = winning_number;
    
    // Подсвечиваем выигрышную ячейку
    document.querySelectorAll('.number-cell').forEach(cell => {
        cell.classList.remove('winner');
        if (parseInt(cell.dataset.number) === winning_number) {
            cell.classList.add('winner');
        }
    });
    
    // Показываем выигрыш
    if (total_win > 0) {
        document.getElementById('win-info').classList.add('show');
        document.getElementById('win-amount').textContent = `+${formatMoney(total_win)}`;
        showNotification(`🎉 Выигрыш: ${formatMoney(total_win)}!`, 'success');
        vibrate('success');
    } else {
        showNotification('Не повезло! Попробуйте ещё 🍀', 'warning');
        vibrate('error');
    }
    
    // Обновляем баланс
    updateBalanceDisplay();
    
    // Очищаем ставки
    bets = {};
    updateBetsDisplay();
    
    // Разблокируем
    isSpinning = false;
    document.getElementById('btn-spin').disabled = false;
    
    // Убираем выделение через 3 секунды
    setTimeout(() => {
        document.querySelectorAll('.number-cell').forEach(cell => {
            cell.classList.remove('selected');
            const chip = cell.querySelector('.chip-on-cell');
            if (chip) chip.remove();
        });
        document.querySelectorAll('.special-bet').forEach(b => b.classList.remove('selected'));
    }, 3000);
}

function getDiceFace(value) {
    const faces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];
    return faces[value - 1] || value;
}

// ===== УВЕДОМЛЕНИЯ =====
function showNotification(message, type = 'info') {
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('hide');
        setTimeout(() => notification.remove(), 300);
    }, 2500);
}

// ===== ВИБРАЦИЯ =====
function vibrate(type) {
    if (tg?.HapticFeedback) {
        switch (type) {
            case 'light':
                tg.HapticFeedback.impactOccurred('light');
                break;
            case 'medium':
                tg.HapticFeedback.impactOccurred('medium');
                break;
            case 'success':
                tg.HapticFeedback.notificationOccurred('success');
                break;
            case 'error':
                tg.HapticFeedback.notificationOccurred('error');
                break;
            case 'warning':
                tg.HapticFeedback.notificationOccurred('warning');
                break;
        }
    }
}


console.log('🎰 Express 37 Loaded!');
