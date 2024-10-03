import os
import re
import asyncio
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
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

class Friendship(db.Model):
    __tablename__ = 'friendships'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    friend_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', foreign_keys=[user_id], backref='friends')
    friend = relationship('User', foreign_keys=[friend_user_id], backref='friend_of')


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
    errors = {}

    if request.method == 'POST':
        first_name = request.form.get('first_name', '')  
        last_name = request.form.get('last_name', '') 
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if first_name and not is_valid_name(first_name):
            errors['first_name'] = 'Ім\'я повинно містити лише букви!'
        
        if last_name and not is_valid_name(last_name):
            errors['last_name'] = 'Прізвище повинно містити лише букви!'
        
        if not is_valid_login(login):
            errors['login'] = 'Логін повинен містити лише латинські букви та цифри, без пробілів!'
        
        if not is_valid_email(email):
            errors['email'] = 'Неправильний формат пошти!'
        
        if not is_valid_password(password):
            errors['password'] = 'Пароль не відповідає вимогам!'
        
        if password != confirm_password:
            errors['confirm_password'] = 'Паролі не співпадають!'

        if errors:
            return render_template('register.html', errors=errors, form=request.form)

        async with async_session() as session:
            async with session.begin():
                existing_user = await session.execute(select(User).filter_by(login=login))
                if existing_user.scalars().first() is not None:
                    errors['login'] = 'Такий користувач уже існує!'
                    return render_template('register.html', errors=errors, form=request.form)

                hashed_password = generate_password_hash(password)
                new_user = User(first_name=first_name, last_name=last_name, login=login, email=email, password=hashed_password)
                session.add(new_user)
            await session.commit()

        flash('Реєстрація пройшла успішно!')
        return redirect(url_for('index'))

    return render_template('register.html', errors=errors)

@app.route('/login', methods=['GET', 'POST'])
async def login_view():
    errors = {}  # Создаем словарь для ошибок

    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        # Проверка на наличие данных
        if not login:
            errors['login'] = 'Поле логина не может быть пустым'
        if not password:
            errors['password'] = 'Поле пароля не может быть пустым'

        if not errors:  # Если нет ошибок, продолжаем проверку пользователя
            async with async_session() as db_session:
                async with db_session.begin():
                    user = await db_session.execute(select(User).filter_by(login=login))
                    user = user.scalar_one_or_none()

            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash('Ви успішно увійшли в систему!')
                return redirect(url_for('index'))
            else:
                errors['login'] = 'Неправильний логін або пароль!'

    # Если есть ошибки или метод GET
    return render_template('login.html', errors=errors)

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


