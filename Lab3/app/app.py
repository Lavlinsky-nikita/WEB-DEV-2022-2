from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required


# LoginManager - через этот класс, осуществляем настройку Аутентификации приложения
# login_manager = LoginManager() - объект класса
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к данной страницк необходимо пройти процедуру аутентификации.'
login_manager.login_message_category = 'warning'

app = Flask(__name__)
application = app

# После вызова нужно вызвать элемент init_app, с аргументом объект приложения
# Этот метод, берет бъект приложения и в качестве атрибута записывает сам себя, чтобы у приложения был доступ к этому объекту
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, user_id, login, password):
        super().__init__()
        self.id = user_id
        self.login = login
        self.password = password

# функция, которая позволяет по индификатору пользователя, который храниться в сессии, вернуть объект соответствующему пользователю 
# или вернуть None если такого пользователя нет
# Проходимся по БД, проверяем если индефикатор текущего пользователя есть в БД, то возвращаем объект этого пользователя
@login_manager.user_loader
def load_user(user_id):
    for user in get_users():
        if user['user_id']==user_id:
            return User(**user)
    return None

# Доступ к секретному ключу
app.config.from_pyfile('config.py')

def get_users():
    return [{'user_id': '1', 'login': 'user', 'password': 'qwerty'}]

@app.route('/')
def index():
    return render_template('index.html')

# session - словарь, ключ - значение
@app.route('/visits')
def visits():
    if session.get('visits_count') is None:
        session['visits_count'] = 1
    else:
        session['visits_count'] += 1
    return render_template('visits.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_ = request.form.get('login')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'
        for user in get_users():
            if user['login'] == login_ and user['password'] == password:
                login_user(User(**user), remember=remember_me)
                flash('Вы успешно прошли процедуру аутентификации.', 'success')
                next_ = request.args.get('next')
                return redirect(next_ or url_for('index'))
        flash('Введенны неверные логин и/или пароль.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/secret_page')
@login_required
def secret_page():
    return render_template('secret_page.html')