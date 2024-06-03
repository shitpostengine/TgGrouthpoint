import psycopg2
import telebot
from telebot import types     #для указание типов
from config import host, user, password, db_name, token
bot = telebot.TeleBot(token)
answers = []

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
    btn_url = types.InlineKeyboardButton("Сайт Точки роста", url='https://tchkrosta.ru/')
    btn_faq = types.InlineKeyboardButton('Ответы на часто задаваемые вопросы', callback_data='faq_all')
    markup.add(btn_url, btn_faq)
    #print(message)
    bot.send_message(message.chat.id, 'Привет, {0.first_name}! Это бот Точки роста. Что вы хотите узнать? '.format(message.from_user), reply_markup=markup)
    #bot.send_message(message.chat.id, answer)

@bot.callback_query_handler(func=lambda call: call.data == 'faq_all')
def faq_all_btn(call):
    question_id = 0
    markup = types.InlineKeyboardMarkup()
    message = call.message
    chat_id = message.chat.id
    for question in questions:
        question_id += 1
        btn = types.InlineKeyboardButton(text=question, callback_data='answer_' + str(question_id))# Присваиваем каждой кнопке уникальный callback_data
        markup.add(btn)
    bot.send_message(chat_id, f'Какой тип вопросов вам подходит?', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: 'answer_' in call.data)
def faq_theme_questions_btn(call):
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

    # except Exception as _ex:
    #     print('[INFO] Error while working with Postgresql  (2.0)', _ex)
    # finally:
    #     if connection:
    #         connection.close()
    #         print('[INFO] PostgreSQL connection closed  (2.0)')
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    with connection.cursor() as cursor:
        global answers
        cursor.execute(f"SELECT answers FROM faq_ans WHERE type_id1 = '{question_number}';")
        answers = cursor.fetchall()  # Получаем все ответы из базы данных
        connection.close()
    print('[INFO] PostgreSQL connection closed  (2.1)')
    for question1 in questions1:
        question_id += 1
        btn = types.InlineKeyboardButton(text=question1, callback_data='answer1_' + str(question_id))  # Присваиваем каждой кнопке уникальный callback_data
        markup.add(btn)
    chat_id = message.chat.id
    bot.send_message(chat_id, f'Какой вопрос вам подходит?', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: 'answer1_' in call.data)
def faq_answers(call):
    message = call.message
    chat_id = message.chat.id
    question_number = int(call.data[-1])-1
    correct_answer = answers[question_number-1]
    bot.send_message(chat_id, correct_answer)#, reply_markup=markup)

bot.polling(none_stop = True)
