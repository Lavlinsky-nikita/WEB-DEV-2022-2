from flask import Flask, render_template, request, make_response
 
app = Flask(__name__)
application = app



@app.route('/')
def index():
    url = request.url
    return render_template('index.html')

@app.route('/args')
def args():
    return render_template('args.html')

@app.route('/headers')
def headers():
    return render_template('headers.html')

@app.route('/cookies')
def cookies():
    response = make_response(render_template('cookies.html'))
    if request.cookies.get('name') is None:
        response.set_cookie('name', 'qq')
    else:
        response.set_cookie('name', 'qq', expires=0)
    return response

# Добавляем методы, чтобы обрабатывать запросы
@app.route("/form", methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        context = {}
        num = []
        others = []
        allowed = [' ', '(', ')', '-', '.', '+']
        
        for i in request.form['number']:
            if i.isdigit():
                num.append(i)
            else:
                others.append(i)
        if len(num) < 10:
            context = {'error': 'номер слишком короткий'}
        elif len(others) == 3 and (len(num) == 10):
            if (others[0]=='.') and (others[1]=='.') and (others[2]=='.'):
                print('верный формат')
            else:
                context = {'error': 'номер содержит недопустимые символы'}
        elif (int(num[0]) == 8 or (int(num[0])==7 and others[0]=='+')) and len(num) == 11:
            print('верный формат')
        else:
            context = {'error': 'номер слишком длинный'}
        # Проверка каждого спецсимвола которые у нас попал в thers, на соответсвие допустимых спецсимволов
        # Если хоть один спец символ не соответсвуте => ошибка
        for symbol in others:
            if symbol not in allowed:
                context = {'error': 'номер содержит недопустимые символы'}
        
    

        if context:
            print(context)
            return render_template('form.html', context=context, number_format=number_format)
        else:
            return request.form
            
    return render_template('form.html')
