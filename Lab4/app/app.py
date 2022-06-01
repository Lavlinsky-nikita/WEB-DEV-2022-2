
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

# mysql - объект для установления соединения
mysql = MySQL(app)

# Параметры которые необходимо извлекать из запроса при создании пользователя 
CREATE_PARAMS = ['login','password','first_name','last_name','middle_name', 'role_id']
# Параметры которые необходимо извлекать из запроса при редактировании пользователя 
UPDATE_PARAMS = ['first_name', 'last_name', 'middle_name', 'role_id']

# Функция для извлечения параметра, возвращет словарь 
def request_params(params_list):
    params ={}
    for param_name in params_list:
        # get чтобы невернул ошибку если такого параметра нет, or None чтобы пустые значения заменялись на None
        params[param_name]=request.form.get(param_name) or None
    return params

# Функция загружающая все роли имеющиеся в базе
def load_roles():
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT id, name FROM roles;')
        roles = cursor.fetchall()
    return roles

class User(UserMixin):
    def __init__(self, user_id, login):
        super().__init__()
        self.id = user_id
        self.login = login

# mysql.connection - вернет объект соединения, cursor - создаст cursor(as cursor)
# cursor.execute - запрос в БД, WHERE id=%s - где индефикатор равен тому, который передан в эту функцию
# Передаем индефикатор в виде tuple (user_id,) запятая - для так как у нас tuple
# Результат будет доступен через cursor
# fetchone() - вернет единственную запись в виде tuple, если результата нет вернет None
# fetchall() - вернет все записи запроса в виде списка
# fetchmany(10) - по частям, сколько записей хотим получить
# named_tuple=True - записи из таблички будут не в виде tuple, а как именнованный tuple (позволяет создавать подкласы стандартного tuple, к полям котогого можно обращаться по названию, id-например)
@login_manager.user_loader
def load_user(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (user_id,))
        db_user=cursor.fetchone()
    # Если пользователь найден создаем его
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
        # Запрос, SHA2(%s, 256)- для сопоставления пароля, %s - пароль, 256=длина
        with mysql.connection.cursor(named_tuple=True) as cursor:
            cursor.execute(
                'SELECT * FROM users WHERE login=%s AND password_hash=SHA2(%s, 256);', 
                # подставляем значения в виде tuple
                (login_, password))
            db_user=cursor.fetchone()
        # Проверка, логиним и выводим сообщение
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

# 
@app.route('/users')
def users():
    with mysql.connection.cursor(named_tuple=True) as cursor:
        # 
        # LEFT JOIN - созранятся все записи даже если у них нет роли 
        cursor.execute('SELECT users.*, roles.name AS role_name FROM users LEFT JOIN roles ON users.role_id = roles.id;')
        users = cursor.fetchall()
    return render_template('users/index.html', users=users)

# @login_required - ограничение доступа для неавторизованных пользователей

@app.route('/users/new')
@login_required
def new():
    return render_template('users/new.html', user={}, roles=load_roles())



@app.route('/users/create', methods=['POST'])
@login_required
def create():
    # Извлечение параметров
    params = request_params(CREATE_PARAMS)
    # Преобразоавние к int 
    params['role_id'] = int(params['role_id']) if params['role_id'] else None
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            # INSERT вставляет новые записи в таблицу
            #  %(login)s - указываем конкретные значения из словаря, куда хотим вставить
            cursor.execute(
                ('INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id)'
                'VALUES (%(login)s, SHA2(%(password)s, 256), %(last_name)s, %(first_name)s, %(middle_name)s, %(role_id)s);'),
                params
            )
            # Закомитили транзакцию
            mysql.connection.commit()
       # Перехват ошибок типа 
        except connector.Error:
            flash('Введены некорректные данные. Ошибка сохранения', 'danger')
            return render_template('users/new.html', 
                                    user=params,
                                    roles=load_roles())
    flash(f"Пользователь {params.get('login')} был успешно создан!", 'success')
    return redirect(url_for('users'))

# передаем индефикатор как часть урла, подставляться в user_id и обязательно int
# Всегда будет GET запрос
@app.route('/users/<int:user_id>')
def show(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (user_id,))
        user=cursor.fetchone()
    return render_template('users/show.html', user=user)

@app.route('/users/<int:user_id>/edit')
@login_required
def edit(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT * FROM users WHERE id=%s;', (user_id,))
        user = cursor.fetchone()
    return render_template('users/edit.html', user=user, roles=load_roles())

@app.route('/users/<int:user_id>/update', methods=['POST'])
@login_required
def update(user_id):
    params = request_params(UPDATE_PARAMS)
    params['role_id'] = int(params['role_id']) if params['role_id'] else None
    # для того чтобы передать данные в виде словаря
    params['id'] = user_id
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try:
            cursor.execute(
                ('UPDATE users SET last_name=%(last_name)s, first_name=%(first_name)s, ' 
                'middle_name=%(middle_name)s, role_id=%(role_id)s WHERE id = %(id)s;'), params)
            mysql.connection.commit()
        except connector.Error:
            flash('Введены некорректные данные. Ошибка сохранения', 'danger')
            return render_template('users/edit.html', user=params, roles=load_roles())
    flash("Пользователь был успешно обновлён!", 'success')
    return redirect(url_for('show', user_id=user_id))

@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete(user_id):
    with mysql.connection.cursor(named_tuple=True) as cursor:
        try: 
            cursor.execute('DELETE FROM users WHERE id=%s;', (user_id,))
            mysql.connection.commit()
        except connector.Error:
            flash('Не удалось удалить пользователя', 'danger')
            return redirect(url_for('users'))
    flash("Пользователь был успешно удалён!", 'success')
    return redirect(url_for('users'))