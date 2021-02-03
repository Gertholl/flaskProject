from flask import Flask, request,Response,make_response
from flask_socketio import SocketIO, emit, send
from uuid import uuid4
import random
from database import db, Code
import json
import requests



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test.sqlite'
db.init_app(app)


token:str = '2af02bec58db8f6a30bf4fb4060ca681'
# socketio = SocketIO(app)

clients=[]

@app.route('/')
def index():
    return 'Пися'
# @socketio.on('connect')
# def handle_my_custom_event():
#     print('Client connected')
#     # send(message='Пися')
#
#     clients.append(request.sid)
#     print(clients)
#     emit('connect','Сам соси')
#
# @socketio.on('disconnect')
# def test_disconnect():
#     clients.remove(request.sid)
#     print('Client disconnected')
#
# @socketio.on('msg')
# def msg(message):
#     print(message)
#     emit('msg', 'Сам соси')


# @app.route('/test')
# def send_message():
#     client_id = clients[-1]
#     emit('main', 'ЧО тЫ ДОЕБАЛСЯ', room=client_id)
#     print('sending message "{}" to client "{}".'.format(data, client_id))

# @app.route('/webhook',methods=['POST', 'GET'])
# def webhook():
#     if request.method == 'POST':
#         content = request.data.decode()
#         data = json.loads(content)
#         phone = data['phone']
#         order_id = data['order_id']
#         executor = data['Executor']
#         try:
#             temp_data = Temp_data(phone=phone, order_id=order_id, executor=executor)
#             db.session.add(temp_data)
#             db.session.flush()
#             db.session.commit()
#         except:
#             print('Запись уже существует')
#         return make_response(f'{phone}:{order_id}:{executor}',200)

    #
    # if request.method == 'GET':
    #     data = Temp_data.query.all()
    #     tr = '<tr><th>Телефон</th><th>Номер заказа</th><th>Исполнитель</th><tr>'
    #     for i in data:
    #         tr += f'<tr><td>{i.phone}</td><td>{i.order_id}</td><td>{i.executor}</td><tr>'
    #     return f'<table style="text-align:center">{tr}</table>'


# @app.route('/add/<telephone>')
# def index(telephone: int):
#     try:
#         u = Users(phone=telephone, token=f'{uuid4()}')
#         db.session.add(u)
#         db.session.flush()
#         db.session.commit()
#         return 'GOOD'
#     except:
#         db.session.rollback()
#         return 'Ошибка добавления в БД'


@app.route('/check-phone/', methods=['GET', 'POST'])
def check_phone():
    telephone:int = request.args.get('phone')
    # try:
    #     u = Users.query.filter(Users.phone == telephone).first()
    #     if u.phone:
    #         try:
    #             temp_code = 111111
    #             # temp_code = random.randint(100000, 999999)
    #             auth = Code(phone=u.phone, auth_code=temp_code, attempt=3)
    #             db.session.add(auth)
    #             db.session.flush()
    #             db.session.commit()
    #             # a = Code.query.filter(Code.phone == telephone).first()
    #             # requests.get(
    #             #     f'https://sms.ru/sms/send?api_id=C7391857-66B4-5B0D-3026-AD6772BEF38F&to={telephone}&msg={a.auth_code}&json=1')
    #             status = 'ok'
    #             print('Сохранено')
    #         except:
    #             print('Хуй')
    #             status = 'code exists'
    #             db.session.rollback()
    # except:
    #     status = 'not user'
    a = requests.get(f'https://124bt.ru/api.php/bt.auth.sendPhone/?phone={telephone}&access_token={token}').text
    answer = json.loads(a)
    print(answer['status'])
    if answer['status'] == "ok":
        try:
            user_id = int(answer['message'])
            print(user_id)
            temp_code = 111111
            # temp_code = random.randint(100000, 999999)
            auth = Code(user_id=user_id, auth_code=temp_code, attempt=3)
            db.session.add(auth)
            db.session.flush()
            db.session.commit()
            print('Данные сохранены')
        except:

            print('ХУй')
            pass
    return answer


def delete_code(user_id:int) -> bool:
    try:
        d = Code.query.get(user_id)
        db.session.delete(d)
        db.session.commit()
        print('Данные удалены')
        return True
    except Exception as e:
        print('Что-то пошло не так')
        print(e)
        return False


@app.route('/confirm-code/', methods=['GET'])
def check_code():

    user_id: int = request.args.get('user_id')
    print(user_id)
    code: int = request.args.get('code')
    print(code)
    res = Code.query.filter_by(user_id=user_id).first()
    print(res)

    if int(code) == int(res.auth_code):
            user_info = requests.get(f'https://124bt.ru/api.php/bt.auth.getUserInfo/?user_id={int(user_id)}&access_token={token}').text
            if delete_code(user_id):
                return user_info
            else:
                return '404'
    else:
            if res.attempt > 1:
                print(res.attempt)
                att = res.attempt-1
                Code.query.filter_by(user_id=res.user_id).update(dict(attempt=att))
                db.session.flush()
                db.session.commit()
                print(res.attempt)
                answer = {'status': 'bad', 'message': res.attempt}
                return answer
            else:
                delete_code(res.user_id)
                return {'status': 'error'}



if __name__ == "__main__":
    app.run()