@app.route('/edit_profile', methods=['GET', 'POST'])
async def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Спершу увійдіть до системи!')
        return redirect(url_for('login_view'))

    async with async_session() as db_session:

        user = await db_session.execute(select(User).filter_by(id=user_id))
        user = user.scalar_one_or_none()

        if not user:
            flash('Користувач не знайдений!')
            return redirect(url_for('index'))

        errors = {}
        if request.method == 'POST':
            current_password = request.form['current_password']
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            login = request.form.get('login', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()

            if not check_password_hash(user.password, current_password):
                errors['current_password'] = 'Неправильний поточний пароль!'

            if first_name and not is_valid_name(first_name):
                errors['first_name'] = 'Ім\'я повинно містити лише букви!'
            if last_name and not is_valid_name(last_name):
                errors['last_name'] = 'Прізвище повинно містити лише букви!'

            if not is_valid_login(login):
                errors['login'] = 'Логін повинен містити лише латинські букви та цифри, без пробілів!'
            else:
                existing_user = await db_session.execute(select(User).filter_by(login=login))
                existing_user = existing_user.scalar_one_or_none()
                if existing_user and existing_user.id != user.id:
                    errors['login'] = 'Такий логін уже використовується!'

            if not is_valid_email(email):
                errors['email'] = 'Неправильний формат пошти!'
            else:
                existing_user = await db_session.execute(select(User).filter_by(email=email))
                existing_user = existing_user.scalar_one_or_none()
                if existing_user and existing_user.id != user.id:
                    errors['email'] = 'Ця пошта вже використовується іншим користувачем!'

            if password:
                if not is_valid_password(password):
                    errors['password'] = 'Пароль не відповідає вимогам!'
                if password != confirm_password:
                    errors['confirm_password'] = 'Паролі не співпадають!'

            if not errors:
                user.first_name = first_name or user.first_name
                user.last_name = last_name or user.last_name
                user.login = login or user.login
                user.email = email or user.email
                if password:
                    user.password = generate_password_hash(password)

                db_session.add(user)
                await db_session.commit()

                flash('Зміни збережені!')
                return redirect(url_for('index'))

        return render_template('edit_profile.html', user=user, errors=errors)

@app.route('/friends', methods=['GET', 'POST'])
async def friends():
    user_id = session.get('user_id')
    if not user_id:
        flash('Спершу увійдіть до системи!')
        return redirect(url_for('login_view'))

    if request.method == 'POST':
        nickname = request.form['nickname'].strip()
        async with async_session() as db_session:
            try:
                result = await db_session.execute(select(User).filter_by(login=nickname))
                friend = result.scalar_one_or_none()

                if friend:
                    if friend.id == user_id:
                        return redirect(url_for('user_profile', user_id=user_id))
                    else:
                        return redirect(url_for('user_profile', user_id=friend.id))
                else:
                    flash('Користувача не знайдено!')
            except Exception as e:
                flash('Виникла помилка при пошуку користувача.')

    return render_template('friends.html')

@app.route('/profile')
async def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Спершу увійдіть до системи!')
        return redirect(url_for('login_view'))

    today = datetime.utcnow().date() 
    async with async_session() as db_session:
        user_result = await db_session.execute(select(User).filter_by(id=user_id))
        user = user_result.scalar_one_or_none()

        if user is None:
            flash('Користувача не знайдено!')
            return redirect(url_for('index'))

        gratitude_entries = await db_session.execute(
            select(Gratitude).filter_by(user_id=user_id).filter(Gratitude.created_at >= today)
        )
        todays_gratitudes = gratitude_entries.scalars().all()

    return render_template('profile.html', user=user, todays_gratitudes=todays_gratitudes)



@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
async def user_profile(user_id):
    current_user_id = session.get('user_id')
    if not current_user_id:
        flash('Спершу увійдіть до системи!')
        return redirect(url_for('login_view'))

    async with async_session() as db_session:
        user = await db_session.execute(select(User).filter_by(id=user_id))
        user = user.scalar_one_or_none()

        if user is None:
            flash('Користувача не знайдено!')
            return redirect(url_for('feed')) 

        if request.method == 'POST':

            if current_user_id == user.id:
                flash('Ви не можете додати себе в друзі!')
            else:
                existing_friendship = await db_session.execute(
                    select(Friendship).filter_by(user_id=current_user_id, friend_user_id=user.id)
                )
                if not existing_friendship.scalar_one_or_none():
                    new_friendship = Friendship(user_id=current_user_id, friend_user_id=user.id)
                    db_session.add(new_friendship)
                    await db_session.commit()
                    flash('Користувача додано до друзів!')
                else:
                    flash('Користувач вже є у вашому списку друзів!')


        gratitudes = await db_session.execute(
            select(Gratitude).options(selectinload(Gratitude.user)).filter_by(user_id=user_id)
        )
        gratitudes = gratitudes.scalars().all()

    return render_template('user_profile.html', user=user, gratitudes=gratitudes)

@app.route('/search_users')
async def search_users():
    query = request.args.get('query', '').strip()
    async with async_session() as db_session:
        results = await db_session.execute(
            select(User).filter(User.login.ilike(f'%{query}%'))
        )
        users = results.scalars().all()
        
    return jsonify([{'id': user.id, 'login': user.login} for user in users])

@app.route('/feed')
async def feed():
    user_id = session.get('user_id')
    if not user_id:
        flash('Спершу увійдіть до системи!')
        return redirect(url_for('login_view'))

    async with async_session() as db_session:
        # Fetch friends' IDs
        friendships = await db_session.execute(
            select(Friendship).filter_by(user_id=user_id)
        )
        friend_ids = [friendship.friend_user_id for friendship in friendships.scalars().all()]

        # Fetch gratitudes from friends
        gratitudes = await db_session.execute(
            select(Gratitude).filter(Gratitude.user_id.in_(friend_ids)).filter(Gratitude.is_public == True)
            .options(selectinload(Gratitude.user))
            .order_by(Gratitude.created_at.desc())
        )
        gratitudes = gratitudes.scalars().all()

    return render_template('feed.html', gratitudes=gratitudes)


if __name__ == '__main__':
    asyncio.run(create_db())
    app.run(debug=True)
