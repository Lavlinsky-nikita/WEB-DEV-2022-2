from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import *

bp = Blueprint('books', __name__, url_prefix='/books')

@bp.route('/new')
def new():
    return render_template('books/new.html')

@bp.route('/edit/<int:book_id>')
def edit(book_id):
    return render_template('books/edit.html')

@bp.route('/show/<int:book_id>')
def show(book_id):
    return render_template('books/show.html')