from flask import Flask, render_template, request
import random
import string

app = Flask(__name__)


def generate_password(length=6, complexity='medium'):
    """
    Генерация случайного пароля заданной сложности

    Args:
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
def generate_password_route():
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
