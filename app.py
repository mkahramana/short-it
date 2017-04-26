from string import ascii_letters, digits

import re
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates', static_folder='static')

app.debug = True
app.secret_key = 'secret'
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
})
db = SQLAlchemy(app)

BASE = ascii_letters + digits
HOST = '127.0.0.1'
PORT = 5000


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(255), unique=True)
    shortenURL = db.Column(db.String(6), unique=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def form_post():
    if request.method == 'POST':
        url = request.form['link']
        if not valid_url(url):
            error = 'Unable to create short URL!'
            return render_template('index.html', error=error)
        else:
            url = discard_http(url)
            is_db = Link.query.filter_by(url=url).first()
            if not is_db:
                base_encode = encode()
                save_to_db(url, base_encode)
                shortened_url = 'http://' + HOST + ':' + str(PORT) + '/' + base_encode
                return render_template('index.html', shortened_url=shortened_url)
            else:
                encode_string = Link.query.filter_by(url=url).first().shortenedURL
                shortened_url = 'http://' + HOST + ':' + str(PORT) + '/' + encode_string
                return render_template('index.html', shortened_url=shortened_url)


@app.route('/<encode_string>')
def resolve_url(encode_string):
    if not encode_string[-1] is '+':
        decode_string = decode(encode_string)
        shorten_url = Link.query.filter_by(id=decode_string).first()
        if shorten_url is not None:
            return redirect('http://' + shorten_url.url)
        else:
            return render_template('index.html', not_exist='http://' + HOST + ':' + str(PORT) + '/' + encode_string)
    else:
        encode_string = encode_string[:-1]
        decode_string = decode(encode_string)
        original_url = Link.query.filter_by(id=decode_string).first()
        if original_url is not None:
            return render_template('index.html', original_url='http://' + original_url.url)
        else:
            return render_template('index.html', not_exist='http://' + HOST + ':' + str(PORT) + '/' + encode_string)


def valid_url(url):
    pattern = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(pattern, url)


def discard_http(url):
    pattern = r'^https?:\/\/'
    replace = re.compile(pattern)
    url = replace.sub('', url)
    return url


def save_to_db(url, shorten_url):
    is_db = Link.query.filter_by(url=url).first()
    if not is_db:
        is_db = Link(url=url, shortenURL=shorten_url)
        db.session.add(is_db)
        db.session.commit()


def to_base_62():
    number = len(Link.query.all())
    digits = []
    if number == 0:
        digits.append(0)
        return digits
    else:
        while number > 0:
            remainder = number % 62
            digits.append(remainder)
            number = int(number / 62)
        return digits[::-1]


def encode():
    return ''.join(BASE[i] for i in to_base_62())


def decode(id):
    return sum([BASE.index(value) * (62 ** key) for key, value in enumerate(id[::-1])]) + 1


if __name__ == '__main__':
    db.create_all()
    app.run(host=HOST, port=PORT)
