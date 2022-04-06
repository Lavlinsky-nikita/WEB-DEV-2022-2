from email.mime import application
from flask import Flask

app = Flask(__name__)
application = app

@app.route('/')
def index():
    return 'Hello, world!'