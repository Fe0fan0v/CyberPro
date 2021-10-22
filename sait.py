from flask import redirect, render_template, Flask, request, jsonify, make_response
from data.register import RegisterForm
from data.login_form import LoginForm
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from db_work import column_length
from data import db_session
from data.users import User
from data.complaints import Complaint
from data.thanks import Thank
from data.resolved_problem import Resolved
from constants import *
from PIL import Image
from geocoder import geocode
import operator
from db_work import add_complaint
import base64
from requests import post

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ryasov_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/site_db.db")
db_sess = db_session.create_session()


def shaping_dictionary(i, the_main=True, thank=False, resolved=False):
    diction = {}
    if not thank and not resolved:
        recording_img(i.id, i.photo, 'img_problems')
        if i.n_confirmation >= QUANTITY_CONFIRMATION:
            flag = True
        else:
            flag = False
        diction['lat'] = i.coordinates.split(',')[0]
        diction['lon'] = i.coordinates.split(',')[1]
        diction['category'] = i.category
        diction['ver'] = flag
        diction['color'] = DICT_COLORS_PROBLEMS[i.category]
    elif thank:
        recording_img(i.id, i.photo, 'thanks')
    elif resolved:
        recording_img(i.id, i.photo, 'resolved_problems')
        if i.rating:
            n_star = 0
            for j in i.rating.split(','):
                if j != '':
                    n_star += int(j)
            lst = i.users.split(',')
            while '' in lst:
                lst.remove('')
            n_star = round(n_star / (len(lst)), 0)
            diction['rating'] = int(n_star)
            if current_user.is_authenticated:
                user = db_sess.query(User).filter(User.email == current_user.email).first()
                if str(user.id) in i.users.split(','):
                    print(i.rating.split(','))
                    diction['my_rating'] = int(i.rating.split(',')[i.users.split(',').index(str(user.id))])
        else:
            diction['rating'] = None
        diction['id_problem'] = i.problem
        problem = db_sess.query(Complaint).filter(Complaint.id == i.problem).first()
        diction['category'] = problem.category
        diction['color'] = DICT_COLORS_PROBLEMS[problem.category]
    diction['id'] = i.id
    diction['name'] = i.name
    diction['date'] = transformation_date(str(i.modifed_date))
    if the_main:
        diction['datetime'] = i.modifed_date
        diction['text'] = i.description
        if not thank and not resolved:
            diction['n_ver'] = i.n_confirmation
            if current_user.is_authenticated:
                user = db_sess.query(User).filter(User.email == current_user.email).first()
                diction['pub'] = 0
                if user.ver_problems:
                    if str(i.id) in user.ver_problems.split(','):
                        diction['pub'] = -1
                if user.my_problems:
                    if str(i.id) in user.my_problems.split(','):
                        diction['pub'] = 1
            # if f'{i.id}.jpg' not in os.listdir('static/img/map_problems'):
            #     write_map(ll_spn=f"{i.coordinates.split(',')[1]},{i.coordinates.split(',')[0]}", size=f"650,450",
            #               map_file=f'static/img/map_problems/{i.id}.jpg', point=DICT_COLORS_POINT[i.category])
        elif thank:
            diction['n_ver'] = i.n_accession
            if current_user.is_authenticated:
                user = db_sess.query(User).filter(User.email == current_user.email).first()
                diction['pub'] = 0
                if user.ver_thanks:
                    if str(i.id) in user.ver_thanks.split(','):
                        diction['pub'] = -1
        elif resolved:
            if current_user.is_authenticated:
                user = db_sess.query(User).filter(User.email == current_user.email).first()
                diction['pub'] = 0
                if i.users:
                    if str(user.id) in i.users.split(','):
                        diction['pub'] = 1
    elif not thank:
        diction['label'] = DICT_COLORS_LABELS[i.category]
    return diction


