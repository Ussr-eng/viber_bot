from flask import Flask, Response, request, jsonify, make_response
from bot import session
from bot import app, viber
from .models import User, ChatMessage
import pprint

import json
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
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_token = '4c9c7acc1e400fbe-266ea034c860abc6-b50342de6358d929'
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
            "Columns": 3,
            "Rows": 2,
            "Text": "<font color=\"#494E67\">Консультация менеджера</font><br>",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "bottom",
            "ActionType": "reply",
            "ActionBody": "Свяжитесь со мной",
            "BgColor": "#fef8eb",
            "Image": "https://i.postimg.cc/VsDKccQ6/back.jpg"

        }, {
            "Columns": 3,
            "Rows": 2,
            "Text": "<font color=\"#494E67\">Статус заказа</font><br><br>",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "bottom",
            "ActionType": "reply",
            "ActionBody": "Статус заказа",
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
            TextMessage(text="Напишите 👉 Начать \nЧтобы начать диалог с ботом🔥")])

    if isinstance(viber_request, ViberMessageRequest):
        message_user = str(viber_request.message.text)
        print(message_user)

        if message_user == 'Начать' or message_user == 'начать' or message_user == 'Назад':

            keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_START)
            message = TextMessage(text='Выберете интересующую вас опцию')
            viber.send_messages(viber_request.sender.id, [
                message,
                keyboard
            ])

        elif message_user == "Свяжитесь со мной":

            keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)
            message = TextMessage(text='Будем рады вам помочь🔥\nЗадайте Ваш вопрос👇')
            viber.send_messages(viber_request.sender.id, [
                message,
                keyboard
            ])

        elif message_user == "Статус заказа":

            keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)
            message = TextMessage(text='🚧Данная функция на этапе разработки🚧\n'
                                       'воспользуйтесь существующим функционалом🙏')
            viber.send_messages(viber_request.sender.id, [
                message,
                keyboard
            ])

        else:

            keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)
            viber.send_messages(viber_request.sender.id, [
                keyboard
            ])

            user_id = viber_request.sender.id
            user_name = viber_request.sender.name
            user_message = message_user
            sender = User.query.filter_by(user_id=user_id).first()

            if sender:
                message = ChatMessage(message=user_message,
                                  owner=sender,
                                  from_admin=False)

                session.add(message)
                session.commit()
                print('add message')

            else:
                user = User(user_id=user_id,
                            name=user_name)
                message = ChatMessage(message=user_message,
                                  owner=user,
                                  from_admin=False)

                session.add(user)
                session.add(message)
                session.commit()
                print('add user and message')

    return Response(status=200)
