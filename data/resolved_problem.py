import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Resolved(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'resolved_problems'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True)
    rating = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    problem = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    users = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modifed_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f'<Resolved_problem> {self.id} {self.name} {self.problem} {self.modifed_date}'