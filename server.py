from entities.DatabaseManager import DatabaseManager
from flask_cors import CORS, cross_origin

from flask import Flask, request, jsonify, render_template, g, redirect, url_for, make_response, flash
from playhouse.shortcuts import model_to_dict
from reader_serial import ReaderCom
from test_reader import TestReader
import jwt 
from datetime import datetime, timedelta
import json
from logger import Logger

# Создание сервисов
COM_PORT = 'COM6'
db_manager = DatabaseManager()

Logger = Logger()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key' 
CORS(app)



def _user_to_model(user):
    user_data = {
                'id' : user.id,
                'username': user.username,
                'first_name': user.first_name,
                'name': user.name,
                'last_name': user.last_name,
                'rfid': None  # По умолчанию RFID отсутствует
            }

    if user.rfid:  # Если у пользователя есть связанный RFID
        user_data['rfid'] = {
            'id': user.rfid.id,
            'name': user.rfid.name
        }
       
    return user_data


"""
    Функция `add_user` — это маршрут в приложении Python Flask, который обрабатывает добавление нового пользователя.
     пользователя в базе данных.
     :return: перенаправление на страницу входа, если пользователь не прошел аутентификацию. Если метод запроса
     POST, он добавляет нового пользователя в базу данных и перенаправляет на страницу пользователя. Если метод запроса
     GET, он отображает шаблон add_user.html с пользователем, для которого установлено значение None.
"""
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():   
    try:    
        if _is_auth() == None:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            user = db_manager.add_user(username=request.form.get('username'),
                                first_name=request.form.get('first_name'),
                                name=request.form.get('name'),
                                last_name=request.form.get('last_name'),
                                password = request.form.get('password'))
            
            Logger.info(f"Add user {user}")
            return redirect(url_for('get_user', user_id=user.id))
     
        return render_template('add_user.html', user=None)
    except Exception as e:
        Logger.error(e)

"""
    This function deletes a user from the database based on their user ID.
    @param user_id - The `user_id` parameter is an integer that represents the ID of the user to be
    deleted.
    @returns either a redirect to the login page if the user is not authenticated, or it is returning a
    rendered template with a success or failure message indicating whether the user with the given ID
    was successfully deleted or not.
"""
@app.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_user(user_id):   
    try:
        if _is_auth() == None:
            return redirect(url_for('login'))     
           
        result = db_manager.delete_user_by_id(user_id=user_id)  
        if result:
            Logger.info(f"Delete user id = {user_id}")         
            return render_template('info.html', message=f"Пользователь с id = {user_id} успешно удален!")
        else:
            return render_template('info.html', message=f"Пользователь с id = {user_id} не удален!")
    except Exception as e:
        Logger.error(e)

    

"""
    The function `add_rfid_to_user_form` is a Flask route that handles both GET and POST requests to add
    an RFID to a user in a database.
    @param user_id - The user_id parameter is the ID of the user to whom the RFID is being added.
    @returns In the code snippet, there are two possible return statements:
"""
@app.route('/add_rfid/<int:user_id>', methods=['GET', 'POST'])
def add_rfid_to_user_form(user_id):
    try:
        if (request.method == 'GET'):        
            user = db_manager.get_user_by_id(user_id)
            return render_template('add_rfid.html', user=_user_to_model(user))
        
        if (request.method == 'POST'):
            rfid_id = request.form.get('rfid_id')
            rfid_name = request.form.get('rfid_name')
            user_id = request.form.get('user_id')
        
            rfid = db_manager.add_rfid_to_user(user_id, rfid_id=rfid_id, rfid_name=rfid_name)
            
            Logger.info(f"Add rfid = {rfid.id} rfid_name = {fird.name}  to user id = {user_id}")   
            return redirect(url_for('get_user', user_id=user_id))
    except Exception as e:
        Logger.error(e)


# Эндпоинт для получения пользователя по RFID
@app.route('/get_user_by_rfid/<int:user_id>', methods=['GET'])
def get_user_by_rfid():
    try:
        rfid_id = request.args.get('rfid_id')
        user = db_manager.get_user_by_rfid(rfid_id)
        if user:
            return jsonify({'user_id': user.id, 'username': user.username, 'first_name': user.first_name,
                            'name': user.name, 'last_name': user.last_name})
        else:
            return jsonify({'message': 'User not found'})
    except Exception as e:
        Logger.error(e)

# Эндпоинт для получения списка всех пользователей
@app.route('/get_users', methods=['GET'])
def get_users():
    try:
        if _is_auth() == None:
            return redirect(url_for('login'))
        
        users = db_manager.get_users()       
        return render_template('users.html', users=users)
    except Exception as e:
        Logger.error(e)

    
