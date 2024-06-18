import telebot
from telebot import types
import sqlite3
import random

API_TOKEN = ''
bot = telebot.TeleBot(API_TOKEN)

list = []
list2 = []
list4 = []
con = sqlite3.connect("terms.db", check_same_thread=False)
cursor = con.cursor()


@bot.message_handler(commands=['start'])
def start(message):
    database(con)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔎Учить термины")
    btn2 = types.KeyboardButton("➕Добавить термины")
    btn3 = types.KeyboardButton("❌Удалить термины")
    btn4 = types.KeyboardButton("📕Вывести все термины")

    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id,
                     text="Привет, {0.first_name}! Я бот для изучения терминов".format(
                         message.from_user), reply_markup=markup)


@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, text= f"Данный бот предназнчен для изучения любых образовательных терминов \n"
                                            f"Кнопка '🔎Учить термины' предназначена для проверки знаний добавленных "
                                            f"\терминов, а также просмотра интересующего вас термина\n"
                                            f"Кнопка '➕Добавить термины' предназначена для добавления нового термина, "
                                            f"который можно будет в дальнейшем учить\n"
                                            f"Кнопка '❌Удалить термины' предназначена для удаления уже не нужного "
                                            f"термина, или всех имеющихся\n"
                                            f"Кнопка '📕Вывести все термины' предназначена для повторения всех "
                                            f"добавленных терминов")


@bot.message_handler(content_types=['text'])
def func(message):
    if (message.text == "🔎Учить термины"):
        markup1 = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton("В случайном порядке", callback_data="random")
        btn2 = types.InlineKeyboardButton("Конкретный термин", callback_data="search")
        markup1.add(btn1, btn2)
        bot.send_message(message.chat.id,
                         text="Как ты хочешь учить?".format(
                             message.from_user), reply_markup=markup1)

    elif (message.text == "❌Удалить термины"):
        markup2 = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton("Все термины", callback_data="deleteall")
        btn2 = types.InlineKeyboardButton("По названию термина", callback_data="delete")
        markup2.add(btn1, btn2)
        bot.send_message(message.chat.id,
                         text="Что конкретно ты хочешь удалить?".format(
                             message.from_user), reply_markup=markup2)

    elif (message.text == "➕Добавить термины"):
        bot.send_message(message.chat.id, "Введите название термина")
        bot.register_next_step_handler(message, terminname)

    elif (message.text == "📕Вывести все термины"):
        cursor.execute("SELECT * FROM term")
        terminlist = cursor.fetchall()
        value = len(terminlist)
        if value == 0:
            bot.send_message(message.chat.id, text="У вас ещё нет ни одного термина")
        else:
            bot.send_message(message.chat.id, text="Ваши термины:")
            for str in terminlist:
                bot.send_message(message.chat.id, text=(f"{str[1]} — {str[2]}"))

    elif (message.text == "⬅Назад"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🔎Учить термины")
        btn2 = types.KeyboardButton("➕Добавить термины")
        btn3 = types.KeyboardButton("❌Удалить термины")
        btn4 = types.KeyboardButton("📕Вывести все термины")
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, text="Вы вернулись в главное меню".format(
            message.from_user), reply_markup=markup)

    elif (message.text == "Учить cледующий термин➡"):
        bot.send_message(message.chat.id, "Идём дальше")
        randomlearn(message)


def terminname(message):
    list.append(message.text)
    bot.send_message(message.chat.id, "Введите текст термина")
    bot.register_next_step_handler(message, termintext)


def termintext(message):
    list.append(message.text)
    cursor.execute("INSERT INTO term (termin, termintext) VALUES (?, ?)", (str(list[0]), str(list[1])))
    list.clear()
    con.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("➕Добавить термины")
    button2 = types.KeyboardButton("⬅Назад")
    markup.add(button1, button2)
    bot.send_message(message.chat.id, "✔Термин добавлен", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'deleteall':
        cursor.execute("DROP TABLE term")
        database(con)
        con.commit()
        bot.send_message(call.message.chat.id, "✔Все термины успешно удалены")

    if call.data == 'delete':
        bot.send_message(call.message.chat.id, "Введите название термина")
        bot.register_next_step_handler(call.message, deletename)

    if call.data == 'random':
        randomlearn(call.message)

    if call.data == 'search':
        bot.send_message(call.message.chat.id, "Введите название термина")
        bot.register_next_step_handler(call.message, searchname)


def deletename(message):
    termname = message.text
    cursor.execute("DELETE FROM term WHERE termin = ?", (termname,))
    con.commit()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("По названию термина")
    button2 = types.KeyboardButton("⬅Назад")
    markup.add(button1, button2)
    bot.send_message(message.chat.id, "✔Данный термин удалён", reply_markup=markup)


def searchname(message):
    numberstr = message.text
    cursor.execute("SELECT * FROM term WHERE termin = ?", (numberstr,))
    terminlist = cursor.fetchall()
    value = len(terminlist)
    if value == 0:
        bot.send_message(message.chat.id, text="У вас ещё нет такого термина")
    else:
        for str in terminlist:
            bot.send_message(message.chat.id, text=(f"{str[1]} — {str[2]}"))


def randomlearn(message):
    cursor.execute("SELECT COUNT(*) FROM term")
    list4.append(cursor.fetchone()[0])
    list4.append(random.randint(1, list4[0] + 1))
    cursor.execute("SELECT termintext FROM term WHERE id = ?", (list4[1],))
    list4.append(cursor.fetchall())
    bot.send_message(message.chat.id, text=(list4[2]))
    bot.send_message(message.chat.id, "Введите название данного термина для проверки")
    bot.register_next_step_handler(message, checkrandom)


def checkrandom(message):
    cursor.execute("SELECT termin FROM term WHERE id = ?", (list4[1],))
    message1 = cursor.fetchone()[0]
    if message.text == message1:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Учить cледующий термин➡")
        btn2 = types.KeyboardButton("⬅Назад")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, "✔Всё правильно!", reply_markup=markup)
        list4.clear()
    else:
        bot.send_message(message.chat.id, "❌Неправильно, попробуй ещё раз")
        bot.register_next_step_handler(message, checkrandom)


def database(con):
    cursor.execute("""CREATE TABLE IF NOT EXISTS term
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    termin TEXT,
                    termintext TEXT)""")
    con.commit()


bot.polling(none_stop=True)
