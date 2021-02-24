from flask import Flask, Response, request, jsonify, make_response, render_template, url_for, flash, session, redirect
from flask_login import login_required, current_user, logout_user, login_user
from bot import session, engine, connection, app, viber, admin, token
from bot.dialog.models import User, ChatMessage, Prom
from bot.novaposhta.novaposhta_request import colors_chat
from .forms import Chat, ManagerLoginForm
from .models import Manager
import requests
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
import pprint
from threading import Timer
import json
from datetime import datetime, timedelta
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
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')


auth_token = token
hook = 'https://chatapi.viber.com/pa/send_message'
headers = {'X-Viber-Auth-Token': auth_token}


@app.route('/data/login', methods=['GET', 'POST'])
def manager_login():
    form = ManagerLoginForm()

    if request.method == 'POST':
        manager = Manager.query.filter_by(login=form.login.data).first()

        if manager and manager.password == form.password.data:
            login_user(manager)
            flash(f'Вы вошли в систему', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('data'))
        flash(f'Неверный логин или пароль', 'danger')
        return redirect(url_for('manager_login'))
    return render_template('chat/login.html', form=form)


@app.route('/data/logout')
def manager_logout():
    logout_user()
    return redirect(url_for('manager_login'))


@app.route('/ajaxlivesearch', methods=['POST', 'GET'])
def ajaxlivesearch():
    if request.method == 'POST':
        query = request.form.get('query')
        search = "%{}%".format(query)
        print(search)
        if search != '%None%':
            search_users = User.query.filter(User.name.like(search)).all()

        else:
            search_users = User.query.all()

    return jsonify({'htmlresponse': render_template('chat/search_users.html', search_users=search_users)})


@app.route("/insert", methods=['POST', 'GET'])
def insert():
    if request.method == 'POST':
        get_id = request.form.get('query')

        if get_id == None:
            pass

        elif 'not' in get_id:
            get_id = get_id.split()
            prom = session.query(Prom).filter_by(user_id=get_id[0]).order_by(Prom.id.desc()).first()
            prom.status = 'waiting payment'
            session.commit()

        else:
            prom = session.query(Prom).filter_by(user_id=get_id).order_by(Prom.id.desc()).first()
            prom.status = 'confirm payment'
            session.commit()
            message_text(get_id, 'Оплату проверили, готовим посылку к отправке☺')
            colors_chat(prom.id)

    return jsonify(True)


@app.route('/data', methods=['GET', 'POST'])
@login_required
def data():
    # print(current_user.name)
    time = datetime.now() - timedelta(hours=24)
    all_users = User.query.join(ChatMessage, User.id == ChatMessage.user_id).all()

    return render_template('chat/index.html', all_users=all_users)


@app.route('/data/<int:id>', methods=['GET', 'POST'])
@login_required
def chat(id):
    form = Chat()
    time = datetime.now() - timedelta(hours=24)
    all_users = User.query.join(ChatMessage, User.id == ChatMessage.user_id).all()
    print(all_users)

    users = session.query(User).filter_by(id=id).first()
    prom = session.query(Prom).filter_by(user_id=id).first()
    messages = ChatMessage.query.filter_by(owner=users).all()

    if request.method == 'POST':
        form_message = form.message.data
        message = ChatMessage(owner=users, message=form_message)

        session.add(message)
        session.commit()
        print('сообщение добавлено')
        viber_message = TextMessage(text=form_message)

        viber.send_messages(users.user_id, [viber_message])
        keyboard_back(user_id=users.user_id)

        return redirect(request.url)

    return render_template('chat/single_page.html', all_users=all_users, users=users,
                           messages=messages, prom=prom, form=form)


@app.route('/data/copy-paste1/<int:id>', methods=['GET', 'POST'])
@login_required
def private_fop(id):
    form = Chat()
    time = datetime.now() - timedelta(hours=24)
    all_users = User.query.join(ChatMessage, User.id == ChatMessage.user_id).filter(ChatMessage.date_created > time) \
        .all()
    users = session.query(User).filter_by(id=id).first()
    messages = ChatMessage.query.filter_by(owner=users).all()
    prom = session.query(Prom).filter_by(user_id=id).order_by(Prom.id.desc()).first()
    requisites = 'Приват ФОП: 4246001001336563 Мокрушин Кирилл.\n' \
                 '\nЧтобы отправить скрин оплаты нажмите на кнопку выше👆\n' \
                 '\n❗Чтобы отменить заказ напишите👉"Отмена заказа"'
    form.message.data = requisites

    if request.method == 'POST':

        message = ChatMessage(owner=users, message=form.message.data)
        prom.status = 'waiting payment'
        session.add(message)
        session.commit()

        widget(id=users.user_id)
        viber_message = TextMessage(text=form.message.data)
        viber.send_messages(users.user_id, [viber_message])
        keyboard_back(user_id=users.user_id)

        schedule = Timer(172800.0, reminder, [id])
        schedule.start()

        return redirect(url_for('chat', id=id))

    return render_template('chat/single_page.html', all_users=all_users, users=users, messages=messages, form=form)