@app.route('/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        if _is_auth() == None:
            return redirect(url_for('login'))
        
        user = db_manager.get_user_by_id(user_id = user_id)
        return render_template('user_details.html', user=_user_to_model(user))
    except Exception as e:
        Logger.error(e)
    

@app.route('/read_rfid', methods=['GET'])
def read_rfid():
    try:
        readerCom = ReaderCom(COM_PORT)
        data = readerCom.read()
        
        if data == None:
            return "error"
        
        if data.__contains__("UID"):        
            uid = data.split(":")[1].strip() 
            Logger.info(f"Scan rfid UID: {uid} ")   
            return jsonify({'rfid': uid})

        return "error"
    except Exception as e:
        Logger.error(e)
    
  
  
#login zone
def _is_auth():
    try:
        token = request.cookies.get('token')
        if token:
            try:
                decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                user = db_manager.get_user_by_id(decoded_token['user_id'])
                return user
            except jwt.ExpiredSignatureError:
                flash('Token has expired. Please log in again.', 'error')
                return None
            except jwt.InvalidTokenError:
                flash('Invalid token. Please log in again.', 'error')
                return None
    except Exception as e:
        Logger.error(e)




@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':            
            username = request.form.get('username')
            password = request.form.get('password')

            user = db_manager.get_user_by_username_and_password(username=username, password=password)

            # Create a JWT token with user information
            token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
                        app.config['SECRET_KEY'], algorithm='HS256')
        
            
            response = make_response(redirect(url_for('check_authorization')))
            response.set_cookie('token', token)
            Logger.info(f"Login in system user_id = {user.id}")  
            return response
        
        return render_template('login.html')
    except Exception as e:
        Logger.error(e)


@app.route('/login_2auth', methods=['GET', 'POST'])
def login_2auth():
    try:
        if request.method == 'POST':
            try:
                rfid = request.form.get('rfid')
                if rfid == "":
                    return jsonify({'error': 'RFID is empty', 'message': 'mot found'}), 400
                
                user = db_manager.get_user_by_rfid(rfid_id=rfid)
                
                if user == None:
                    return jsonify({'error': 'RFID is empty', 'message': 'mot found'}), 400
            
                token = jwt.encode({'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
                            app.config['SECRET_KEY'], algorithm='HS256')
            
                
                response_data = {
                    'token': token,
                    'url': "/check_authorization"                    
                }
                # Устанавливаем токен в куки
                response = make_response(jsonify(response_data), 200)
                response.set_cookie('token', token)
                Logger.info(f"Login_2auth in system user_id = {user.id} with rfid = {rfid}") 
                return response
            except Exception as e:
                response_data = {
                    'error': str(e),
                    'message': "not found"
                }
                return make_response(jsonify(response_data), 500)
            

        return render_template('login_2auth.html')
    except Exception as e:
        Logger.error(e)
    


@app.route('/logout')
def logout():
    try:
        # Clear the JWT token cookie
        user = _is_auth()
        response = redirect(url_for('login'))
        response.delete_cookie('token')
        flash('Logout successful', 'success')
        if (user != None):
            Logger.info(f"Logout system user_id = {user.id}") 
        return response
    except Exception as e:
        Logger.error(e)
    

@app.route('/get_current_username', methods=['GET'])
def get_current_username():
    try:
        user = _is_auth()
        if (user == None):
            return jsonify({'username': "Неавторизован"})     
        
        return jsonify({'username': user.username})  
    except Exception as e:
        Logger.error(e)   
        
    
@app.route('/check_authorization', methods=['GET'])
def check_authorization():
    try:
        token = request.cookies.get('token')  # Retrieve the token from the cookie
        if token:
            try:
                user = _is_auth()
                #decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
                username = user.username

                # Check if the user is authorized (you may replace this with your own logic)
                if username != None:
                    return render_template('info.html', message = f'Authorized as {username}')               
                else:
                    return render_template('info.html', message = f'Unauthorized')          

            except jwt.ExpiredSignatureError:
                return render_template('info.html', message = f'Token has expired. Please log in again')         
            except jwt.InvalidTokenError:
                return render_template('info.html', message = f'Invalid token. Please log in again')
        else:
            return jsonify({'message': 'Unauthorized'}), 401
    except Exception as e:
        Logger.error(e)
    

if __name__ == '__main__':     

    # Запускаем сервер на порте 5000
    app.run(port=5000, debug=True)
    