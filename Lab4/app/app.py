
from click import password_option
from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from mysql_db import MySQL
import mysql.connector as connector

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к данной страницк необходимо пройти процедуру аутентификации.'
login_manager.login_message_category = 'warning'


app = Flask(__name__)
application = app

login_manager.init_app(app)

app.config.from_pyfile('config.py')

mysql = MySQL(app)

# Параметры которые необходимо извлекать из запроса при создании пользователя 
CREATE_PARAMS = ['login','password','first_name','last_name','middle_name']

def request_params(params_list):
    params ={}
    for param_name in params_list:
        # get чтобы невернул ошибку если такого параметра нет, or None чтобы пустые значения заменялись на None
        params[param_name]=request.form.get(param_name) or None
    return params

class User(UserMixin):
    def __init__(self, user_id, login):
        super().__init__()
        self.id = user_id
        self.login = login


@login_manager.user_loader
def load_user(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (user_id,))
        db_user=cursor.fetchone()
    if db_user:
        return User(user_id=db_user.id, login=db_user.login) 
    return None


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_ = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        with mysql.connection.cursor(named_tuple=True) as cursor:
            cursor.execute(
                'SELECT * FROM users WHERE login=%s AND password_hash=SHA2(%s, 256);', 
                (login_, password))
            db_user=cursor.fetchone()
        if db_user:
            login_user(User(user_id=db_user.id, login=db_user.login),
                        remember=remember_me)
            flash('Вы успешно прошли процедуру аутентификации.', 'success')
            next_ = request.args.get('next')
            return redirect(next_ or url_for('index'))
        flash('Введенны неверные логин и/или пароль.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/users')
def users():
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users;')
        users=cursor.fetchall()
    return render_template('users/index.html', users=users)

@app.route('/users/new')
@login_required
def new():
    return render_template('users/new.html', user={})

@app.route('/users/create', methods=['POST'])
@login_required
def create():
    params = request_params(CREATE_PARAMS)
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            cursor.execute(
                ('INSERT INTO users (login, password_hash, last_name, first_name, middle_name)'
                'VALUES (%(login)s, SHA2(%(password)s, 256), %(last_name)s, %(first_name)s, %(middle_name)s);'),
                params
            )
            # Закомитили транзакцию
            mysql.connection.commit()
       # Перехват ошибок типа 
        except connector.Error:
            flash('Введены некорректные данные. Ошибка сохранения', 'danger')
            return render_template('users/new.html', user=params)
    flash(f"Пользователь {params.get('login')} был успешно создан!", 'success')
    return redirect(url_for('users'))