from flask import Flask, request, Response
from flask_admin import Admin
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from flask_login import LoginManager
from configparser import ConfigParser
import os
from novaposhta import NovaPoshtaApi
config = ConfigParser()
config.read('config.ini')


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = '99ehisip'

engine = create_engine('sqlite:///viber_bot0.db', connect_args={'check_same_thread': False}, convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
connection = engine.raw_connection()
Base = declarative_base()
Base.query = session.query_property()


# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///viber_bot.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = '99ehisip'
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# NovaPoshtaApi
client = NovaPoshtaApi(api_key=config['database']['nova_poshta'])

admin = Admin(app, template_mode='bootstrap3')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'manager_login'
login_manager.needs_refresh_message_category = 'denger'

# viberbot token
token = config['database']['main_token']

bot_configuration = BotConfiguration(
    name='FullCup',
    avatar='https://i.ibb.co/wN5pM0B/photo-2021-01-18-20-00-23.jpg',
    auth_token=token
    )

viber = Api(bot_configuration)
viber.set_webhook('')


from bot.dialog import route    # noqa: E402
from bot.admin import route     # noqa: E402
