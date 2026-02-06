import logging
from aiogram import Client, filters
from telegram.ext import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import json

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Данные о шифрах
CIPHERS_DATA = {
    "caesar": {
        "name": "Шифр Цезаря",
        "description": "Один из самых древних и простых шифров. Каждая буква в тексте заменяется буквой, находящейся на некотором постоянном числе позиций дальше в алфавите.",
        "example": "При сдвиге 3: A → D, B → E, C → F",
        "encryption": "C = (P + K) mod 26, где P - позиция исходной буквы, K - ключ",
        "decryption": "P = (C - K) mod 26",
        "key_type": "Число от 1 до 25",
        "history": "Использовался Юлием Цезарем для секретной переписки."
    },
    "vigenere": {
        "name": "Шифр Виженера",
        "description": "Полиалфавитный шифр подстановки, использующий ключевое слово для шифрования.",
        "example": "Ключ 'KEY': HELLO → RIJVS",
        "encryption": "C_i = (P_i + K_i) mod 26",
        "decryption": "P_i = (C_i - K_i) mod 26",
        "key_type": "Слово или фраза",
        "history": "Изобретен в 16 веке, долгое время считался невзламываемым."
    },
    "atbash": {
        "name": "Шифр Атбаш",
        "description": "Моноалфавитный шифр подстановки, где первая буква алфавита заменяется на последнюю, вторая - на предпоследнюю и т.д.",
        "example": "A → Z, B → Y, C → X",
        "encryption": "Алфавит переворачивается",
        "decryption": "Аналогично шифрованию",
        "key_type": "Без ключа",
        "history": "Использовался в древнееврейском языке."
    },
    "morse": {
        "name": "Азбука Морзе",
        "description": "Способ кодирования букв, цифр и знаков препинания с помощью коротких (точка) и длинных (тире) сигналов.",
        "example": "SOS → ... --- ...",
        "encryption": "Сопоставление символов с кодами Морзе",
        "decryption": "Обратное сопоставление",
        "key_type": "Без ключа",
        "history": "Разработана в 1838 году Сэмюэлем Морзе."
    },
    "playfair": {
        "name": "Шифр Плейфера",
        "description": "Шифр биграмм, использующий матрицу 5x5 с буквами алфавита.",
        "example": "Слово 'HELLO' разбивается на пары: HE LX LO",
        "encryption": "Специальные правила для пар букв в матрице",
        "decryption": "Обратные правила",
        "key_type": "Ключевое слово для построения матрицы",
        "history": "Изобретен в 1854 году Чарльзом Уитстоном."
    },
    "rail_fence": {
        "name": "Шифр железной дороги (Rail Fence)",
        "description": "Транспозиционный шифр, где текст записывается зигзагообразно по нескольким 'рельсам'.",
        "example": "Текст 'HELLO' с 3 рельсами: H O\n E L\n L",
        "encryption": "Запись зигзагом, чтение по строкам",
        "decryption": "Обратный процесс",
        "key_type": "Количество рельс (обычно 2-10)",
        "history": "Простой транспозиционный шифр."
    }
}

