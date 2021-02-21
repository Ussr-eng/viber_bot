from flask import Flask, Response, request, jsonify, make_response, url_for
import requests
from novaposhta import NovaPoshtaApi
from bot import session, app, viber, client
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages import VideoMessage, ContactMessage, KeyboardMessage, PictureMessage, RichMediaMessage, \
    FileMessage
from threading import Timer
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from bot.dialog.models import Prom


def poshta_request(id, declaration_number, board):

    r = client.internet_document.get_status_documents(declaration_number)
    # print(r.json()['data'][0])
    answer = None
    status_code = r.json()['data'][0]['StatusCode']
    print(status_code)

    if status_code == '1':
        answer = 'Новая почта ожидает поступления от отправителя.'
    elif status_code == '2':
        answer = 'Удалено'
    elif status_code == '4' or status_code == '5':
        answer = 'Посылка уже едет в ваш город.'
    elif status_code == '6':
        answer = 'Посылка уже у вас в городе, ожидайте дополнительное сообщение о прибытии.'
    elif status_code == '7' or status_code == '8':
        answer = 'Посылка в отделении, Вы можете ее получить.'
    elif status_code == '9' or status_code == '10' or status_code == '11':
        answer = 'Отправление получено.'
    elif status_code == '14':
        answer = 'Отправление передано получателю на осмотр.'
    elif status_code == '101':
        answer = 'На пути к получателю.'
    elif status_code == '102' or status_code == '103' or status_code == '108':
        answer = 'Отмена получателя.'
    elif status_code == '104':
        answer = 'Смена адреса.'
    elif status_code == '105':
        answer = 'Хранение остановлено.'
    elif status_code == '106':
        answer = 'Получено и есть ТТН денежный перевод.'
    elif status_code == '107':
        answer = 'Начисляется плата за хранение.'

    keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=board)
    message = TextMessage(text=answer)
    viber.send_messages(id, [
        message,
        keyboard
    ])


def mailing_np_status(declaration_number, user_id, board):

    r = client.internet_document.get_status_documents(declaration_number)
    status_code = r.json()['data'][0]['StatusCode']
    print(status_code)

    if status_code == '4' or status_code == '5' or status_code == '6' \
            or status_code == '7' or status_code == '8':

        keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=board)
        message = TextMessage(text='🥳Ваш заказ отправлен🥳\n'
                                   'Номер посылки - {}'.format(declaration_number))
        viber.send_messages(user_id, [
            message,
            keyboard
        ])

    elif status_code == '2' or status_code == '9' or status_code == '10' or status_code == '11' or status_code == '102'\
            or status_code == '103' or status_code == '108' or status_code == '106' or status_code == '105':

        pass

    else:

        schedule = Timer(10000.0, mailing_np_status, [declaration_number, user_id, board])
        schedule.start()


def mailing_np(declaration_number, user_id, board):

    r = client.internet_document.get_status_documents(declaration_number)
    status_code = r.json()['data'][0]['StatusCode']
    print(status_code)

    if status_code == '9' or status_code == '10' or status_code == '11' or status_code == '106':

        keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=board)
        message = TextMessage(text='Спасибо за покупку, напишите ваш отзыв'
                                   '👉 https://zzapravka.com.ua/testimonials')
        viber.send_messages(user_id, [
            message,
            keyboard
        ])

    elif status_code == '2' or status_code == '102' or status_code == '103' or status_code == '108'\
            or status_code == '105':

        pass

    else:

        schedule = Timer(10000.0, mailing_np, [declaration_number, user_id, board])
        schedule.start()


def colors_chat(prom_id):
    prom = session.query(Prom).filter_by(id=prom_id).first()

    if prom.declaration_number != None:
        r = client.internet_document.get_status_documents(prom.declaration_number)
        status_code = r.json()['data'][0]['StatusCode']
        print(status_code)

        if status_code == '9' or status_code == '10' or status_code == '11':
            # 'Отправление получено'
            prom.status = 'success'
            session.commit()

        elif status_code == '102' or status_code == '103' or status_code == '108':
            # 'Отмена получателя'
            prom.status = 'buyer refusal'
            session.commit()

        else:

            schedule = Timer(5000.0, colors_chat, [prom_id])
            schedule.start()

    else:

        schedule = Timer(20000.0, colors_chat, [prom_id])
        schedule.start()
