
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import mysql


bp = Blueprint('visits', __name__, url_prefix='/visits')

# Журнал посещёний, отображаем записи страницы visit_logs
@bp.route('/logs')
def logs():
    # Запрос к базе
    with mysql.connection.cursor(named_tuple=True) as cursor:
        # Отображаем пользователя, путь до станицы, и дата действия
        # JOIN users ON visit_logs.user_id = users.id объединяет 2 талицы по users.id
        # LEFT JOIN - чтобы были записы таблицы visit_logs, но у которых users.id пустое и нет пары в таблице user
        # ORDER BY created_at DESC (по убыванию) - сотрировка, чтобы показывать последнее действие
        cursor.execute('SELECT visit_logs.*, users.last_name, users.first_name, users.middle_name FROM visit_logs LEFT JOIN users ON visit_logs.user_id = users.id ORDER BY visit_logs.created_at DESC;')
        records = cursor.fetchall()
    # возвращает шаблон, и передаем записи которые есть в табличке
    return render_template('visits/logs.html', records=records)

# Статистика по пользователям
@bp.route('/stats/users')
def users_stat():
    query = 'SELECT users.last_name, users.first_name, users.middle_name, COUNT (*)'

@bp.route('/stats/pages')
def pages_stat():
    pass