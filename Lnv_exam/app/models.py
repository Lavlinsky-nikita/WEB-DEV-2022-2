from app import db


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
    name_genre = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Genre %r>' % self.name_genre