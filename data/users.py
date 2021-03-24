import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    # back_populates должно указывать не на таблицу, а на атрибут класса orm.relation
    news = orm.relation("News", back_populates='user')

    # устанавливает значение хэша пароля для переданной строки.
    # для регистрации пользователя
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    # правильный ли пароль ввел пользователь
    # авторизация пользователей
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)