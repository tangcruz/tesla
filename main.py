from flask import Flask
import telegram

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/version')
def version():
    return f'python-telegram-bot version: {telegram.__version__}'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)