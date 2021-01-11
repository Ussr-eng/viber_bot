from flask_login import UserMixin
from bot import engine, Base
from bot import login_manager
from sqlalchemy import create_engine, Float, Column, Integer, String, Boolean, ForeignKey, update, \
    Unicode, or_, and_, DateTime, literal, JSON, Text, DECIMAL, BIGINT, Table, Sequence, Date, cast, func
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from datetime import datetime, timedelta
from sqlalchemy.sql import case

from datetime import datetime


@login_manager.user_loader
def load_manager(user_id):
    return Manager.query.get(user_id)


class Manager(Base, UserMixin):
    __tablename__ = "manager"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    login = Column(String(130), nullable=False, unique=True)
    password = Column(String(130), nullable=False)

    def __repr__(self):
        return 'Менеджер %r' % self.name


Base.metadata.create_all(bind=engine)
