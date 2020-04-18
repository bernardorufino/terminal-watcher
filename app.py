import os

from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])
    return 'Hello, World!'
