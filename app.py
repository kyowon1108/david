from flask import Flask, request, Response, render_template
import os
import socket
from io import BytesIO
from gtts import gTTS

DEFAULT_LANG = os.getenv('DEFAULT_LANG', 'ko')
app = Flask(__name__)

@app.route("/")
def home():
    if app.debug:
        hostname = '컴퓨터(인스턴스) : ' + socket.gethostname()
    else:
        hostname = ' '

    text = "Hello, DevOps"

    lang = request.args.get('lang', DEFAULT_LANG)
    fp = BytesIO()
    gTTS(text, "com", lang).write_to_fp(fp)

    return render_template('index.html', computername=hostname)

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route("/test1")
def test1():
  return render_template('test1.html')

if __name__ == '__main__':
    app.run('0.0.0.0', 80, debug=True)
