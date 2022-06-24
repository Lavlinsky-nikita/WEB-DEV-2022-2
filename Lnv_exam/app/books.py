from flask import Blueprint, render_template, redirect, url_for, flash, request


bp = Blueprint('books', __name__, url_prefix='/books')

@bp.route('/new')
def new():
    return render_template('books/new.html')

@bp.route('/edit')
def edit():
    return render_template('books/edit.html')

@bp.route('/show')
def show():
    return render_template('books/show.html')
