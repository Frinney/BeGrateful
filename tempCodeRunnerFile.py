import re
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash

app = Flask(__name__, template_folder='pages')
app.secret_key = 'your_secret_key'

users = {}

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

        if login in users:
            flash('Такий користувач уже існує!')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        users[login] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': hashed_password
        }
        flash('Реєстрація пройшла успішно!')
        return redirect(url_for('index'))

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
