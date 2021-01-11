from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerField, TextAreaField,\
    DecimalField, RadioField
from flask_wtf import FlaskForm


class Chat(FlaskForm):
    message = StringField('Ваше сообщение:')
    select = RadioField('Реквизиты', choices=[('Приват ФОП: 4246001001336563 Мокрушин Кирилл. \n'
                                               'МоноБанк: 5375414123101718 Мокрушин Кирилл. \n'
                                               'Приват: 5168755905269185 Мокрушин Кирилл.', 'Все реквизиты'),
                                              ('Приват ФОП: 4246001001336563 Мокрушин Кирилл.', 'Приват ФОП'),
                                              ('МоноБанк: 5375414123101718 Мокрушин Кирилл.', 'МоноБанк'),
                                              ('Приват: 5168755905269185 Мокрушин Кирилл.', 'Приват Банк')])


class ManagerLoginForm(FlaskForm):
    login = StringField('Логин:', [validators.DataRequired()])
    password = StringField('Пароль:', [validators.DataRequired()])
