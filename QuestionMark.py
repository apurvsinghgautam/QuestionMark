from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/profile')
def profile():
    return 'Hi there'


if __name__ == '__main__':
    app.run()
