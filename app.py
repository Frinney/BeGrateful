import os
import re
import asyncio

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.future import select
from sqlalchemy.orm    import selectinload

from data.tables       import init_db, BaseEngine, User, Gratitude, Friendship
from data.queries.user import register_user, get_user_id, add_gratitude, get_gratitudes

from datetime import datetime, timedelta


app = Flask(__name__, template_folder='pages')
app.secret_key = 'your_secret_key'

 
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
async def index():
    user_id = session.get('user_id')
    friends_list = await get_friends(user_id) if user_id else []
    return render_template('index.html', friends=friends_list)



@app.route('/register', methods=['GET', 'POST'])
async def register():
    errors = {}
    general_error = None

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
            general_error = 'Некоректні дані. Перевірте їх і повторіть спробу'
            return render_template('register.html', general_error=general_error, errors=errors, form=request.form)
        
        is_exist = await register_user(login, password, first_name, last_name, email)
        if is_exist:
            general_error = 'Некоректні дані. Перевірте їх і повторіть спробу'
            return render_template('register.html', general_error=general_error, errors=errors, form=request.form)

        return redirect(url_for('index'))

    return render_template('register.html', errors=errors, form=request.form)


@app.route('/login', methods=['GET', 'POST'])
async def login_view():
    errors = {}
    invalid_credentials = False 

    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        if not login:
            errors['login'] = 'Поле логина не может быть пустым'
        if not password:
            errors['password'] = 'Поле пароля не может быть пустым'

        if not errors: 
            user_id = await get_user_id(login, password)

            if user_id is not None:
                session['user_id'] = user_id

                return redirect(url_for('index'))
           
            invalid_credentials = True  
            flash('Неправильний логін або пароль!')
            return redirect(url_for('login_view'))

    return render_template('login.html', errors=errors, invalid_credentials=invalid_credentials)


@app.route('/create', methods=['GET', 'POST'])
async def create_gratitude():

    user_id = session.get('user_id')
    if not user_id:
        flash('Спершу увійдіть до системи!', 'warning')  
        return redirect(url_for('login_view'))  

    if request.method == 'POST':
        content = request.form.get('content')
        image = request.files.get('image')
        is_public = request.form.get('is_public') is not None 
        image_url = None

        if image:
            image_folder = os.path.join('static', 'images')
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)
            image_path = os.path.join(image_folder, image.filename)
            image.save(image_path)
            image_url = f'images/{image.filename}'

        await add_gratitude(
            content,
            image_url,
            is_public, 
            user_id
        )

        flash('Подяка створена!', 'success')  
        return redirect(url_for('index'))

    return render_template('index.html')  


@app.route('/global')
async def global_gratitudes():
    gratitudes = await get_gratitudes()

    return render_template('global.html', gratitudes=gratitudes)


@app.route('/edit_profile', methods=['GET', 'POST'])
async def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Спершу увійдіть до системи!')
        return redirect(url_for('login_view'))

    async with BaseEngine.async_session() as db_session:
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

                return render_template('profile.html', user=user, errors=errors, success='Зміни збережені!')

        return render_template('profile.html', user=user, errors=errors)

async def get_friends(user_id):
    friends_list = []
    async with BaseEngine.async_session() as db_session:
        try:
            result = await db_session.execute(
                select(Friendship).filter(Friendship.user_id == user_id)
            )
            friendships = result.scalars().all()

            for friendship in friendships:
                friend_result = await db_session.execute(
                    select(User).filter(User.id == friendship.friend_user_id)
                )
                friend = friend_result.scalar_one_or_none()
                if friend:
                    friends_list.append(friend)
        except Exception as e:
            print(f"Ошибка при загрузке друзей: {e}")

    return friends_list


@app.before_request
async def load_friends():
    user_id = session.get('user_id')
    if user_id:
        g.friends = await get_friends(user_id)
    else:
        g.friends = []


@app.route('/friends', methods=['GET', 'POST'])
async def friends():
    user_id = session.get('user_id')
    if not user_id:
        flash('Спершу увійдіть до системи!')
        return redirect(url_for('login_view'))

    friends_list = await get_friends(user_id)

    if request.method == 'POST':
        nickname = request.form['nickname'].strip()
        async with BaseEngine.async_session() as db_session:
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

    return render_template('friends.html', friends=friends_list)



@app.route('/profile')
async def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Спершу увійдіть до системи!')
        return redirect(url_for('login_view'))

    today = datetime.today()

    async with BaseEngine.async_session() as db_session: #edit
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

    async with BaseEngine.async_session() as db_session: #edit
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
    async with BaseEngine.async_session() as db_session: #edit
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

    async with BaseEngine.async_session() as db_session: #edit
        friendships = await db_session.execute(
            select(Friendship).filter_by(user_id=user_id)
        )
        friend_ids = [friendship.friend_user_id for friendship in friendships.scalars().all()]

        gratitudes = await db_session.execute(
            select(Gratitude).filter(Gratitude.user_id.in_(friend_ids)).filter(Gratitude.is_public == True)
            .options(selectinload(Gratitude.user))
            .order_by(Gratitude.created_at.desc())
        )
        gratitudes = gratitudes.scalars().all()

    return render_template('feed.html', gratitudes=gratitudes)

@app.route('/archive')
async def archive():
    return render_template('archive.html')

@app.route('/gratitudes/<date>', methods=['GET'])
async def gratitudes_by_date(date):
    user_id = session.get('user_id')
    if not user_id:
        flash('Спершу увійдіть до системи!')
        return redirect(url_for('login_view'))

    try:
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        flash('Неправильний формат дати! Використовуйте YYYY-MM-DD.')
        return redirect(url_for('profile'))

    async with BaseEngine.async_session() as db_session:

        gratitude_entries = await db_session.execute(
            select(Gratitude).filter_by(user_id=user_id).filter(
                Gratitude.created_at >= selected_date,
                Gratitude.created_at < selected_date + timedelta(days=1) 
            )
        )
        todays_gratitudes = gratitude_entries.scalars().all()

    return render_template('gratitudes_by_date.html', gratitudes=todays_gratitudes, selected_date=selected_date)


if __name__ == '__main__':
    asyncio.run(init_db())
    app.run(debug = True)