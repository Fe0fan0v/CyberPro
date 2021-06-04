from flask import redirect, render_template, Flask, request, jsonify
from data.register import RegisterForm
from data.login_form import LoginForm
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.complaints import Complaint
from constants import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ryasov_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают.")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже существует")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', title='Авторизация', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def index():
    db_session.global_init("db/users_my_site.db")
    db_sess = db_session.create_session()
    list_problems = []
    for i in db_sess.query(Complaint).all():
        if i.n_confirmation >= 5:
            flag = True
        else:
            flag = False
        diction = {}
        diction['id'] = i.id
        diction['name'] = i.name
        diction['lat'] = i.coordinates.split(',')[0]
        diction['lon'] = i.coordinates.split(',')[1]
        diction['date'] = transformation_date(str(i.modifed_date))
        diction['category'] = i.category
        diction['ver'] = flag
        diction['color'] = DICT_COLORS_PROBLEMS[i.category]
        diction['label'] = DICT_COLORS_LABELS[i.category]
        list_problems.append(diction)
    return render_template('geolocation.html', title='Главная', list_problems=list_problems)


@app.route('/c', methods=["GET"])
def co():
    db_sess = db_session.create_session()
    list_problems = []
    for i in db_sess.query(Complaint).all():
        if i.n_confirmation >= 5:
            flag = True
        else:
            flag = False
        diction = {}
        diction['id'] = i.id
        diction['name'] = i.name
        diction['text'] = i.description
        diction['lat'] = i.coordinates.split(',')[0]
        diction['lon'] = i.coordinates.split(',')[1]
        diction['date'] = i.modifed_date
        diction['category'] = i.category
        diction['ver'] = flag
        diction['color'] = DICT_COLORS_PROBLEMS[i.category]
        diction['label'] = DICT_COLORS_LABELS[i.category]
        list_problems.append(diction)
    print(request.remote_addr)
    return render_template('problems.html', list_problems=list_problems)


if __name__ == '__main__':
    db_session.global_init("db/users_my_site.db")
    app.run('localhost', 8000)
