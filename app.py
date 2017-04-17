from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder='templates')

app.debug = True
app.secret_key = 'secret'
app.config.update({
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
})
db = SQLAlchemy(app)


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    link = db.Column(db.String(255), unique=True)
    shortedLink = db.Column(db.String(6), unique=True)


@app.route('/')
def index():
    a=Link.query.all()
    return render_template("index.html",a=a)


@app.route('/', methods=['POST'])
def form_post():
    if request.method == 'POST':
        text = request.form['link']
        save_to_db(text, '122456')
    return render_template("index.html")


def save_to_db(url, sorted_link):
    domain=Link.query.filter_by(link=url).first()
    if not domain:
        domain=Link(link=url,shortedLink=sorted_link)
        db.session.add(domain)
        db.session.commit()
        return redirect('/')


if __name__ == '__main__':
    db.create_all()
    app.run()