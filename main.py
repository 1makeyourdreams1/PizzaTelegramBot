import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
import json
from time import sleep
import database

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
PAY_TOKEN = os.getenv("TOKEN_PAYMENTS")

bot = telebot.TeleBot(TOKEN)

data = """
{
  "menu": [
    {
      "name": "Маргарита",
      "ingredients": ["томатный соус", "моцарелла", "свежий базилик"],
      "price": 300
    },
    {
      "name": "Пепперони",
      "ingredients": ["томатный соус", "моцарелла", "пепперони колбаса"],
      "price": 350
    },
    {
      "name": "Гавайская",
      "ingredients": ["томатный соус", "моцарелла", "ветчина", "ананасы"],
      "price": 380
    },
    {
      "name": "Вегетарианская",
      "ingredients": ["томатный соус", "моцарелла", "свежие овощи (помидоры, перцы, грибы, оливки)"],
      "price": 320
    },
    {
      "name": "BBQ Цыпленок",
      "ingredients": ["BBQ соус", "моцарелла", "кусочки цыпленка", "красный лук"],
      "price": 370
    },
    {
      "name": "Мексиканская",
      "ingredients": ["томатный соус", "моцарелла", "фасоль", "кукуруза", "острый перец", "соус сальса"],
      "price": 360
    },
    {
      "name": "Четыре Сыра",
      "ingredients": ["белый соус", "моцарелла", "пармезан", "горгонзола", "фета"],
      "price": 390
    },
    {
      "name": "Мясная",
      "ingredients": ["томатный соус", "моцарелла", "ветчина", "пепперони", "салями", "бекон"],
      "price": 400
    },
    {
      "name": "Маринара",
      "ingredients": ["томатный соус", "чеснок", "оливковое масло", "свежий базилик"],
      "price": 330
    },
    {
      "name": "Морепродукты",
      "ingredients": ["томатный соус", "моцарелла", "креветки", "мидии", "кальмары", "осьминоги"],
      "price": 420
    }
  ]
}

"""
menu = json.loads(data)
db = database.Database()


def generate_menu():
    global menu
    text = "_Вот наше меню:_\n"
    for i in range(1, len(menu["menu"]) + 1):
        text += str(i) + "  ***" + menu["menu"][i - 1]["name"] + "*** - " + \
                str(menu["menu"][i - 1]["price"]) + " руб." \
                + "\n" \
                + "*Ингредиенты*: " + \
                menu["menu"][i - 1]["ingredients"][0]
        for item in menu["menu"][i - 1]["ingredients"][1::]:
            text += ", " + item
        text += "\n\n"
    text += "Чтобы добавить пиццу в корзину, нажмите на одну из кнопок ниже👇"
    return text


def generate_keyboard():
    markup = InlineKeyboardMarkup(row_width=5)
    buttons = []
    for i in range(1, 11):
        button = InlineKeyboardButton(str(i), callback_data=str(i))
        buttons.append(button)
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("Перейти в корзину", callback_data="basket"),
               InlineKeyboardButton("Вернуться назад", callback_data="back"))
    return markup


def add_to_basket(user_id, num):
    basket = db.get_basket(user_id)
    if not (num in basket):
        basket[num] = 1
    else:
        basket[num] += 1
    db.set_basket(user_id, str(basket))


def generate_basket(user_id):
    text = ""
    count = 1
    total_price = 0
    basket = db.get_basket(user_id)
    for key, value in basket.items():
        text += str(count) + "  " + menu['menu'][key]['name'] + ' - ' + str(value) + " шт. " + '_' + \
                str(menu['menu'][key]['price'] * value) + ' руб._\n'
        total_price += menu['menu'][key]['price'] * value
        count += 1
    text += '\n\nК оплате: _' + str(total_price) + " руб._"
    return text


def generate_receipt(user_id):
    text = "Заказ:\n"
    count = 1
    basket = db.get_basket(user_id)
    for key, value in basket.items():
        text += str(count) + "  " + menu['menu'][key]['name'] + ' - ' + str(value) + " шт. " + '_' + \
                str(menu['menu'][key]['price'] * value) + ' руб._\n'
        count += 1
    text += "\nУспешно оплачен! Наш курьер с вами свяжется!"
    return text



def review_handler(message):
    bot.delete_message(message.chat.id, db.get_last_message(message.chat.id))
    db.add_review(message.chat.id, message.text)
    bot.delete_message(message.chat.id, db.get_last_message(message.chat.id) + 1)
    last_message = bot.send_message(message.chat.id, "Ваш отзыв был отправлен").message_id
    sleep(2)
    bot.delete_message(message.chat.id, last_message)
    db.set_last_message(message.chat.id, 0)
    start_message_handler(message)