def request_processing(req):
    print(req)
    db_sess = db_session.create_session()
    if 'region' in req:
        region = req['region'].strip()
        print([region])
    if 'options' in req:
        if request.form['options'] == '0':
            flag_date = 0
        else:
            flag_date = 1
        return flag_date
    if 'prob_0' in req:
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        problem = db_sess.query(Complaint).filter(Complaint.id == int(req["prob_0"])).first()
        problem.n_confirmation += 1
        if user.ver_problems:
            user.ver_problems += f'{req["prob_0"]},'
        else:
            user.ver_problems = f'{req["prob_0"]},'
        db_sess.commit()
    elif 'prob_1' in req:
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        problem = db_sess.query(Complaint).filter(Complaint.id == int(req["prob_1"])).first()
        problem.n_confirmation -= 1
        lst_problems = user.ver_problems.split(',')
        lst_problems.remove(req['prob_1'])
        user.ver_problems = ','.join(lst_problems)
        db_sess.commit()
    if 'th_0' in req:
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        thank = db_sess.query(Thank).filter(Thank.id == int(req["th_0"])).first()
        thank.n_accession += 1
        if user.ver_thanks:
            user.ver_thanks += f'{req["th_0"]},'
        else:
            user.ver_thanks = f'{req["th_0"]},'
        db_sess.commit()
    elif 'th_1' in req:
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        thank = db_sess.query(Thank).filter(Thank.id == int(req["th_1"])).first()
        thank.n_accession -= 1
        lst_problems = user.ver_thanks.split(',')
        lst_problems.remove(req['th_1'])
        user.ver_thanks = ','.join(lst_problems)
        db_sess.commit()


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
            email=form.email.data
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
        diction = shaping_dictionary(i, False)
        width, height = Image.open(f"static/img/img_problems/{i.id}.jpg").size
        diction['size'] = image_scaling(width, height)
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
    coordinates = '55.753630,37.620070'
    if current_user.is_authenticated:
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        if user.coordinates_map:
            coordinates = user.coordinates_map
    coordinates = coordinates.split(',')
    return render_template('geolocation.html', title='Главная', list_problems=list_problems, backlight=lst_backlight,
                           url=URL, lon=coordinates[0], lat=coordinates[1])


@app.route('/all_problems', methods=["GET", 'POST'])
def all_problems():
    db_sess = db_session.create_session()
    flag_date = 0
    lst_backlight = ['-outline', '-outline']
    region = 'все'
    if request.method == "POST":
        print(request.form)
        s = request_processing(request.form)
        if s:
            flag_date = s
    lst_backlight[flag_date] = ''
    list_problems = []
    for i in db_sess.query(Complaint).all():
        diction = shaping_dictionary(i)
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
        my_problems=False, url=URL, len_pr=column_length(), thank=False)


@app.route('/my_problems', methods=['GET', 'POST'])
def my_problems():
    db_sess = db_session.create_session()
    flag_date = 0
    lst_backlight = ['-outline', '-outline']
    region = 'все'
    user = db_sess.query(User).filter(User.email == current_user.email).first()
    if request.method == "POST":
        print(request.form)
        s = request_processing(request.form)
        if s:
            flag_date = s
    lst_backlight[flag_date] = ''
    list_problems = []
    for i in db_sess.query(Complaint).all():
        diction = shaping_dictionary(i)
        if user.my_problems:
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
        my_problems=True, url=URL, len_pr=column_length(current_user.id), thank=False)


@app.route('/problem/<int:id_problem>', methods=['GET', 'POST'])
def problem(id_problem):
    if request.method == "POST":
        request_processing(request.form)
    is_problem = db_sess.query(Complaint).filter(Complaint.id == id_problem).first()
    diction = shaping_dictionary(is_problem)
    return render_template(
        'problem.html', diction=diction, title=is_problem.name, len_pr=column_length(id_problem=is_problem.id))


@app.route('/all_thanks', methods=["GET", 'POST'])
def all_thanks():
    db_sess = db_session.create_session()
    flag_date = 0
    lst_backlight = ['-outline', '-outline']
    if request.method == "POST":
        print(request.form)
        s = request_processing(request.form)
        if s:
            flag_date = s
    lst_backlight[flag_date] = ''
    list_thanks = []
    for i in db_sess.query(Thank).all():
        list_thanks.append(shaping_dictionary(i, thank=True))
    if flag_date == 0:
        list_thanks.sort(key=operator.itemgetter('datetime'), reverse=True)
    else:
        list_thanks.sort(key=operator.itemgetter('n_ver'), reverse=True)
    return render_template(
        'problems.html', list_problems=list_thanks, title='Благодарности', backlight=lst_backlight,
        my_problems=False, url=URL, len_pr=column_length(cl=Thank), thank=True)


@app.route('/resolved_problems', methods=["GET", 'POST'])
def resolved_problems():
    db_sess = db_session.create_session()
    if request.method == "POST":
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        problem = db_sess.query(Resolved).filter(Resolved.id == int(request.form['problem'])).first()
        if str(user.id) not in problem.users.split(','):
            problem.users += str(user.id) + ','
            problem.rating += request.form['rating'] + ','
            db_sess.commit()
            print(request.form)
    flag_date = 0
    lst_backlight = ['-outline', '-outline']
    if request.method == "POST":
        print(request.form)
        s = request_processing(request.form)
        if s:
            flag_date = s
    lst_backlight[flag_date] = ''
    list_resolved = []
    for i in db_sess.query(Resolved).all():
        list_resolved.append(shaping_dictionary(i, resolved=True))
    print(list_resolved)
    # доделать
    # if flag_date == 0:
    #     list_resolved.sort(key=operator.itemgetter('datetime'), reverse=True)
    # else:
    #     list_resolved.sort(key=operator.itemgetter('n_ver'), reverse=True)
    return render_template(
        'resolved_problems.html', list_problems=list_resolved, title='Решённые проблемы', backlight=lst_backlight,
        my_problems=False, url=URL, len_pr=column_length(cl=Thank))


