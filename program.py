# from flask import Flask, render_template
# from flask_wtf import FlaskForm
# from wtforms import RadioField
#
# SECRET_KEY = 'development'
#
# app = Flask(__name__)
# app.config.from_object(__name__)
#
#
# class SimpleForm(FlaskForm):
#     example = RadioField('Label', choices=[('value', 'description'), ('value_two', 'whatever')])
#
#
# @app.route('/', methods=['post', 'get'])
# def hello_world():
#     form = SimpleForm()
#     if form.validate_on_submit():
#         print(form.example.data)
#     else:
#         print(form.errors)
#     return render_template('example.html', form=form)
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
from flask import redirect, render_template, Flask, request, jsonify
from data.register import RegisterForm
from data.login_form import LoginForm
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.complaints import Complaint
from constants import *
from main import write_to_file, geocode, convert_to_binary_data
import os
import operator



db_session.global_init("db/site_db.db")
db_sess = db_session.create_session()
lst_confir = []
for i in db_sess.query(Complaint).all():
    if i.id == 5:
        i.photo = convert_to_binary_data('static/img/img_problems/труб.jpg')