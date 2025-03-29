from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # В реальном приложении используйте безопасный секретный ключ
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Срок жизни постоянной сессии
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)  # Срок жизни remember cookie

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.remember_cookie_duration = timedelta(days=7)  # Срок жизни remember cookie для Flask-Login

# Простой класс пользователя
class User(UserMixin):
    def __init__(self, username):
        self.id = username

# Создаем тестового пользователя
user = User('user')

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'user':
        return user
    return None

# Декоратор для проверки аутентификации
def login_required_with_redirect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Для доступа к этой странице необходимо войти в систему.')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'visits' not in session:
        session['visits'] = 0
    session['visits'] += 1
    return render_template('index.html', visits=session['visits'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if username == 'user' and password == 'qwerty':
            login_user(user, remember=remember, duration=timedelta(days=7) if remember else None)
            flash('Вы успешно вошли в систему!')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('index'))

@app.route('/secret')
@login_required_with_redirect
def secret():
    return render_template('secret.html')

if __name__ == '__main__':
    app.run(debug=True) 
