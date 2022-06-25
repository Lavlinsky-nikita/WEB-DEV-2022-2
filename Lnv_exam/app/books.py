from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import *

bp = Blueprint('books', __name__, url_prefix='/books')

@bp.route('/new')
def new():
    books = Book.query.all()
    return render_template('books/new.html',books=books)

@bp.route('/edit/<int:book_id>')
def edit(book_id):
    return render_template('books/edit.html')

@bp.route('/show/<int:book_id>')
def show(book_id):
    return render_template('books/show.html')

@bp.route('/<int:book_id>/delete', methods=['POST'])
def delete(book_id):
    books = Book.query.filter(id=book_id).one()
    return redirect(url_for('index'))
