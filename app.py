
from http.cookiejar import debug
import logging
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, render_template, jsonify, redirect, json

app = Flask(__name__)

if not app.debug:
    handler = RotatingFileHandler('app.json.log', maxBytes=100000, backupCount=3)
    formatter = jsonlogger.JsonFormatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

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
    app.logger.info('Main page visited', extra={'ip': request.remote_addr})
    return render_template("main_page.html")


@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form['imie']
        surname = request.form['nazwisko']
        age = request.form['wiek']
        new_user = User(name=name, surname=surname, age=age)
        db.session.add(new_user)
        db.session.commit()
        app.logger.info('Form submitted', extra={'ip': request.remote_addr})
        return redirect('/users')
    app.logger.info('Form visited', extra={'ip': request.remote_addr})
    return render_template("form.html")


@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'GET':
        app.logger.info('All users visited', extra={'ip': request.remote_addr})
        all_users = User.query.all()
        return render_template("users.html", users=all_users)
    elif request.method == 'POST':
        all_users = User.query.all()
        try:
            db.session.query(User).delete()
            db.session.commit()
            app.logger.info('DB cleaned', extra={'ip': request.remote_addr})
            return render_template("users.html", users=all_users)
        except Exception as e:
            db.session.rollback()
            app.logger.info('DB cleaning error', extra={'ip': request.remote_addr})
            return render_template("users.html", users=all_users)
@app.route('/api_users', methods=["GET"])
def api_users():
    user_id = request.args.get('id', '').strip()
    if user_id == '':
        app.logger.info('API users page visited', extra={'ip': request.remote_addr})
        return render_template('api_users.html')
    if user_id.isdigit():
        return redirect(f'/api_specific_user/{int(user_id)}')
    return "Nieprawidłowe ID", 400

@app.route('/api_specific_user/<int:user_id>', methods=["GET"])
def api_specific_user(user_id):
    app.logger.info('API specific user visited', extra={'ip': request.remote_addr})
    specific_user = User.query.get(user_id)
    if specific_user:
        app.logger.info(f'API specific user id{user_id} displayed', extra={'ip': request.remote_addr})
        return jsonify({
            "id": specific_user.id,
            "name": specific_user.name,
            "surname": specific_user.surname,
            "age": specific_user.age
        })
    else:
        app.logger.info(f'API specific user id {user_id} not found', extra={'ip': request.remote_addr})
        return jsonify({"error": "Użytkownik nie znaleziony"}), 404

@app.route('/logs', methods=["GET", "POST"])
def show_logs():
    if request.method == 'GET':
        logs = []
        try:
            with open('app.json.log', 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue  # pomiń uszkodzone linie
        except FileNotFoundError:
            app.logger.warning("Logs file does not exist", extra={'ip': request.remote_addr})

        return render_template("logs.html", logs=logs)
    elif request.method == "POST":
        logs = []
        log_path = 'app.json.log'
        try:
            open(log_path, 'w').close()
            app.logger.info('Logs cleared', extra={'ip': request.remote_addr})
        except Exception as e:
            app.logger.error('Błąd przy czyszczeniu logów: %s', str(e), extra={'ip': request.remote_addr})
        return render_template("logs.html", logs=logs)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
