import psycopg2
import telebot
from telebot import types     #для указание типов
from config import host, user, password, db_name, token
bot = telebot.TeleBot(token)

answer = [] #переменная для ответов из бд

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
        #def get_questions2():
        #answer = cursor.fetchall()
        #print(cursor.fetchall())
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
def faq_theme_btn(call):
    question_number = call.data[-1]
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT questions FROM faq_ans WHERE type_id1 = '{question_number}';")
        questions2 = cursor.fetchall()
        print(questions2)
bot.polling(none_stop = True)
