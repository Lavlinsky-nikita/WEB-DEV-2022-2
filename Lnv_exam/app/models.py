import os
import sqlalchemy as sa
from flask_login import UserMixin
from app import db, app
from users_policy import UserPolicy
from werkzeug.security import check_password_hash, generate_password_hash



book_genres = db.Table('book_genres',
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True))


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_description = db.Column(db.Text, nullable=False)
    year = db.Column(db.DateTime, nullable=False)
    publishing_house = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    page_volume = db.Column(db.Integer, nullable=False)
    genres = db.relationship('Genre', secondary=book_genres,
    backref=db.backref('books'))

    def __repr__(self):
        return '<Book %r>' % self.name

class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name_genre = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return '<Genre %r>' % self.name_genre

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.String(100), primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(100), nullable=False, unique=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)

    def __repr__(self):
        return '<Image  %r>' % self.file_name

class Reviews(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    book_review = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating_sum = db.Column(db.Float, nullable=False, default=0)
    rating_num = db.Column(db.Float, nullable=False, default=0)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())
    
    @property
    def rating(self):
        if self.rating_num > 0:
            return self.rating_sum / self.rating_num
        return 0

    def __repr__(self):
        return '<Reviews %r>' % self.user

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    role = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])

    @property
    def is_admin(self):
        return app.config.get('ADMIN_ROLE_ID') == self.role

    @property
    def is_moder(self):
        return app.config.get('ADMIN_MODER_ID') == self.role

    @property
    def is_user(self):
        return app.config.get('ADMIN_USER_ID') == self.role

    def can(self, action):
        user_policy = UserPolicy()
        method = getattr(user_policy, action) 
        if method is not None:
            return method()
        return False


    def __repr__(self):
        return '<users  %r>' % self.login

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), nullable=False)
    role_description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<Role %r>' % self.role_name
