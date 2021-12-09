from data import db_session
from data.complaints import Complaint
from data.resolved_problem import Resolved
from data.thanks import Thank
from db_work import add_complaint
from constants import write_to_file, convert_to_binary_data, height_len


def set_complaint(id_pr):
    db_session.global_init("db/site_db.db")
    db_sess = db_session.create_session()
    problem = db_sess.query(Resolved).filter(Resolved.id == id_pr).first()
    problem.photo = convert_to_binary_data("пляж.jpg")
    db_sess.commit()
    return 'ok'


set_complaint(1)
# print(add_complaint(name='Улица без света',
#              description='На улице полнейшая темнота, так как отсутвует или не работают все фонари..',
#              photo=convert_to_binary_data('темнота.jpg'),
#              coordinates='55.1634,60.1246', category='Другое', user_id=1))
