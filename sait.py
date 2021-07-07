from flask import redirect, render_template, Flask, request, jsonify
from data.register import RegisterForm
from data.login_form import LoginForm
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.complaints import Complaint
from constants import *
from main import write_to_file, geocode
import os
import operator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ryasov_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/site_db.db")
db_sess = db_session.create_session()


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
            id_tele=form.id_tele.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
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
        if not user:
            return render_template('login.html', title='Авторизация', message="Вы не зарегистрированы",
                                   form=form, color='yellow', left='42')
        return render_template('login.html', title='Авторизация', message="Неправильный логин или пароль",
                               color='red', form=form, left='39')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/', methods=['GET', 'POST'])
def index():
    db_session.global_init("db/site_db.db")
    user_answer = '4'
    lst_backlight = ['-outline', '-outline', '-outline', '-outline', '-outline']
    if request.method == 'POST':
        user_answer = request.form['category']
    lst_backlight[int(user_answer)] = ''
    db_sess = db_session.create_session()
    list_problems = []
    for i in db_sess.query(Complaint).all():
        if i.n_confirmation >= QUANTITY_CONFIRMATION:
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
        if user_answer == '0' and diction['category'] == 'Дорожная':
            pass
        elif user_answer == '1' and diction['category'] == 'Экологическая':
            pass
        elif user_answer == '2' and diction['category'] == 'ЖКХ':
            pass
        elif user_answer == '3' and diction['category'] == 'Другое':
            pass
        elif user_answer == '4':
            pass
        else:
            continue
        list_problems.append(diction)
    return render_template('geolocation.html', title='Главная', list_problems=list_problems, backlight=lst_backlight,
                            url=URL)


@app.route('/all_problems', methods=["GET", 'POST'])
def all_problems():
    db_sess = db_session.create_session()
    flag_date = 0
    lst_backlight = ['-outline', '-outline']
    region = 'все'
    if request.method == "POST":
        print(request.form)
        if 'region' in request.form:
            region = request.form['region'].strip()
            print([region])
        if 'options' in request.form:
            if request.form['options'] == '0':
                flag_date = 0
            else:
                flag_date = 1
        if 'prob_0' in request.form:
            user = db_sess.query(User).filter(User.email == current_user.email).first()
            problem = db_sess.query(Complaint).filter(Complaint.id == int(request.form["prob_0"])).first()
            problem.n_confirmation += 1
            if user.ver_problems:
                user.ver_problems += f'{request.form["prob_0"]},'
            else:
                user.ver_problems = f'{request.form["prob_0"]},'
            db_sess.commit()
        elif 'prob_1' in request.form:
            user = db_sess.query(User).filter(User.email == current_user.email).first()
            problem = db_sess.query(Complaint).filter(Complaint.id == int(request.form["prob_1"])).first()
            problem.n_confirmation -= 1
            lst_problems = user.ver_problems.split(',')
            lst_problems.remove(request.form['prob_1'])
            user.ver_problems = ','.join(lst_problems)
            db_sess.commit()
    if current_user.is_authenticated:
        user = db_sess.query(User).filter(User.email == current_user.email).first()
    lst_backlight[flag_date] = ''
    list_problems = []
    for i in db_sess.query(Complaint).all():
        if i.n_confirmation >= QUANTITY_CONFIRMATION:
            flag = True
        else:
            flag = False
        if f'{i.id}.jpg' not in os.listdir('static/img/img_problems'):
            write_to_file(i.photo, f'static/img/img_problems/{i.id}.jpg')
        diction = {}
        diction['id'] = i.id
        diction['name'] = i.name
        diction['text'] = i.description
        diction['lat'] = i.coordinates.split(',')[0]
        diction['lon'] = i.coordinates.split(',')[1]
        diction['datetime'] = i.modifed_date
        diction['date'] = transformation_date(str(i.modifed_date))
        diction['category'] = i.category
        diction['n_ver'] = i.n_confirmation
        diction['ver'] = flag
        diction['color'] = DICT_COLORS_PROBLEMS[i.category]
        diction['label'] = DICT_COLORS_LABELS[i.category]
        if current_user.is_authenticated:
            diction['pub'] = 0
            if user.ver_problems:
                if str(i.id) in user.ver_problems.split(','):
                    diction['pub'] = -1
            if user.my_problems:
                if str(i.id) in user.my_problems.split(','):
                    diction['pub'] = 1
        # print(geocode(f'{diction["lon"]},{diction["lat"]}')['metaDataProperty']['GeocoderMetaData']['text'])
        if region != 'все' and region in \
                geocode(f'{diction["lon"]},{diction["lat"]}')['metaDataProperty']['GeocoderMetaData']['text']:
            list_problems.append(diction)
        elif region == 'все':
            list_problems.append(diction)
    if flag_date == 0:
        list_problems.sort(key=operator.itemgetter('datetime'), reverse=True)
    else:
        list_problems.sort(key=operator.itemgetter('n_ver'), reverse=True)
    with open('static/txt/regions.txt', 'r', encoding='utf-8') as file:
        lst = file.readlines()
    return render_template(
        'problems.html', list_problems=list_problems, title='Проблемы', lst_regions=lst, backlight=lst_backlight,
        my_problems=False, url=URL)


