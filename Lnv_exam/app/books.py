from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import *

bp = Blueprint('books', __name__, url_prefix='/books')

BOOKS_PARAMS = ['name', 'short_description', 'year', 'genries','publishing_house','author', 'page_volume']

def params():
    return { p: request.form.get(p) for p in BOOKS_PARAMS }


@bp.route('/new', methods=['POST'])
def new():
    genries = Genre.query.all()

    books = Book(**params())
    db.session.add(books)
    db.session.commit()
    flash(f'Курс {books.name} был успешно добавлен!')

    return render_template('books/new.html', genries=genries)

@bp.route('/edit/<int:book_id>')
def edit(book_id):
    return render_template('books/edit.html')

@bp.route('/show/<int:book_id>')
def show(book_id):
    return render_template('books/show.html')

# Удаление
@bp.route('/<int:book_id>/delete', methods=['POST'])
def delete(book_id):
    Book.query.filter(id=book_id).delete()
    db.session.commit()
    return redirect(url_for('index'))
