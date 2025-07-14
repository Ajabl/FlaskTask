from http.cookiejar import debug

from flask_sqlalchemy import  SQLAlchemy


from flask import Flask, request, render_template

app = Flask(__name__)




app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///baza.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return f'<Uzytkownik {self.name}>'


@app.route('/')
def home():
    return render_template("main_page.html")

@app.route('/form', methods = ['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['imie']
        surname = request.form['nazwisko']
        age = request.form['wiek']
        new_user = User(name = name, surname=surname, age=age)
        db.session.add(new_user)
        db.session.commit()
        return users()
    return render_template("form.html")

@app.route('/users')
def users():
    all_users = User.query.all()
    return render_template("users.html", users=all_users)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)