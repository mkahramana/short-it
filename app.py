from string import ascii_letters, digits

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


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(255), unique=True)
    shortenedURL = db.Column(db.String(6), unique=True)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/', methods=['POST'])
def form_post():
    if request.method == 'POST':
        text = request.form['link']
        text = text.replace('http://', '')
        text = text.replace('https://', '')
        if not text[-1] is '+':
            is_db = Link.query.filter_by(url=text).first()
            if not is_db:
                base_encode = encode()
                save_to_db(text, base_encode)
                shortened_url = 'http://shorturldemo.com/' + base_encode
                return render_template("index.html", shortened_url=shortened_url)
            else:
                url = Link.query.filter_by(url=text).first().shortenedURL
                shortened_url = 'http://shorturldemo.com/' + url
                return render_template("index.html", shortened_url=shortened_url)
        else:
            try:
                start = text.index('/')
                url = text[start + 1:-1]
                base_decode = decode(url)
                shortened_url = Link.query.filter_by(id=base_decode).first()
                return redirect("http://" + shortened_url.url)
            except ValueError:
                return redirect('/')


def save_to_db(url, shortenedURL):
    is_db = Link.query.filter_by(url=url).first()
    if not is_db:
        is_db = Link(url=url, shortenedURL=shortenedURL)
        db.session.add(is_db)
        db.session.commit()
        return redirect('/')


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
    digits = to_base_62()
    encode_letters = ''
    for i in digits:
        encode_letters += BASE[i]
    return encode_letters


def decode(id):
    return sum([BASE.index(value) * (62 ** key) for key, value in enumerate(id[::-1])]) + 1


if __name__ == '__main__':
    db.create_all()
    app.run()
