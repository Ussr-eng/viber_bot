from bot import engine, Base
from sqlalchemy import create_engine, Float, Column, Integer, String, Boolean, ForeignKey, update, \
    Unicode, or_, and_, DateTime, literal, JSON, Text, DECIMAL, BIGINT, Table, Sequence, Date, cast, func
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from datetime import datetime, timedelta
from sqlalchemy.sql import case
from datetime import datetime
from flask_admin.contrib.sqla import ModelView
from bot import admin


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)
    phone = Column(String(100), nullable=True)
    name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)

    messages = relationship('ChatMessage', order_by="desc(ChatMessage.date_created)",
                            backref=backref('owner', lazy=True))
    prom = relationship('Prom', order_by="desc(Prom.date_created)",
                        backref=backref('owner', lazy=True))

    def __repr__(self):
        return 'Владелец сообщения %r' % self.name


class MyUser(ModelView):
    # __ hide user id in flask admin __
    column_exclude_list = ['user_id']
    column_display_pk = True
    can_edit = False
    can_delete = False
    can_create = False
    page_size = 10


class ChatMessage(Base):

    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(String(100), nullable=True)
    image = Column(String(150), nullable=True, default='image.jpg')
    from_admin = Column(Boolean, unique=False, default=True)
    date_created = Column(DateTime(30), default=datetime.now, nullable=False)

    def __repr__(self):
        return '<ChatMessage %r>' % self.id


class Prom(Base):

    __tablename__ = "prom"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="prom")

    status = Column(String(100), default=None)
    order_id = Column(String(400), nullable=True)
    declaration_number = Column(String(150), nullable=True)
    date_created = Column(DateTime(30), default=datetime.now, nullable=False)


# admin.add_view(MyUser(User, Base.session, name='Пользователи'))
# admin.add_view(ModelView(ChatMessage, Base.session, name='Сообщения'))

Base.metadata.create_all(bind=engine)

