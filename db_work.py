from data import db_session
from data.complaints import Complaint
from data.users import User
from data.thanks import Thank
from data.sentenses import Sentense
from data.resolved_problem import Resolved
import math
import os
from PIL import Image
from constants import write_to_file, convert_to_binary_data, height_len
from flask_login import current_user


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)
    return int(distance)


# def download_image():
# # функция установки изображения из базы данных
# global picture
# pictures = os.listdir('static/img/avatars')
# db_sess = db_session.create_session()
# user = db_sess.query(Complaint).filter(Complaint.coordinates == current_user.email).first()
# write_to_file(user.avatar, f'static/img/avatars/{len(pictures) + 1}.png')
# picture = f"../static/img/avatars/{len(pictures) + 1}.png"


def add_complaint(**kwards):
    db_session.global_init("db/site_db.db")
    db_sess = db_session.create_session()
    if not all(key in kwards for key in ['name', 'description', 'coordinates', 'photo', 'user_id']):
        return 'Not all keys for problem'
    for i in db_sess.query(Complaint).all():
        if lonlat_distance((float(kwards['coordinates'].split(',')[0]), float(kwards['coordinates'].split(',')[1])),
                           (float(i.coordinates.split(',')[0]), float(i.coordinates.split(',')[1]))) <= 20 and \
                kwards['category'] == i.category:
            i.n_confirmation += 1
            db_sess.commit()
            return 'Похожая проблема'
    complaint = Complaint(
            name=kwards['name'],
            description=kwards['description'],
            coordinates=kwards['coordinates'],
            photo=kwards['photo'],
            category=kwards['category']
        )
    db_sess.add(complaint)
    user = db_sess.query(User).filter(User.id == kwards['user_id']).first()
    if user.my_problems:
        user.my_problems += f'{complaint.id},'
    else:
        user.my_problems = f'{complaint.id},'
    user.coordinates_map = kwards["coordinates"]
    db_sess.commit()
    return complaint.id


def add_thanks(**kwards):
    db_session.global_init("db/site_db.db")
    db_sess = db_session.create_session()
    for i in ['name', 'description', 'photo']:
        if i not in list(kwards.keys()):
            return
    if db_sess.query(Thank).all():
        write_to_file(kwards['photo'], f'static/img/thanks/{len(list(db_sess.query(Thank).all())) + 1}.jpg')
    else:
        write_to_file(kwards['photo'], f'static/img/thanks/1.jpg')
    thanks = Thank(
        name=kwards['name'],
        description=kwards['description'],
        photo=kwards['photo'],
    )
    db_sess.add(thanks)
    db_sess.commit()
    return


def add_sentense(**kwards):
    db_sess = db_session.create_session()
    for i in ['description', 'file', 'name']:
        if i not in list(kwards.keys()):
            return
    if 'category' not in list(kwards.keys()):
        category = 'Другое'
    else:
        category = kwards['category']
    sentense = Sentense(name=kwards['name'],
                        description=kwards['description'],
                        file=kwards['file'],
                        category=category,
                        )
    db_sess.add(sentense)
    db_sess.commit()
    return


def column_length(id_user='!', id_problem='!', cl=Complaint):
    length = 0
    name_pape = 'img_problems'
    if cl == Thank:
        name_pape = 'thanks'
    db_session.global_init("db/site_db.db")
    db_sess = db_session.create_session()
    if id_user == '!':
        for i in db_sess.query(cl).all():
            width, height = Image.open(f"static/img/{name_pape}/{i.id}.jpg").size
            length += height_len(width, height)
    elif id_problem != '!':
        i = db_sess.query(cl).filter(cl.id == int(id_problem)).first()
        width, height = Image.open(f"static/img/{name_pape}/{i.id}.jpg").size
        length += height_len(width, height)
    else:
        # сюда идут только проблемы
        user = db_sess.query(User).filter(User.email == current_user.email).first()
        for i in db_sess.query(Complaint).all():
            if str(i.id) in user.my_problems.split(','):
                width, height = Image.open(f"static/img/img_problems/{i.id}.jpg").size
                length += height_len(width, height)
    if length == 0:
        return 10
    return length




def replacement(id_com, img, thank=False):
    db_session.global_init("db/site_db.db")
    db_sess = db_session.create_session()
    if not thank:
        complaint = db_sess.query(Complaint).filter(Complaint.id == id_com).first()
        complaint.photo = convert_to_binary_data(f'static/img/img_problems/{img}')
        db_sess.commit()
        os.remove(f'static/img/img_problems/{id_com}.jpg')
    else:
        thank = db_sess.query(Thank).filter(Thank.id == id_com).first()
        thank.photo = convert_to_binary_data(f'static/img/thanks/{img}')
        db_sess.commit()
        os.remove(f'static/img/thanks/{id_com}.jpg')


def add_resolved(**kwards):
    db_session.global_init("db/site_db.db")
    db_sess = db_session.create_session()
    for i in ['name', 'description', 'problem', 'photo']:
        if i not in list(kwards.keys()):
            return
    resolved_problem = Resolved(
        name=kwards['name'],
        description=kwards['description'],
        problem=kwards['problem'],
        photo=kwards['photo']
    )
    db_sess.add(resolved_problem)
    db_sess.commit()
    return


#if __name__ == '__main__':
#    add_resolved(name='Пляж чист!', description='Пляж был растищен волонтёрами, собрано 12 мешков мусора.',
#                 problem=4, photo=convert_to_binary_data('static/img/thanks/цветы.jpg'))
#