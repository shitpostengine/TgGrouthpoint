import psycopg2
import telebot
from telebot import types
from config import host, user, password, db_name, token, admin
bot = telebot.TeleBot(token)
answers = []
question_number = 0
file = open('packages\grouth_point.png', 'rb')


try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    with connection.cursor() as cursor:
        def get_questions():
            cursor.execute("SELECT type_questions FROM faq_var")
            questions = cursor.fetchall()  # Получаем все вопросы из базы данных
            return [question[0] for question in questions]
        questions = get_questions()

except Exception as _ex:
    print('[INFO] Error while working with Postgresql', _ex)
finally:
    if connection:
        connection.close()
        print('[INFO] PostgreSQL connection closed')

@bot.message_handler(commands = ['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text='Продолжить', callback_data='start')
    markup.add(btn)
    bot.send_photo(message.chat.id, file, 'Привет, {0.first_name}! Это бот Точки роста ❤️!'.format(message.from_user), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'start')
def main_menu(call):
    message = call.message
    markup = types.InlineKeyboardMarkup()
    btn_url = types.InlineKeyboardButton("Сайт Точки роста", url='https://tchkrosta.ru/')
    btn_faq = types.InlineKeyboardButton('Ответы на часто задаваемые вопросы', callback_data='faq_all')
    markup.add(btn_url, btn_faq)
    bot.send_message(message.chat.id, 'Здесь вы можете получить ответы которые вас интересуют или перейти на наш сайт!💚 А если не получилось найти подходящий вам ответ - можно связаться с оператором!📞'.format(message.from_user), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'faq_all')
def faq_all_btn(call):
    question_id = 0
    markup = types.InlineKeyboardMarkup()
    message = call.message
    chat_id = message.chat.id
    for question in questions:
        question_id += 1
        btn = types.InlineKeyboardButton(text=question + '❔', callback_data='answer_' + str(question_id))# Присваиваем каждой кнопке уникальный callback_data
        markup.add(btn)
    btn_start = types.InlineKeyboardButton(text='На главную 🏠', callback_data='start')
    markup.add(btn_start)
    bot.send_message(chat_id, 'Какой тип вопросов вам подходит? 👀', reply_markup=markup)

# @bot.callback_query_handler(func=lambda call: call.data == 'start')
# def go_to_start(call):
#     start(call.message)
#     print (call.message)

@bot.callback_query_handler(func=lambda call: 'answer_' in call.data)
def faq_theme_questions_btn(call):
    global question_number
    question_id = 0
    markup = types.InlineKeyboardMarkup()
    message = call.message
    question_number = call.data[-1]
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    with connection.cursor() as cursor:
        def get_questions1():
            cursor.execute(f"SELECT questions FROM faq_ans WHERE type_id1 = '{question_number}';")
            questions2 = cursor.fetchall()  # Получаем все вопросы из базы данных
            return [question[0] for question in questions2]

        questions1 = get_questions1()
    connection.close()
    print('[INFO] PostgreSQL connection closed  (2.0)')


    for question1 in questions1:
        question_id += 1
        print(question1)
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT row_number FROM (SELECT row_number() OVER() AS row_number, questions FROM faq_ans) AS numbered_rows WHERE questions = '{question1}';")
            answer_number = cursor.fetchall()  # Получаем все ответы из базы данных
            answer_number_str = str(answer_number[0][0])
            connection.close()
            print('[INFO] PostgreSQL connection closed  (2.1)')
        btn = types.InlineKeyboardButton(text=question1 + '⭐️', callback_data='answer1_' + answer_number_str)  # Присваиваем каждой кнопке уникальный callback_data
        markup.add(btn)
    chat_id = message.chat.id
    btn = types.InlineKeyboardButton(text='Назад ↩️', callback_data='faq_all')
    markup.add(btn)
    bot.send_message(chat_id, f'Какой вопрос вам подходит? ❓', reply_markup=markup)
    print(call.data)

@bot.callback_query_handler(func=lambda call: 'answer1_' in call.data)
def faq_answers(call):
    question_number1 = call.data[-1]
    markup = types.InlineKeyboardMarkup()
    print(call.data, type(question_number1))
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT answers FROM (SELECT row_number() OVER() AS row_number, answers FROM faq_ans) AS numbered_rows WHERE row_number = {question_number1};")
        answer = cursor.fetchall()  # Получаем все ответы из базы данных
        connection.close()
        print('[INFO] PostgreSQL connection closed  (2.2)')
    message = call.message
    chat_id = message.chat.id
    btn = types.InlineKeyboardButton(text='Назад ↩️', callback_data='answer_1')
    markup.add(btn)
    bot.send_message(chat_id, answer, reply_markup=markup)

bot.polling(none_stop = True)