@app.route('/my_problems', methods=['GET', 'POST'])
def my_problems():
    db_sess = db_session.create_session()
    flag_date = 0
    lst_backlight = ['-outline', '-outline']
    region = 'все'
    user = db_sess.query(User).filter(User.email == current_user.email).first()
    if request.method == "POST":
        print(request.form)
        if 'region' in request.form:
            region = request.form['region'].strip()
            print([region])
        if 'options' in request.form:
            if request.form['options'] == '0':
                flag_date = 0
            else:
                flag_date = 1
    lst_backlight[flag_date] = ''
    list_problems = []
    for i in db_sess.query(Complaint).all():
        if i.n_confirmation >= QUANTITY_CONFIRMATION:
            flag = True
        else:
            flag = False
        if f'{i.id}.jpg' not in os.listdir('static/img/img_problems'):
            write_to_file(i.photo, f'static/img/img_problems/{i.id}.jpg')
        diction = {}
        diction['id'] = i.id
        diction['name'] = i.name
        diction['text'] = i.description
        diction['lat'] = i.coordinates.split(',')[0]
        diction['lon'] = i.coordinates.split(',')[1]
        diction['datetime'] = i.modifed_date
        diction['date'] = transformation_date(str(i.modifed_date))
        diction['category'] = i.category
        diction['n_ver'] = i.n_confirmation
        diction['ver'] = flag
        diction['color'] = DICT_COLORS_PROBLEMS[i.category]
        diction['label'] = DICT_COLORS_LABELS[i.category]
        if current_user.is_authenticated:
            diction['pub'] = 0
            if user.ver_problems:
                if str(i.id) in user.ver_problems.split(','):
                    diction['pub'] = -1
            if user.my_problems:
                if str(i.id) in user.my_problems.split(','):
                    diction['pub'] = 1
        if str(i.id) in user.my_problems.split(','):
            if region != 'все' and region in \
                    geocode(f'{diction["lon"]},{diction["lat"]}')['metaDataProperty']['GeocoderMetaData']['text']:
                list_problems.append(diction)
            elif region == 'все':
                list_problems.append(diction)
    if flag_date == 0:
        list_problems.sort(key=operator.itemgetter('datetime'), reverse=True)
    else:
        list_problems.sort(key=operator.itemgetter('n_ver'), reverse=True)
    with open('static/txt/regions.txt', 'r', encoding='utf-8') as file:
        lst = file.readlines()
    return render_template(
        'problems.html', list_problems=list_problems, title='Проблемы', lst_regions=lst, backlight=lst_backlight,
        my_problems=True, url=URL)


@app.route('/problem/<int:id_problem>', methods=['GET', 'POST'])
def problem(id_problem):
    if request.method == "POST":
        if 'prob_0' in request.form:
            user = db_sess.query(User).filter(User.email == current_user.email).first()
            problem = db_sess.query(Complaint).filter(Complaint.id == int(request.form["prob_0"])).first()
            problem.n_confirmation += 1
            if user.ver_problems:
                user.ver_problems += f'{request.form["prob_0"]},'
            else:
                user.ver_problems = f'{request.form["prob_0"]},'
            db_sess.commit()
        elif 'prob_1' in request.form:
            user = db_sess.query(User).filter(User.email == current_user.email).first()
            problem = db_sess.query(Complaint).filter(Complaint.id == int(request.form["prob_1"])).first()
            problem.n_confirmation -= 1
            lst_problems = user.ver_problems.split(',')
            lst_problems.remove(request.form['prob_1'])
            user.ver_problems = ','.join(lst_problems)
            db_sess.commit()
    is_problem = db_sess.query(Complaint).filter(Complaint.id == id_problem).first()
    if is_problem.n_confirmation >= QUANTITY_CONFIRMATION:
        flag = True
    else:
        flag = False
    if f'{is_problem.id}.jpg' not in os.listdir('static/img/img_problems'):
        write_to_file(is_problem.photo, f'static/img/img_problems/{is_problem.id}.jpg')
    diction = {}
    diction['id'] = is_problem.id
    diction['name'] = is_problem.name
    diction['text'] = is_problem.description
    diction['lat'] = is_problem.coordinates.split(',')[0]
    diction['lon'] = is_problem.coordinates.split(',')[1]
    diction['datetime'] = is_problem.modifed_date
    diction['date'] = transformation_date(str(is_problem.modifed_date))
    diction['category'] = is_problem.category
    diction['n_ver'] = is_problem.n_confirmation
    diction['ver'] = flag
    diction['color'] = DICT_COLORS_PROBLEMS[is_problem.category]
    diction['label'] = DICT_COLORS_LABELS[is_problem.category]
    if current_user.is_authenticated:
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        diction['pub'] = 0
        if user.ver_problems:
            if str(is_problem.id) in user.ver_problems.split(','):
                diction['pub'] = -1
        if user.my_problems:
            if str(is_problem.id) in user.my_problems.split(','):
                diction['pub'] = 1
    return render_template(
        'problem.html', diction=diction, title=is_problem.name)


if __name__ == '__main__':
    db_session.global_init("db/site_db.db")
    app.run('localhost', URL)
