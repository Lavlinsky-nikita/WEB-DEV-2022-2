import random
from flask import Flask, render_template
from faker import Faker

fake = Faker()

# WSGI - стандарт взаимодействия между веб приложение и веб сервером


# объект класса, name - принимает значение main, если запускаем файл, если импортируем - значение будет название модуля  
# Используется во фласке, чтобы определить откуда загружать другие файлы (шаблоны)
app = Flask(__name__)
application = app

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']

def generate_comments(replies=True):
    comments = []
    for i in range(random.randint(1, 3)):
        comment = { 'author': fake.name(), 'text': fake.text() }
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments

def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }


posts_list = sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)

#  Декораторы — это, по сути, "обёртки", которые дают нам возможность изменить поведение функции, не изменяя её код
# @app.route('/') - декаратор с методом роут принимает шаблон пути 
# index() -  view functio? обработчик которая обрабатывает запрос, поторый поступил, хранятся в app 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list)

# Передаем параметры как часть url, int - конвертор
@app.route('/posts/<int:index>')
def post(index):
    p = posts_list[index]
    return render_template('post.html', title=p['title'], post=p)

@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')

# {{ }} - подстановка значения, которое мы передали -->
# {% block content %}  {% endblock %} - содержимое, которое можно переопределить на конкретной странице, в потомках доступно содержимое блоко по умочанию, у блоков должно быть уникальное название   
# {% extends 'base.html' %} - наследование и название шаблона
# {{ }} - выражения значение которых, подставляется в итоговый документ, видны на странице 
# Чтобы передать значения в шаблон мы их передаем в качестве параметров в  render_template
