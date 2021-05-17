import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from data.db_session import SqlAlchemyBase


class Thank(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'thanks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True)
    coordinates = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    n_accession = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=1)
    modifed_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f'<Thanks> {self.id} {self.name} {self.n_accession}'