@app.route('/api/login', methods=['POST'])
def api_login():
    if request.method == 'POST':
        if not request.json:
            return make_response(jsonify({'error': 'Empty request'}), 400)
        elif not all(key in request.json for key in
                     ['email', 'password']):
            return make_response(jsonify({'error': 'Bad request'}), 400)
        else:
            email, password = request.json['email'], request.json['password']
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == email).first()
            if user and user.check_password(password):
                return make_response(jsonify({'status': 'OK', 'id': user.id}), 201)
            if not user:
                return make_response(jsonify({'error': 'User not registered'}), 404)
            return make_response(jsonify({'error': 'Invalid password or email'}), 401)


@app.route('/api/register', methods=['POST'])
def api_register():
    if request.method == 'POST':
        if not request.json:
            return make_response(jsonify({'error': 'Empty request'}), 400)
        elif not all(key in request.json for key in
                     ['email', 'password', 'name', 'surname']):
            return make_response(jsonify({'error': 'Bad request'}), 400)
        else:
            email, password = request.json['email'], request.json['password']
            name, surname = request.json['name'], request.json['surname']
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == email).first():
                return make_response(jsonify({'error': 'User already exists'}), 409)
            user = User(
                name=name,
                surname=surname,
                email=email
            )
            user.set_password(password)
            db_sess.add(user)
            db_sess.commit()
            return make_response(jsonify({'status': 'register successful', 'id': user.id}), 201)


@app.route('/api/all_problems', methods=['GET', 'POST'])
def api_all_problem():
    if request.method == 'GET':
        db_sess = db_session.create_session()
        list_problems = []
        for i in db_sess.query(Complaint).all()[:15]:
            diction = shaping_dictionary(i)
            list_problems.append(diction)
        return make_response(jsonify({'problems': list_problems, 'status': 'OK'}), 201)
    if request.method == 'POST':
        id_problem, verified, user_id = request.json['id'], request.json['verified'], request.json['user_id']
        db_sess = db_session.create_session()
        problem = db_sess.query(Complaint).filter(Complaint.id == id_problem).first()
        if not problem:
            return make_response(jsonify({'error': 'No problem'}), 401)
        user = db_sess.query(User).filter(User.id == user_id).first()
        problem = db_sess.query(Complaint).filter(Complaint.id == id_problem).first()
        if verified:
            problem.n_confirmation += 1
            if user.ver_problems:
                user.ver_problems += f'{id_problem},'
            else:
                user.ver_problems = f'{id_problem},'
        else:
            problem.n_confirmation -= 1
            lst_problems = user.ver_problems.split(',')
            lst_problems.remove(id_problem)
            user.ver_problems = ','.join(lst_problems)
        db_sess.commit()
        return make_response(jsonify({'status': 'OK'}), 201)


@app.route('/api/add_problem', methods=['POST'])
def api_add_problem():
    if request.method == 'POST':
        if request.files:
            write_to_file(request.files['file'].read(), "example.jpg")
            return make_response(jsonify({'status': 'Image recorded'}), 200)

        if not request.json:
            return make_response(jsonify({'error': 'Empty request'}), 400)
        elif not all(key in request.json for key in
                     ['name', 'description', 'coordinates', 'user_id']):
            return make_response(jsonify({'error': 'Bad request'}), 400)
        else:
            name, description, category = request.json['name'], request.json['description'], request.json['category']
            coordinates, user_id = request.json['coordinates'], request.json['user_id']
            photo = convert_to_binary_data("example.jpg")
            id_problem = add_complaint(name=name, description=description, coordinates=coordinates,
                                       photo=photo, user_id=user_id, category=category)

            if id_problem:
                return make_response(jsonify({'id_problem': id_problem}), 201)
            else:
                return make_response(jsonify({'status': 'ОШибочка'}), 200)


@app.route('/api/all_users', methods=['GET'])
def api_all_users():
    if request.method == 'GET':
        db_sess = db_session.create_session()
        list_users = []
        for i in db_sess.query(User).all():
            list_users.append(i.email)
        return make_response(jsonify({'users': list_users, 'status': 'OK'}), 201)


if __name__ == '__main__':
    app.run()
