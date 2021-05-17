from data import db_session
from data.complaints import Complaint
from data.thanks import Thank
from data.sentenses import Sentense
import os


def convert_to_binary_data(filename):
    # Преобразование данных в двоичный формат
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data


def write_to_file(data, filename):
    # Преобразование двоичных данных в нужный формат
    with open(filename, 'wb') as file:
        file.write(data)


# def download_image():
# # функция установки изображения из базы данных
# global picture
# pictures = os.listdir('static/img/avatars')
# db_sess = db_session.create_session()
# user = db_sess.query(Complaint).filter(Complaint.coordinates == current_user.email).first()
# write_to_file(user.avatar, f'static/img/avatars/{len(pictures) + 1}.png')
# picture = f"../static/img/avatars/{len(pictures) + 1}.png"


def add_complaint(**kwards):
    db_sess = db_session.create_session()
    for i in ['name', 'description', 'coordinates', 'photo']:
        if i not in list(kwards.keys()):
            return
    for i in db_sess.query(Complaint).all():
        if kwards['coordinates'] == i.coordinates:
            complaint = db_sess.query(Complaint).filter(Complaint.coordinates == kwards['coordinates']).first()
            complaint.n_confirmation += 1
            db_sess.commit()
            return
    if 'category' not in list(kwards.keys()):
        complaint = Complaint(
            name=kwards['name'],
            description=kwards['description'],
            coordinates=kwards['coordinates'],
            photo=kwards['photo'],
            category='Другое'
        )
    else:
        complaint = Complaint(
            name=kwards['name'],
            description=kwards['description'],
            coordinates=kwards['coordinates'],
            photo=kwards['photo'],
            category=kwards['category']
        )
    db_sess.add(complaint)
    db_sess.commit()
    return


def add_thanks(**kwards):
    db_sess = db_session.create_session()
    for i in ['name', 'description', 'coordinates', 'photo']:
        if i not in list(kwards.keys()):
            return
    for i in db_sess.query(Thank).all():
        if kwards['coordinates'] == i.coordinates:
            thanks = db_sess.query(Complaint).filter(Thank.coordinates == kwards['coordinates']).first()
            thanks.n_accession += 1
            db_sess.commit()
            return
    thanks = Complaint(
        name=kwards['name'],
        description=kwards['description'],
        coordinates=kwards['coordinates'],
        photo=kwards['photo'],
    )
    db_sess.add(thanks)
    db_sess.commit()
    return


def add_sentense(**kwards):
    db_sess = db_session.create_session()
    for i in ['description', 'file']:
        if i not in list(kwards.keys()):
            return
    if 'category' not in list(kwards.keys()):
        category = 'Другое'
    else:
        category = kwards['category']
    sentense = Sentense(
        description=kwards['description'],
        file=kwards['file'],
        category=category,
    )
    db_sess.add(sentense)
    db_sess.commit()
    return


db_session.global_init("db/users_my_site.db")
add_complaint(name='Дорога', description='fjgfkmfgk', coordinates='44, 36', category='ЖКХ')