# Клавиатура с шифрами
def get_ciphers_keyboard():
    keyboard = [
        [InlineKeyboardButton("Цезаря", callback_data='caesar')],
        [InlineKeyboardButton("Виженера", callback_data='vigenere')],
        [InlineKeyboardButton("Атбаш", callback_data='atbash')],
        [InlineKeyboardButton("Морзе", callback_data='morse')],
        [InlineKeyboardButton("Плейфера", callback_data='playfair')],
        [InlineKeyboardButton("Железной дороги", callback_data='rail_fence')],
        [InlineKeyboardButton("Все шифры", callback_data='all')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Команда /start
@Client.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user
    welcome_text = f"👋 Привет, {user.first_name}!\n\n"
    welcome_text += "Я - бот-энциклопедия по шифрам! 📚\n"
    welcome_text += "Выбери шифр, о котором хочешь узнать:"
    
    await client.send_message(message.chat.id, welcome_text, reply_markup=get_ciphers_keyboard())

# Обработка выбора шифра    
@Client.on_callback_query()
async def cipher_callback(client, callback_query):
    query = callback_query
    await query.answer()
    
    cipher_id = query.data
    
    if cipher_id == 'all':
        await show_all_ciphers(query)
    else:
        await show_cipher_info(query, cipher_id)

# Показать информацию о конкретном шифре
async def show_cipher_info(query, cipher_id):
    cipher = CIPHERS_DATA[cipher_id]
    
    text = f"🔐 <b>{cipher['name']}</b>\n\n"
    text += f"📝 <b>Описание:</b> {cipher['description']}\n\n"
    text += f"📖 <b>История:</b> {cipher['history']}\n\n"
    text += f"🔑 <b>Тип ключа:</b> {cipher['key_type']}\n\n"
    text += f"🔢 <b>Шифрование:</b> {cipher['encryption']}\n"
    text += f"🔢 <b>Дешифрование:</b> {cipher['decryption']}\n\n"
    text += f"📌 <b>Пример:</b> {cipher['example']}\n\n"
    
    # Кнопки для примеров шифрования/дешифрования
    example_keyboard = [
        [InlineKeyboardButton("🔙 Назад к списку", callback_data='back')],
        [InlineKeyboardButton(f"📋 Пример шифрования {cipher['name']}",
                              callback_data=f'encrypt_{cipher_id}')],
        [InlineKeyboardButton(f"📋 Пример дешифрования {cipher['name']}",
                              callback_data=f'decrypt_{cipher_id}')]
    ]
    
    await query.edit_message_text(
        text=text,
        parse_mode='html',
        reply_markup=InlineKeyboardMarkup(example_keyboard)
    )

# Показать все шифры
async def show_all_ciphers(query):
    text = "📚 <b>Все доступные шифры:</b>\n\n"
    
    for cipher_id, cipher in CIPHERS_DATA.items():
        text += f"🔐 <b>{cipher['name']}</b>\n"
        text += f"   {cipher['description'][:100]}...\n\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back')]]
    await query.edit_message_text(
        text=text,
        parse_mode='html',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработка примеров
@Client.on_callback_query()
async def example_callback(client, callback_query):
    query = callback_query
    await query.answer()
    
    data = query.data
    if data.startswith('encrypt_'):
        cipher_id = data[8:]
        await show_encryption_example(query, cipher_id)
    elif data.startswith('decrypt_'):
        cipher_id = data[8:]
        await show_decryption_example(query, cipher_id)
    elif data == 'back':
        await query.edit_message_text(
            text="Выбери шифр, о котором хочешь узнать:",
            reply_markup=get_ciphers_keyboard()
        )

# Показать пример шифрования
async def show_encryption_example(query, cipher_id):
    cipher = CIPHERS_DATA[cipher_id]
    
    examples = {
        'caesar': """
<b>Пример шифрования Цезаря:</b>

Исходный текст: HELLO
Ключ: 3

H (7) → (7 + 3) % 26 = 10 → K
E (4) → (4 + 3) % 26 = 7 → H
L (11) → (11 + 3) % 26 = 14 → O
L (11) → (11 + 3) % 26 = 14 → O
O (14) → (14 + 3) % 26 = 17 → R

Результат: KHOOR
        """,
        'vigenere': """
<b>Пример шифрования Виженера:</b>

Исходный текст: ATTACKATDAWN
Ключ: LEMON

Ключ повторяется: LEMONLEMONLE
A + L → 0 + 11 = 11 → L
T + E → 19 + 4 = 23 → X
T + M → 19 + 12 = 31 → 5 → F
A + O → 0 + 14 = 14 → O
C + N → 2 + 13 = 15 → P
...

Результат: LXFOPVEFRNHR
        """,
        'atbash': """
<b>Пример шифрования Атбаш:</b>

Алфавит: ABCDEFGHIJKLMNOPQRSTUVWXYZ
Обратный: ZYXWVUTSRQPONMLKJIHGFEDCBA

HELLO → SVOOL
WORLD → DLIOW
        """,
        'morse': """
<b>Пример кодирования Морзе:</b>

SOS → ... --- ...
HELLO → .... . .-.. .-.. ---
EMERGENCY → . -- . .-. --. . -. -.-. -.--
        """,
        'rail_fence': """
<b>Пример шифрования Rail Fence (3 рельсы):</b>

Текст: WE ARE DISCOVERED FLEE AT ONCE
Запись зигзагом:
W   E   C   R   L   T   E
 E R D S O E E F E A O C
  A   I   V   D   E   N

Чтение по строкам: WECRLTEERDSOEEFEAOCAIVDEN
        """
    }
    
    text = examples.get(cipher_id, "Пример пока недоступен для этого шифра")
    
    keyboard = [
        [InlineKeyboardButton("🔙 Назад к шифру", callback_data=cipher_id)],
        [InlineKeyboardButton("🔙 К списку шифров", callback_data='back')]
    ]
    
    await query.edit_message_text(
        text=text,
        parse_mode='html',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Показать пример дешифрования
async def show_decryption_example(query, cipher_id):
    cipher = CIPHERS_DATA[cipher_id]
    
    examples = {
        'caesar': """
<b>Пример дешифрования Цезаря:</b>

Зашифрованный текст: KHOOR
Ключ: 3

K (10) → (10 - 3) % 26 = 7 → H
H (7) → (7 - 3) % 26 = 4 → E
O (14) → (14 - 3) % 26 = 11 → L
O (14) → (14 - 3) % 26 = 11 → L
R (17) → (17 - 3) % 26 = 14 → O

Результат: HELLO
        """,
        'vigenere': """
<b>Пример дешифрования Виженера:</b>

Зашифрованный текст: LXFOPVEFRNHR
Ключ: LEMON

Ключ повторяется: LEMONLEMONLE
L - L → 11 - 11 = 0 → A
X - E → 23 - 4 = 19 → T
F - M → 5 - 12 = -7 → 19 → T
O - O → 14 - 14 = 0 → A
P - N → 15 - 13 = 2 → C
...

Результат: ATTACKATDAWN
        """
    }
    
    text = examples.get(cipher_id, "Пример дешифрования пока недоступен для этого шифра")
    
    keyboard = [
        [InlineKeyboardButton("🔙 Назад к шифру", callback_data=cipher_id)],
        [InlineKeyboardButton("🔙 К списку шифров", callback_data='back')]
    ]
    
    await query.edit_message_text(
        text=text,
        parse_mode='html',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Команда /help
@Client.on_message(filters.command("help"))
async def help_command(client, message):
    help_text = """
<b>Доступные команды:</b>

/start - Начать работу с ботом
/help - Показать это сообщение
/ciphers - Показать список всех шифров
/about - О боте

<b>Как использовать:</b>
1. Нажмите /start
2. Выберите интересующий шифр из списка
3. Читайте подробную информацию
4. Смотрите примеры шифрования/дешифрования
    """
    await client.send_message(message.chat.id, help_text, parse_mode='html')

# Команда /ciphers
@Client.on_message(filters.command("ciphers"))
async def ciphers_command(client, message):
    await client.send_message(
        message.chat.id,
        "Выбери шифр, о котором хочешь узнать:",
        reply_markup=get_ciphers_keyboard()
    )

# Команда /about
@Client.on_message(filters.command("about"))
async def about_command(client, message):
    about_text = """
🤖 <b>Бот-энциклопедия по шифрам</b>

📚 Этот бот содержит информацию о различных классических шифрах:
- Исторические сведения
- Принципы работы
- Примеры шифрования/дешифрования
- Математические формулы

🔐 Доступные шифры:
• Шифр Цезаря
• Шифр Виженера
• Шифр Атбаш
• Азбука Морзе
• Шифр Плейфера
• Шифр железной дороги

👨‍💻 Разработано для изучения основ криптографии
    """
    await client.send_message(message.chat.id, about_text, parse_mode='html')

# Основная функция
def main():
    # API ID и Hash (полученные на my.telegram.org/apps)
    api_id = "8236462976"
    api_hash = "AAFrxY5AnvrZNDHIVrKB_Ek8eSwDBgzvOdE"
    
    # Имя сессии (можно выбрать любое уникальное название)
    session_name = "encyclopedy_bot"
    
    # Создаем клиент Pyrogram
    app = Client(session_name, api_id=api_id, api_hash=api_hash)
    
    # Запускаем клиента
    with app:
        logger.info("Бот запущен!")
        
        # Регистрация обработчиков
        @app.on_message(filters.command("start"))
        async def start_handler(client, message):
            await start(client, message)
            
        @app.on_message(filters.command("help"))
        async def help_handler(client, message):
            await help_command(client, message)
            
        @app.on_message(filters.command("ciphers"))
        async def ciphers_handler(client, message):
            await ciphers_command(client, message)
            
        @app.on_message(filters.command("about"))
        async def about_handler(client, message):
            await about_command(client, message)
            
        @app.on_callback_query()
        async def callback_handler(client, callback_query):
            await cipher_callback(client, callback_query)
        
        # Начинаем прослушивать события
        app.run()

if __name__ == '__main__':
    main()