@bot.message_handler(commands=['start'])
def start_message_handler(message):
    if not db.user_exists(message.chat.id):
        db.add_user(message.chat.id)
        db.set_last_message(message.chat.id, 0)
        db.set_basket(message.chat.id, str({}))
    markup = InlineKeyboardMarkup()
    button1 = InlineKeyboardButton('Сделать заказ', callback_data='order')
    button2 = InlineKeyboardButton('Оставить отзыв', callback_data='review')
    button3 = InlineKeyboardButton('Перейти к корзине', callback_data='basket')
    markup.add(button1, button2, button3)
    last_message = db.get_last_message(message.chat.id)
    if last_message != 0:
        bot.delete_message(message.chat.id, last_message)
    last_message = bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}. Добро пожаловать "
                                                     f"в Super Pizza – место,"
                                                     f" где вкус"
                                                     f" встречает удовольствие! 🍕🎉\n"
                                                     f"Приветствуем тебя в нашем уютном уголке настоящей "
                                                     f"итальянской кухни, где каждый"
                                                     f" кусочек пиццы – это настоящее произведение искусства. "
                                                     f"Мы гордимся свежими "
                                                     f"ингредиентами высочайшего качества, тщательно подобранными "
                                                     f"для создания неповторимого вкуса."
                                                     f"Мы стремимся не только угодить твоему вкусу, но и создать "
                                                     f"неповторимый опыт. Расслабься, наслаждайся атмосферой и готовься"
                                                     f" к настоящему "
                                                     f"путешествию в мир ароматов и вкусов.",
                                    reply_markup=markup).message_id
    db.set_last_message(message.chat.id, last_message)


@bot.callback_query_handler(func=lambda callback: True)
def callback_handler(callback):
    if callback.data == 'order':
        bot.delete_message(callback.message.chat.id, db.get_last_message(callback.message.chat.id))
        last_message = bot.send_message(callback.message.chat.id, generate_menu(),
                                        parse_mode="Markdown", reply_markup=generate_keyboard()).message_id
        db.set_last_message(callback.message.chat.id, last_message)
    if callback.data == 'review':
        bot.delete_message(callback.message.chat.id, db.get_last_message(callback.message.chat.id))
        mesg = bot.send_message(callback.message.chat.id, 'Напишите свой отзыв')
        db.set_last_message(callback.message.chat.id, mesg.message_id)
        bot.register_next_step_handler(mesg, review_handler)
    if callback.data in "12345678910":
        add_to_basket(callback.message.chat.id, int(callback.data) - 1)
        bot.answer_callback_query(callback_query_id=callback.id, text='Добавлено')
    if callback.data == 'basket':
        if len(db.get_basket(callback.message.chat.id)) == 0:
            bot.answer_callback_query(callback_query_id=callback.id, text='Корзина пуста')
        else:
            markup = InlineKeyboardMarkup()
            button1 = InlineKeyboardButton('Оплатить заказ', callback_data='payments')
            button2 = InlineKeyboardButton('Меню', callback_data='order')
            button3 = InlineKeyboardButton('Очистить корзину', callback_data='clear')
            markup.add(button1, button2, button3)
            bot.delete_message(callback.message.chat.id, db.get_last_message(callback.message.chat.id))
            last_message = bot.send_message(callback.message.chat.id, generate_basket(callback.message.chat.id),
                                            parse_mode="Markdown", reply_markup=markup).message_id
            db.set_last_message(callback.message.chat.id, last_message)
    if callback.data == 'back':
        start_message_handler(callback.message)
    if callback.data == 'clear':
        db.set_basket(callback.message.chat.id, str({}))
        bot.answer_callback_query(callback_query_id=callback.id, text='Корзина очищена')
        start_message_handler(callback.message)
    if callback.data == 'payments':
        basket = db.get_basket(callback.message.chat.id)
        price = []
        for key, value in basket.items():
            price.append(LabeledPrice(
                menu['menu'][key]['name'] + " " + str(value) + " шт.",
                menu['menu'][key]['price'] * value * 100))
        markup = InlineKeyboardMarkup()
        button1 = InlineKeyboardButton('Оплатить', pay=True)
        button2 = InlineKeyboardButton('Назад', callback_data='basket')
        markup.add(button1, button2)
        bot.delete_message(callback.message.chat.id, db.get_last_message(callback.message.chat.id))
        last_message = bot.send_invoice(callback.message.chat.id, title='Оплата заказа',
                                        description='Чтобы начать оплату нажмите на кнопку ниже',
                                        provider_token=PAY_TOKEN,
                                        currency='rub',
                                        need_shipping_address=True,
                                        need_name=True,
                                        need_phone_number=True,
                                        prices=price,
                                        start_parameter='time-machine-example',
                                        invoice_payload='HAPPY FRIDAYS COUPON',
                                        reply_markup=markup).message_id
        db.set_last_message(callback.message.chat.id, last_message)


@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
def process_successful_payment(message):
    bot.delete_message(message.chat.id, db.get_last_message(message.chat.id))
    generate_basket(message.chat.id)
    bot.send_message(message.chat.id, generate_receipt(message.chat.id), parse_mode="Markdown").message_id
    sleep(3)
    db.set_last_message(message.chat.id, 0)
    start_message_handler(message)


@bot.message_handler()
def message_handler(message):
    bot.send_message(message.chat.id, 'Я всего лишь бот и не умею поддерживать '
                                      'беседу, для общения со мной используйте кнопки')


bot.polling(none_stop=True, allowed_updates=[])
