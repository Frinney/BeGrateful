import re
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='pages')
app.secret_key = 'your_secret_key'

# строка конекта с бд, тестировалось  на MS SQL Server
app.config['SQLALCHEMY_DATABASE_URI'] = '!!connection to bd!!'  

# Инициализация SQLAlchemy для работы с базой данных
db = SQLAlchemy(app)

# Модель таблицы пользователей для аутентификации.
class User(db.Model):
    __tablename__ = 'Users'
    __table_args__ = {'schema': 'dbo'}

    UserID = db.Column(db.Integer, primary_key=True)
    UserName = db.Column(db.String(100), nullable=False)
    UserSurname = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(256), nullable=False)
    RegistrationDate = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    ProfilePicture = db.Column(db.String(255), nullable=True)
    Bio = db.Column(db.Text, nullable=True)

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)

def is_valid_password(password):
    if (len(password) < 8 or len(password) > 128):
        return False
    if not re.search(r'[A-Z]', password): 
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if re.search(r'\s', password):
        return False
    if not re.match(r'^[a-zA-Zа-яА-Я0-9~!?@#$%^&*_\-\+\(\)\[\]\{\}><\/\\|"\'.,:;]+$', password):
        return False
    return True

def is_valid_login(login):
    return re.match(r'^[a-zA-Z0-9]+$', login)

@app.route('/')
def index():
    return render_template('index.html') 

def is_valid_name(name):
    return re.match(r'^[a-zA-Zа-яА-Я]*$', name)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '')  
        last_name = request.form.get('last_name', '') 
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        profile_picture = request.form.get('profile_picture', '')
        bio = request.form.get('bio', '')

        if first_name and not is_valid_name(first_name):
            flash('Ім\'я повинно містити лише букви!')
            return redirect(url_for('register'))
        
        if last_name and not is_valid_name(last_name):
            flash('Прізвище повинно містити лише букви!')
            return redirect(url_for('register'))

        if not is_valid_login(login):
            flash('Логін повинен містити лише латинські букви та цифри, без пробілів!')
            return redirect(url_for('register'))

        if not is_valid_email(email):
            flash('Неправильний формат пошти!')
            return redirect(url_for('register'))

        if not is_valid_password(password):
            flash('Пароль не відповідає вимогам!')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Паролі не співпадають!')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(Email=email).first()
        if existing_user:
            flash('Такий користувач уже існує!')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(
            UserName=login,
            UserSurname=last_name,
            Email=email,
            PasswordHash=hashed_password,
            ProfilePicture=profile_picture,
            Bio=bio
        )
        db.session.add(new_user)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            flash('Помилка при реєстрації!')
            return redirect(url_for('register'))
        flash('Реєстрація пройшла успішно!')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        user = User.query.filter_by(UserName=login).first()
        if user and check_password_hash(user.PasswordHash, password):
            flash('Ви успішно увійшли в систему!')
            return redirect(url_for('index'))
        else:
            flash('Неправильний логін або пароль!')
            return redirect(url_for('login'))
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)