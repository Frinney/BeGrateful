import os
import re
import asyncio
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import DateTime
from datetime import datetime

app = Flask(__name__, template_folder='pages')
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite+aiosqlite:///gratitudes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
engine = create_async_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    login = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    gratitudes = relationship('Gratitude', back_populates='user')

class Gratitude(db.Model):
    __tablename__ = 'gratitudes'
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    is_public = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='gratitudes')
    created_at = Column(DateTime, default=datetime.utcnow)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(db.metadata.create_all)

def is_valid_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)

def is_valid_password(password):
    if len(password) < 8 or len(password) > 128:
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

def is_valid_name(name):
    return re.match(r'^[a-zA-Zа-яА-Я]*$', name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
async def register():
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

        async with async_session() as session:
            async with session.begin():
                existing_user = await session.execute(select(User).filter_by(login=login))
                if existing_user.scalars().first() is not None:
                    flash('Такий користувач уже існує!')
                    return redirect(url_for('register'))

                hashed_password = generate_password_hash(password)
                new_user = User(first_name=first_name, last_name=last_name, login=login, email=email, password=hashed_password)
                session.add(new_user)
            await session.commit()

        flash('Реєстрація пройшла успішно!')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
async def login_view():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        async with async_session() as db_session:
            async with db_session.begin():
                user = await db_session.execute(select(User).filter_by(login=login))
                user = user.scalar_one_or_none()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Ви успішно увійшли в систему!')
            return redirect(url_for('index'))
        else:
            flash('Неправильний логін або пароль!')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/create', methods=['GET', 'POST'])
async def create_gratitude():
    if request.method == 'POST':
        content = request.form.get('content')
        image = request.files.get('image')
        user_id = session.get('user_id')

        is_public = request.form.get('is_public') is not None 

        image_url = None
        if image:
            image_folder = os.path.join('static', 'images')
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)
            image_path = os.path.join(image_folder, image.filename)
            image.save(image_path)
            image_url = f'images/{image.filename}'

        async with async_session() as db_session:
            async with db_session.begin():
                new_gratitude = Gratitude(
                    content=content,
                    image_url=image_url,
                    is_public=is_public, 
                    user_id=user_id
                )
                db_session.add(new_gratitude)
            await db_session.commit()

        flash('Подяка створена!', 'success')  
        return redirect(url_for('index'))

    return render_template('index.html')  

@app.route('/global')
async def global_gratitudes():
    async with async_session() as db_session:
        async with db_session.begin():
            gratitudes = await db_session.execute(
                select(Gratitude)
                .filter_by(is_public=True)
                .options(selectinload(Gratitude.user))
                .order_by(Gratitude.created_at.desc()) 
            )
            gratitudes = gratitudes.scalars().all()

    return render_template('global.html', gratitudes=gratitudes)

if __name__ == '__main__':
    asyncio.run(create_db())
    app.run(debug=True)
