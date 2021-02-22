from flask import Flask, Response, request, jsonify, make_response, url_for
import requests
import json
from bot import session, app, viber
from bot.dialog.models import User, ChatMessage, Prom
from bot.novaposhta.novaposhta_request import poshta_request, mailing_np, mailing_np_status
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
import pprint
import json
import time
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')


def check(id, board):
    startTime = time.time()

    headers = {'Authorization': 'Bearer {}'.format(config['database']['prom'])}
    all_clients = requests.get('https://my.prom.ua/api/v1/orders/list?limit=100', headers=headers)
    # print(all_clients.json()['orders'][27])

    user = session.query(User).filter_by(user_id=id).first()

    order_id = None
    last_name = None
    declaration_number = None

    for z in range(99):
        phone = (all_clients.json()['orders'][z]['phone'])
        if phone == '+38' + user.phone:
            last_name = (all_clients.json()['orders'][z]['client_last_name'])
            order_id = (all_clients.json()['orders'][z]['id'])
            declaration_number = (all_clients.json()['orders'][z]['delivery_provider_data']['declaration_number'])
            break

    if order_id != None:

        prom = Prom(owner=user,
                    order_id=order_id)

        session.add(prom)
        session.commit()
        print('id заказа добавлен')

        mailing_prom(order_id=order_id, user_id=id, board_start=board)

        if last_name != '':

            user.last_name = last_name
            session.commit()

        print('user last name add')

        if declaration_number != None:

            order = session.query(Prom).filter_by(order_id=order_id).first()
            order.declaration_number = declaration_number

            session.commit()
            print('declaration number add')

    elif order_id == None:

        prom = Prom(owner=user,
                    order_id=order_id)

        session.add(prom)
        session.commit()

        keyboard = KeyboardMessage(tracking_data='tracking_data',
                                   keyboard=board)
        message = TextMessage(text='По данному номеру не'
                                   '\nнайдено никаких заказов❗')
        viber.send_messages(id, [
            message,
            keyboard
        ])

    print(time.time() - startTime)


def get_declaration(order_id, board, user_id):

    startTime = time.time()

    headers = {'Authorization': 'Bearer {}'.format(config['database']['prom'])}
    client = requests.get('https://my.prom.ua/api/v1/orders/{}'.format(order_id), headers=headers)
    declaration_number = client.json()['order']['delivery_provider_data']['declaration_number']

    if declaration_number != None:

        order = session.query(Prom).filter_by(order_id=order_id).first()
        order.declaration_number = declaration_number

        session.commit()
        poshta_request(id=user_id,
                       declaration_number=order.declaration_number,
                       board=board)
    else:

        keyboard = KeyboardMessage(tracking_data='tracking_data',
                                   keyboard=board)
        message = TextMessage(text='Ваша накладная еще не готова')
        viber.send_messages(user_id, [
            message,
            keyboard
        ])

    print(time.time() - startTime)


def mailing_prom(order_id, user_id, board_start):

    headers = {'Authorization': 'Bearer {}'.format(config['database']['prom'])}
    client = requests.get('https://my.prom.ua/api/v1/orders/{}'.format(order_id), headers=headers)
    declaration_number = client.json()['order']['delivery_provider_data']['declaration_number']
    print(True)

    if declaration_number != None:

        order = session.query(Prom).filter_by(order_id=order_id).first()
        order.declaration_number = declaration_number
        session.commit()

        mailing_np(declaration_number=declaration_number, user_id=user_id, board=board_start)
        mailing_np_status(declaration_number=declaration_number, user_id=user_id, board=board_start)
        print(True)

    else:

        schedule = Timer(100400.0, mailing_prom, [order_id, user_id, board_start])
        schedule.start()
        print(False)