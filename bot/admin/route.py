from flask import Flask, Response, request, jsonify, make_response, render_template, url_for, flash, session, redirect
from flask_login import login_required, current_user, logout_user, login_user
from bot import session
from bot import app, viber, admin
from bot.dialog.models import User, ChatMessage
from .forms import Chat, ManagerLoginForm
from .models import Manager
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
import pprint

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


@app.route('/data', methods=['GET', 'POST'])
# @login_required
def data():
    # print(current_user.name)
    time = datetime.now() - timedelta(hours=24)
    all_users = User.query.join(ChatMessage, User.id == ChatMessage.user_id).filter(ChatMessage.date_created > time)\
        .all()

    return render_template('chat/index.html', all_users=all_users)


@app.route('/data/<int:id>', methods=['GET', 'POST'])
# @login_required
def chat(id):
    form = Chat()
    time = datetime.now() - timedelta(hours=24)
    all_users = User.query.join(ChatMessage, User.id == ChatMessage.user_id).filter(ChatMessage.date_created > time)\
        .all()
    print(all_users)

    users = session.query(User).filter_by(id=id).first()
    messages = ChatMessage.query.filter_by(owner=users).all()

    if request.method == 'POST':

        form_message = form.message.data

        message = ChatMessage(owner=users, message=form_message)

        session.add(message)
        session.commit()
        print('сообщение добавлено')
        viber_message = TextMessage(text=form_message)

        viber.send_messages(users.user_id, [viber_message])

        return redirect(request.url)

    return render_template('chat/single_page.html', all_users=all_users, users=users, messages=messages, form=form)


@app.route('/data/copy-paste1/<int:id>', methods=['GET', 'POST'])
# @login_required
def private_fop(id):
    form = Chat()
    time = datetime.now() - timedelta(hours=24)
    all_users = User.query.join(ChatMessage, User.id == ChatMessage.user_id).filter(ChatMessage.date_created > time) \
        .all()
    users = session.query(User).filter_by(id=id).first()
    messages = ChatMessage.query.filter_by(owner=users).all()
    requisites = 'Приват ФОП: 4246001001336563 Мокрушин Кирилл.'
    form.message.data = requisites

    if request.method == 'POST':

        message = ChatMessage(owner=users, message=form.message.data)

        session.add(message)
        session.commit()

        viber_message = TextMessage(text=form.message.data)

        viber.send_messages(users.user_id, [viber_message])

        return redirect(url_for('chat', id=id))

    return render_template('chat/single_page.html', all_users=all_users, users=users, messages=messages, form=form)


@app.route('/data/copy-paste2/<int:id>', methods=['GET', 'POST'])
# @login_required
def mono_bank(id):
    form = Chat()
    time = datetime.now() - timedelta(hours=24)
    all_users = User.query.join(ChatMessage, User.id == ChatMessage.user_id).filter(ChatMessage.date_created > time) \
        .filter(ChatMessage.from_admin == False).all()
    users = session.query(User).filter_by(id=id).first()
    messages = ChatMessage.query.filter_by(owner=users).all()
    requisites = 'МоноБанк: 5375414123101718 Мокрушин Кирилл.'
    form.message.data = requisites

    if request.method == 'POST':

        message = ChatMessage(owner=users, message=form.message.data)

        session.add(message)
        session.commit()

        viber_message = TextMessage(text=form.message.data)

        viber.send_messages(users.user_id, [viber_message])

        return redirect(url_for('chat', id=id))

    return render_template('chat/single_page.html', all_users=all_users, users=users, messages=messages, form=form)


@app.route('/data/copy-paste3/<int:id>', methods=['GET', 'POST'])
# @login_required
def privat(id):
    form = Chat()
    time = datetime.now() - timedelta(hours=24)
    all_users = User.query.join(ChatMessage, User.id == ChatMessage.user_id).filter(ChatMessage.date_created > time) \
        .filter(ChatMessage.from_admin == False).all()
    users = session.query(User).filter_by(id=id).first()
    messages = ChatMessage.query.filter_by(owner=users).all()
    requisites = 'Приват: 5168755905269185 Мокрушин Кирилл.'
    form.message.data = requisites

    if request.method == 'POST':

        message = ChatMessage(owner=users, message=form.message.data)

        session.add(message)
        session.commit()

        viber_message = TextMessage(text=form.message.data)

        viber.send_messages(users.user_id, [viber_message])

        return redirect(url_for('chat', id=id))

    return render_template('chat/single_page.html', all_users=all_users, users=users, messages=messages, form=form)


@app.route('/sendmessage', methods=['GET', 'POST'])
def sendmessage():

    message = TextMessage(text='Ответ от админа, все работает!')
    id = '1gwYmkDPCCv0MqiBwy+t2A=='
    viber.send_messages(id, [message])