@app.route('/data/copy-paste2/<int:id>', methods=['GET', 'POST'])
@login_required
def mono_bank(id):
    form = Chat()
    time = datetime.now() - timedelta(hours=24)
    all_users = User.query.join(ChatMessage, User.id == ChatMessage.user_id).filter(ChatMessage.date_created > time) \
        .filter(ChatMessage.from_admin == False).all()
    users = session.query(User).filter_by(id=id).first()
    messages = ChatMessage.query.filter_by(owner=users).all()
    prom = session.query(Prom).filter_by(user_id=id).order_by(Prom.id.desc()).first()
    requisites = 'МоноБанк: 5375414123101718 Мокрушин Кирилл.\n' \
                 '\nЧтобы отправить скрин оплаты нажмите на кнопку выше👆\n' \
                 '\n❗Чтобы отменить заказ напишите👉"Отмена заказа"'
    form.message.data = requisites

    if request.method == 'POST':

        message = ChatMessage(owner=users, message=form.message.data)
        prom.status = 'waiting payment'
        session.add(message)
        session.commit()

        widget(id=users.user_id)
        viber_message = TextMessage(text=form.message.data)
        viber.send_messages(users.user_id, [viber_message])
        keyboard_back(user_id=users.user_id)

        schedule = Timer(172800.0, reminder, [id])
        schedule.start()

        return redirect(url_for('chat', id=id))

    return render_template('chat/single_page.html', all_users=all_users, users=users, messages=messages, form=form)


@app.route('/data/copy-paste3/<int:id>', methods=['GET', 'POST'])
@login_required
def privat(id):
    form = Chat()
    time = datetime.now() - timedelta(hours=24)
    all_users = User.query.join(ChatMessage, User.id == ChatMessage.user_id).filter(ChatMessage.date_created > time) \
        .filter(ChatMessage.from_admin == False).all()
    users = session.query(User).filter_by(id=id).first()
    messages = ChatMessage.query.filter_by(owner=users).all()
    prom = session.query(Prom).filter_by(user_id=id).order_by(Prom.id.desc()).first()
    requisites = 'Приват: 5168755905269185 Мокрушин Кирилл.\n' \
                 '\nЧтобы отправить скрин оплаты нажмите на кнопку выше👆\n' \
                 '\n❗Чтобы отменить заказ напишите👉"Отмена заказа"'
    form.message.data = requisites

    if request.method == 'POST':

        message = ChatMessage(owner=users, message=form.message.data)
        prom.status = 'waiting payment'
        session.add(message)
        session.commit()

        widget(id=users.user_id)
        viber_message = TextMessage(text=form.message.data)
        viber.send_messages(users.user_id, [viber_message])
        keyboard_back(user_id=users.user_id)

        schedule = Timer(172800.0, reminder, [id])
        schedule.start()

        return redirect(url_for('chat', id=id))

    return render_template('chat/single_page.html', all_users=all_users, users=users, messages=messages, form=form)


@app.route('/reminder', methods=['GET', 'POST'])
def reminder(id):
    # payment reminder
    user = session.query(User).filter_by(user_id=id).first()
    images = session.query(ChatMessage).filter_by(owner=user).filter(ChatMessage.image != None).first()
    print(images.image)

    if images.image != 'image.jpg':
        pass

    else:
        widget(id)
        message = TextMessage(text='Напоминаем вам об оплате🙂\n'
                                   '\nЧтобы отправить скрин оплаты нажмите на кнопку выше👆')
        viber.send_messages(id, [message])

        keyboard_back(user_id=id)


def message_text(user, message):

    user = session.query(User).filter_by(id=user).first()
    viber_message = TextMessage(text=message)
    viber.send_messages(user.user_id, [viber_message])
    keyboard_back(user_id=user.user_id)


@app.route('/widget', methods=['GET', 'POST'])
def widget(id):
    sen = {
        "receiver": id,
        "type": "rich_media",
        "min_api_version": 7,
        "rich_media": {
            "Type": "rich_media",
            "ButtonsGroupColumns": 6,
            "ButtonsGroupRows": 4,
            "BgColor": "#FFFFFF",
            "Buttons": [
                 {
                    "Columns": 6,
                    "Rows": 2,
                    "ActionType": "reply",
                    "ActionBody": "Скрин оплаты",
                    "Text": "<font color=#8367db>Прикрепить скрин оплаты</font>",
                    "TextSize": "small",
                    "TextVAlign": "middle",
                    "TextHAlign": "middle",
                    "Image": "https://i.ibb.co/QQHb9gF/photo-2021-02-21-21-31-19.jpg"
                 },
                 {
                    "Columns": 6,
                    "Rows": 2,
                    "ActionType": "reply",
                    "ActionBody": "Время оплаты",
                    "Text": "<font color=#8367db>Прикрепить время оплаты</font>",
                    "TextSize": "small",
                    "TextVAlign": "middle",
                    "TextHAlign": "middle",
                    "Image": "https://i.ibb.co/QQHb9gF/photo-2021-02-21-21-31-19.jpg"
                 }
            ]
        }
    }

    r = requests.post(hook, json.dumps(sen), headers=headers)
    print(r.json())


def keyboard_back(user_id):

    KEYBOARD_BACK = {
        "Type": "keyboard",
        "Buttons": [{
            "Columns": 6,
            "Rows": 1,
            "Text": "<font color=\"#494E67\">Действия</font><br>",
            "TextSize": "medium",
            "TextHAlign": "center",
            "TextVAlign": "bottom",
            "ActionType": "reply",
            "ActionBody": "Назад",
            "BgColor": "#fef8eb",
            "Image": "https://i.postimg.cc/VsDKccQ6/back.jpg"
        }]
    }

    keyboard = KeyboardMessage(tracking_data='tracking_data', keyboard=KEYBOARD_BACK)

    viber.send_messages(user_id, [
        keyboard

    ])