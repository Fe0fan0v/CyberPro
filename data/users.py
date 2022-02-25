import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from werkzeug.security import generate_password_hash, check_password_hash
from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    my_problems = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ver_problems = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    my_thanks = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ver_thanks = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    coordinates_map = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modifed_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f'<User> {self.id} {self.surname} {self.name}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def get_all_values(self):
        dict = {"id": self.id, 'name': self.name, 'surname': self.surname, 'email': self.email,
                'my_problems': self.my_problems, 'ver_problems': self.ver_problems,
                'my_thanks': self.my_thanks, 'ver_thanks': self.ver_thanks, 'hashed_password': self.hashed_password,
                'modified_date': self.modifed_date}
        return dict
