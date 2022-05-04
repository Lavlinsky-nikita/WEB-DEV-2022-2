from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from mysql_db import MySQL


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к данной страницк необходимо пройти процедуру аутентификации.'
login_manager.login_message_category = 'warning'


app = Flask(__name__)
application = app

login_manager.init_app(app)

app.config.from_pyfile('config.py')

mysql = MySQL(app)

class User(UserMixin):
    def __init__(self, user_id, login):
        super().__init__()
        self.id = user_id
        self.login = login


@login_manager.user_loader
def load_user(user_id):
    with mysql.connection.cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;' , (user_id))
        db_user=cursor.fetchone()
    if db_user:
        return User(user_id=db_user[0], login=db_user[1]) 
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
        with mysql.connection.cursor() as cursor:
            cursor.execute(
                'SELECT * FROM users WHERE login=%s AND password_hash=SHA(%s, 256);', 
                (login_, password))
            db_user=cursor.fetchone()
        if db_user:
            login_user(User(user_id=db_user[0], login=db_user[1]),
                        remember=remember_me)
            flash('Вы успешно прошли процедуру аутентификации.', 'success')
            next_ = request.args.get('next')
            return redirect(url_for('index', message=''))
        flash('Введенны неверные логин и/или пароль.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

