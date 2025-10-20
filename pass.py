from flask import Flask, render_template, request, session, redirect, url_for, flash
import random
import string
import os

app = Flask(__name__)
app.secret_key = 'helloworld'


# Файл для хранения пользователей
USERS_FILE = 'users.txt'


def load_users():
    try:
        if os.path.exists(USERS_FILE):
            users = []
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # Формат: username,password,role
                        parts = line.split(',')
                        if len(parts) == 3:
                            users.append({
                                'username': parts[0].strip(),
                                'password': parts[1].strip(),
                                'role': parts[2].strip()
                            })
            return users
    except Exception as e:
        print(f"Ошибка при загрузке пользователей: {e}")

    # Возвращаем пользователей по умолчанию, если файла нет
    return [
        {'username': 'admin', 'password': 'admin', 'role': 'admin'},
        {'username': 'user', 'password': 'user', 'role': 'user'}
    ]


def save_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            for user in users:
                line = f"{user['username']},{user['password']},{user['role']}\n"
                f.write(line)
    except Exception as e:
        print(f"Ошибка при сохранении пользователей: {e}")


def generate_password(length=6, complexity='medium'):
    """
    Генерация случайного пароля заданной сложности

        length (int): Длина пароля (по умолчанию 6)
        complexity (str): Уровень сложности ('easy', 'medium', 'hard')

    """
    if complexity == 'easy':
        # Только буквы (строчные и прописные)
        characters = string.ascii_letters
    elif complexity == 'medium':
        # Буквы и цифры
        characters = string.ascii_letters + string.digits
    elif complexity == 'hard':
        # Буквы, цифры и специальные символы
        characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    else:
        characters = string.ascii_letters + string.digits

    # Генерация пароля
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


@app.route('/')
def index():
    """
    Главная страница генератора паролей

    Returns:
        rendered template: HTML страница с формой генерации пароля
    """
    return render_template('index.html')


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    """
    Страница генерации пароля

    Returns:
        rendered template: Страница с результатом генерации пароля
    """
    password = None
    complexity_info = None

    if request.method == 'POST':
        try:
            length = int(request.form.get('length', 6))
            complexity = request.form.get('complexity', 'medium')

            # Ограничиваем длину пароля для безопасности
            length = max(6, min(length, 12))

            password = generate_password(length, complexity)

        except ValueError:
            password = "Ошибка: введите корректную длину пароля"

    return render_template('generate.html',
                           password=password,
                           complexity_info=complexity_info)


# Декоратор для проверки аутентификации
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Пожалуйста, войдите в систему', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


# Маршруты аутентификации
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        user_found = False
        for user in users:
            if user['username'] == username and user['password'] == password:
                session['username'] = user['username']
                session['role'] = user.get('role', 'user')
                print(session)
                flash(f'Добро пожаловать, {username}!', 'success')
                user_found = True
                return redirect(url_for('profile'))

        if not user_found:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if 'username' in session:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Проверка паролей
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('registration.html')

        # Проверка длины пароля
        if len(password) < 4:
            flash('Пароль должен содержать минимум 4 символа', 'error')
            return render_template('registration.html')

        users = load_users()

        # Проверка существующего пользователя
        if any(user['username'] == username for user in users):
            flash('Пользователь с таким именем уже существует', 'error')
            return render_template('registration.html')

        # Добавление нового пользователя
        new_user = {
            'username': username,
            'password': password,
            'role': 'user'
        }
        users.append(new_user)
        save_users(users)

        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))

    return render_template('registration.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html',
                           username=session.get('username'),
                           role=session.get('role'))


@app.route('/admin')
@login_required
def admin():
    if session.get('role') != 'admin':
        flash('У вас нет прав для доступа к этой странице', 'error')
        return redirect(url_for('index'))
    return render_template('admin.html', username=session.get('username'))



def save_managerpassword(username,password,website):
    try:
        data = f"Пользователь: {username}, Пароль: {password}, Сайт: {website}\n"
        with open('managerpassword.txt', 'a', encoding='utf-8') as file:
            file.write(data)
        return True
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")
        return False

def read_managerpassword():
    managerpassword = []
    try:
        with open('managerpassword.txt', 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(', ')
                    username = parts[0].replace('Пользователь: ', '')
                    password = parts[1].replace('Пароль: ', '')
                    website = parts[2].replace('Сайт: ', '')
                    managerpassword.append({
                        'website': website,
                        'username': username,
                        'password': password
                    })
    except FileNotFoundError:
        managerpassword = ["Файл managerpassword.txt не найден"]
    except Exception as e:
        managerpassword = [f"Ошибка при чтении файла: {str(e)}"]

    return managerpassword

@app.route('/manag', methods=['GET','POST'])
def manag():
    message = None
    message_type = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        website = request.form.get('website', '').strip()

        if not all([username,password,website]):
            message = "Заполните все поля"
            message_type = 'error'
        else:
            if save_managerpassword(username, password, website):
                message = f"Данные сайта '{website}' успешно сохранены"
                message_type = 'success'

            else:
                message = "Ошибка при сохранении данных"
                message_type = 'error'

    managerpassword = read_managerpassword()

    return render_template('manag.html',
                           managerpassword=managerpassword,
                           total_count=len(managerpassword))



if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)

