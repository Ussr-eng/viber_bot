from flask import Flask, Response, request, jsonify, make_response, url_for
import requests
import json
from bot import session, app, viber, token
from .models import User, ChatMessage, Prom
from bot.prom.prom_request import check, get_declaration
from bot.novaposhta.novaposhta_request import poshta_request
import secrets, os
import json
import uuid
import datetime
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages import VideoMessage, ContactMessage, KeyboardMessage, PictureMessage, RichMediaMessage, \
    FileMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
from threading import Timer
import time
import logging
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_token = token
hook = 'https://chatapi.viber.com/pa/send_message'
headers = {'X-Viber-Auth-Token': auth_token}


@app.route('/', methods=['GET', 'POST'])
def incoming():

    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    viber_request = viber.parse_request(request.get_data())

    KEYBOARD_START = {
        "Type": "keyboard",
        "Buttons": [{
            "Columns": 6,
            "Rows": 1,
            "Text": "<font color=\"#494E67\">Статус заказа</font>",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "bottom",
            "ActionType": "reply",
            "ActionBody": "Статус заказа",
            "BgColor": "#fef8eb",
            "Image": "https://i.postimg.cc/VsDKccQ6/back.jpg"

        }, {
            "Columns": 6,
            "Rows": 1,
            "Text": "<font color=\"#494E67\">Частые вопросы</font>",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "bottom",
            "ActionType": "reply",
            "ActionBody": "Частые вопросы",
            "BgColor": "#fef8eb",
            "Image": "https://i.postimg.cc/VsDKccQ6/back.jpg"
        }, {
            "Columns": 6,
            "Rows": 1,
            "Text": "<font color=\"#494E67\">Свяжитесь со мной</font>",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "bottom",
            "ActionType": "reply",
            "ActionBody": "Свяжитесь со мной",
            "BgColor": "#fef8eb",
            "Image": "https://i.postimg.cc/VsDKccQ6/back.jpg"
        }]
    }

    KEYBOARD_QUESTIONS = {
        "Type": "keyboard",
        "Buttons": [{
            "Columns": 6,
            "Rows": 1,
            "Text": "<font color=\"#494E67\">Возврат/обмен</font>",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "bottom",
            "ActionType": "reply",
            "ActionBody": "Возврат/обмен",
            "BgColor": "#fef8eb",
            "Image": "https://i.postimg.cc/VsDKccQ6/back.jpg"

        }, {
            "Columns": 6,
            "Rows": 1,
            "Text": "<font color=\"#494E67\">Способы доставки</font>",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "bottom",
            "ActionType": "reply",
            "ActionBody": "Способы доставки",
            "BgColor": "#fef8eb",
            "Image": "https://i.postimg.cc/VsDKccQ6/back.jpg"
        }, {
            "Columns": 6,
            "Rows": 1,
            "Text": "<font color=\"#494E67\">Способы оплаты</font>",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "bottom",
            "ActionType": "reply",
            "ActionBody": "Способы оплаты",
            "BgColor": "#fef8eb",
            "Image": "https://i.postimg.cc/VsDKccQ6/back.jpg"
        }, {
            "Columns": 6,
            "Rows": 1,
            "Text": "<font color=\"#494E67\">Главное меню</font><br>",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "bottom",
            "ActionType": "reply",
            "ActionBody": "Назад",
            "BgColor": "#fef8eb",
            "Image": "https://i.postimg.cc/VsDKccQ6/back.jpg"
        }]
    }

    KEYBOARD_BACK = {
        "Type": "keyboard",
        "Buttons": [{
            "Columns": 6,
            "Rows": 1,
            "Text": "<font color=\"#494E67\">Главное меню</font><br>",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "bottom",
            "ActionType": "reply",
            "ActionBody": "Назад",
            "BgColor": "#fef8eb",
            "Image": "https://i.postimg.cc/VsDKccQ6/back.jpg"
        }]
    }


    logging.basicConfig(filename="logfile.log", level=logging.INFO)
    logging.debug("This is debug message")

    if isinstance(viber_request, ViberConversationStartedRequest):

        viber.send_messages(viber_request.user.id, [
            TextMessage(text="Напишите 👉 ваш номер телефона 📱"
                             "\nна который был оформлен заказ"
                             "\nв нашем магазине🛍️"
                             "\nПример записи: 063*******\n"
                             "\nЕсли же вы не делали заказ"
                             "\nпросто напишите 👉 Нет заказа"),
        ])

    if isinstance(viber_request, ViberMessageRequest):

        # message_user = viber_request.message.text
        # message_media = viber_request.message.media
        message = viber_request.message
        print(viber_request.sender.id)
        print(message)
        print(message.text)
        print(type(message))

        if viber_request.message.text:

            message_user = viber_request.message.text

            if len(message_user) == 10 and message_user.isdecimal() \
                    or message_user == 'Назад' or message_user == 'Нет заказа':
                # user_data = viber.get_user_details(viber_request.sender.id)

                user_id = viber_request.sender.id
                user_name = viber_request.sender.name
                user_message = message_user
                sender = User.query.filter_by(user_id=user_id).first()

                if sender:

                    keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_START)
                    message = TextMessage(text='Выберете интересующую вас опцию')
                    viber.send_messages(viber_request.sender.id, [
                        message,
                        keyboard
                    ])
                    print(viber_request.sender.id)

                elif message_user == 'Нет заказа':

                    user = User(user_id=user_id,
                                name=user_name)

                    keyboard = KeyboardMessage(tracking_data='tracking_data',
                                               keyboard=KEYBOARD_START)

                    message = TextMessage(text='Выберете интересующую вас опцию')
                    viber.send_messages(user_id, [
                        message,
                        keyboard
                    ])

                    session.add(user)
                    session.commit()

                else:

                    user = User(user_id=user_id,
                                name=user_name,
                                phone=user_message)
                    print('!' + user.phone)
                    keyboard = KeyboardMessage(tracking_data='tracking_data',
                                               keyboard=KEYBOARD_START)

                    message = TextMessage(text='Выберете интересующую вас опцию')
                    viber.send_messages(user_id, [
                        message,
                        keyboard
                    ])

                    session.add(user)
                    session.commit()

                    check(id=user_id, board=KEYBOARD_START)

            elif message_user == "Свяжитесь со мной":

                keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)
                message = TextMessage(text='Будем рады вам помочь🔥\nЗадайте Ваш вопрос👇')
                viber.send_messages(viber_request.sender.id, [
                    message,
                    keyboard
                ])
            elif message_user == "Скрин оплаты":

                keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)
                message = TextMessage(text='Отправьте скрин оплаты\nи ожидайте подтверждения менеджера🙂')
                viber.send_messages(viber_request.sender.id, [
                    message,
                    keyboard
                ])

            elif message_user == "Время оплаты":

                keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)
                message = TextMessage(text='Отправьте время оплаты👇🙂')
                viber.send_messages(viber_request.sender.id, [
                    message,
                    keyboard
                ])

            elif message_user == "Частые вопросы":

                keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_QUESTIONS)
                message = TextMessage(text='Выберете тему👇')
                viber.send_messages(viber_request.sender.id, [
                    message,
                    keyboard
                ])

            elif message_user == "Возврат/обмен":

                keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)
                message = TextMessage(text='Компания осуществляет возврат и обмен товаров надлежащего качества согласно'
                                           'Закона «О защите прав потребителей»\n'
                                           'Возврат и обмен товаров возможен в течение 14 дней после получения'
                                           'товара покупателем, обратная доставка товаров осуществляется по'
                                           'договоренности. Пожалуйста, обратите внимание, обмену или возврату подлежит'
                                           'только тот товар который не был в эксплуатации и не имеет следов '
                                           'использования!')
                viber.send_messages(viber_request.sender.id, [
                    message,
                    keyboard
                ])

            elif message_user == "Способы доставки":

                keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)
                message = TextMessage(text='-Новая почта (Бесплатно при стоимости заказа от 2 000 грн'
                                           '\n-Новая почта (Адресная)'
                                           '\n-Justin (По полной предоплате)'
                                           '\n-Укрпочта (По полной предоплате)'
                                           '\n-Самовывоз Новая почта'
                                           '\n-Самовывоз Харьков (при встрече)')
                viber.send_messages(viber_request.sender.id, [
                    message,
                    keyboard
                ])

            elif message_user == "Способы оплаты":

                keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)
                message = TextMessage(text='-Кредиты от КредитМаркет'
                                           '\n-Безналичный расчет'
                                           '\n-Оплата при получении "Новая почта", данный способ оплаты действует'
                                           'только при доставке Новой почтой'
                                           '\n-Наложенный платеж "Новая почта", данный способ оплаты действует'
                                           'только при доставке Новой почтой'
                                           '\n-Онлайн оплата Visa/Mastercard '
                                           '\n Приват: 5168755905269185(Мокрушин Кирилл)'
                                           '\n МоноБанк: 5375414123101718(Мокрушин Кирилл)')
                viber.send_messages(viber_request.sender.id, [
                    message,
                    keyboard
                ])

            elif message_user == "Статус заказа":

                user = session.query(User).filter_by(user_id=viber_request.sender.id).first()
                print(user.phone)

                if user.phone:

                    order = session.query(Prom).filter_by(owner=user).first()
                    print(order.order_id)
                    if order.order_id:

                        if order.declaration_number:

                            poshta_request(id=viber_request.sender.id,
                                           declaration_number=order.declaration_number,
                                           board=KEYBOARD_BACK)

                        else:

                            get_declaration(order_id=order.order_id,
                                            board=KEYBOARD_BACK,
                                            user_id=viber_request.sender.id)

                    else:

                        keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)

                        message = TextMessage(text='На данный номер телефона нет оформленных заказов')
                        viber.send_messages(viber_request.sender.id, [
                            message,
                            keyboard
                        ])

                else:

                    keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)

                    message = TextMessage(text='Вы не ввели номер телефона')
                    viber.send_messages(viber_request.sender.id, [
                        message,
                        keyboard
                    ])

            else:

                user_id = viber_request.sender.id
                user_name = viber_request.sender.name
                user_message = message_user
                sender = User.query.filter_by(user_id=user_id).first()

                if sender:

                    message = ChatMessage(message=user_message,
                                          owner=sender,
                                          from_admin=False)

                    keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)
                    viber.send_messages(viber_request.sender.id, [
                        keyboard
                    ])

                    session.add(message)
                    session.commit()
                    print('add message')

                else:
                    message = TextMessage(text='⚠️Введенный вами текст не соответствует номеру телефона'
                                               '\nномер должен иметь следующий вид:'
                                               '\n063*******'
                                               '\n098*******'
                                               '\n067*******\n'
                                               '\nЕсли же вы не делали заказ'
                                               '\nпросто напишите 👉 Нет заказа')
                    viber.send_messages(viber_request.sender.id, [
                        message

                    ])

        elif viber_request.message.media:

            user_id = viber_request.sender.id
            sender = User.query.filter_by(user_id=user_id).first()

            if sender:

                respons = requests.get(viber_request.message.media)
                generate_name = str(uuid.uuid4())
                create_name = 'bot/static/images/' + generate_name + '.png'
                image_file = open(create_name, 'wb')
                image_file.write(respons.content)
                image_file.close()

                message = ChatMessage(owner=sender,
                                      image=generate_name,
                                      from_admin=False)

                session.add(message)
                session.commit()
                print('add media')

            else:

                message = TextMessage(text='⚠️Введенный вами текст не соответствует номеру телефона'
                                           '\nномер должен иметь следующий вид:'
                                           '\n063*******'
                                           '\n098*******'
                                           '\n067*******\n'
                                           '\nЕсли же вы не делали заказ'
                                           '\nпросто напишите 👉 Нет заказа')
                viber.send_messages(viber_request.sender.id, [
                    message

                ])

    return Response(status=200)


