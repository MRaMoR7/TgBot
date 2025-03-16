import telebot
import sqlite3

from telebot import types

botTimeWeb = telebot.TeleBot('Token')


db_path = "database.db"


tasks = []
current_task_index = 0


def create_table():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS math_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_image BLOB NOT NULL,
            answer_text TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()
        print("Таблица создана или уже существует.")
    except sqlite3.Error as e:
        print(f"Ошибка при создании таблицы: {e}")


def insert_task(image_path, answer_text):
    try:
        with open(image_path, 'rb') as file:
            image_blob = file.read()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO math_tasks (task_image, answer_text)
        VALUES (?, ?)
        ''', (image_blob, answer_text))

        conn.commit()
        conn.close()
        print("Задача успешно добавлена.")
    except Exception as e:
        print(f"Ошибка при вставке задачи: {e}")


create_table()


#image_path = "задачи_егэ_1/scale_12209.png"
#answer_text = "36"
#insert_task(image_path, answer_text)


def get_tasks_by_id_range(start_id, end_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, task_image, answer_text FROM math_tasks WHERE id BETWEEN ? AND ?", (start_id, end_id))
    tasks = cursor.fetchall()

    conn.close()
    return tasks


@botTimeWeb.message_handler(commands=['start'])
def startBot(message):
    first_mess = f"{message.from_user.first_name} {message.from_user.last_name}, Привет! Ты готов начать заниматься?"
    markup = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    markup.add(button_yes)
    botTimeWeb.send_message(message.chat.id, first_mess, parse_mode='html', reply_markup=markup)


@botTimeWeb.callback_query_handler(func=lambda call: call.data == 'yes')
def response(call):
    if call.message:
        second_mess = "Какой номер ты хочешь решить из первой части?"
        markup = types.InlineKeyboardMarkup()

        buttons = [
            types.InlineKeyboardButton(text=str(i), callback_data=f'range_{i}') for i in range(1, 13)
        ]
        markup.add(*buttons)

        botTimeWeb.send_message(call.message.chat.id, second_mess, reply_markup=markup)
        botTimeWeb.answer_callback_query(call.id)


@botTimeWeb.callback_query_handler(func=lambda call: call.data.startswith('range_'))
def handle_task_range(call):
    global current_task_index, tasks
    current_task_index = 0

    range_id = int(call.data.split('_')[1])
    if range_id == 1:
        tasks = get_tasks_by_id_range(1, 10)
    elif range_id == 2:
        tasks = get_tasks_by_id_range(11, 20)
    elif range_id == 3:
        tasks = get_tasks_by_id_range(21, 30)
    elif range_id == 4:
        tasks = get_tasks_by_id_range(31, 40)
    elif range_id == 5:
        tasks = get_tasks_by_id_range(41, 50)
    elif range_id == 6:
        tasks = get_tasks_by_id_range(51, 60)
    elif range_id == 7:
        tasks = get_tasks_by_id_range(61, 70)
    elif range_id == 8:
        tasks = get_tasks_by_id_range(71, 80)
    elif range_id == 9:
        tasks = get_tasks_by_id_range(81, 90)
    elif range_id == 10:
        tasks = get_tasks_by_id_range(91, 100)
    elif range_id == 11:
        tasks = get_tasks_by_id_range(101, 110)
    elif range_id == 12:
        tasks = get_tasks_by_id_range(111, 120)


    send_task(call.message.chat.id)


def send_task(chat_id):
    global current_task_index, tasks
    if current_task_index < len(tasks):
        task_id, task_image_blob, answer_text = tasks[current_task_index]


        with open(f'task_{task_id}.png', 'wb') as file:
            file.write(task_image_blob)


        with open(f'task_{task_id}.png', 'rb') as file:
            botTimeWeb.send_photo(chat_id, file, caption=f"Задача {task_id}")

        botTimeWeb.send_message(chat_id, "Напишите ваш ответ:")
        botTimeWeb.register_next_step_handler_by_chat_id(chat_id, check_answer, answer_text)
    else:
        botTimeWeb.send_message(chat_id, "Это были все задачи.")


def check_answer(message, correct_answer):
    user_answer = message.text.strip()
    chat_id = message.chat.id

    if user_answer == correct_answer:
        botTimeWeb.send_message(chat_id, "Верно! 🎉")
    else:
        botTimeWeb.send_message(chat_id, f"Неверно. Правильный ответ: {correct_answer}")


    markup = types.InlineKeyboardMarkup()
    button_next = types.InlineKeyboardButton(text='Следующая задача', callback_data='next_task')
    button_choose = types.InlineKeyboardButton(text='Выбрать другую задачу', callback_data='choose_task')
    markup.add(button_next, button_choose)
    botTimeWeb.send_message(chat_id, "Выберите действие:", reply_markup=markup)


@botTimeWeb.callback_query_handler(func=lambda call: call.data == 'next_task')
def handle_next_task(call):
    global current_task_index
    current_task_index += 1
    send_task(call.message.chat.id)


@botTimeWeb.callback_query_handler(func=lambda call: call.data == 'choose_task')
def response(call):
    if call.message:
        second_mess = "Какой номер ты хочешь решить из первой части?"
        markup = types.InlineKeyboardMarkup()

        buttons = [
            types.InlineKeyboardButton(text=str(i), callback_data=f'range_{i}') for i in range(1, 13)
        ]
        markup.add(*buttons)

        botTimeWeb.send_message(call.message.chat.id, second_mess, reply_markup=markup)
        botTimeWeb.answer_callback_query(call.id)


botTimeWeb.infinity_polling()