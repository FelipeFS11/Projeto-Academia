from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_migrate import Migrate
from flask_login import current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date)
    endereco = db.Column(db.String(150))
    contato = db.Column(db.String(50))
    password = db.Column(db.String(150), nullable=False)
    forma_pagamento = db.Column(db.String(50))
    ultimo_pagamento = db.Column(db.Date) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        contato = request.form['contato']
        data_nascimento_str = request.form['data_nascimento']
        endereco = request.form['endereco']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        try:
            data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date()
        except ValueError:
            flash('Formato de data inválido para Data de Nascimento.', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('As senhas não coincidem', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado!', 'danger')
            return redirect(url_for('register'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(first_name=first_name, last_name=last_name, email=email, contato=contato, data_nascimento=data_nascimento, endereco=endereco, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('welcome'))
        else:
            flash('Login ou senha incorretos', 'danger')
    return render_template('login.html')

@app.route('/welcome')
@login_required
def welcome():
    return render_template('welcome.html')

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

@app.route('/treino')
@login_required
def treino():
    return render_template('treino.html')

@app.route('/user')
@login_required
def user():
    return render_template('user.html')

@app.route('/infouser')
@login_required
def infouser():
    return render_template('infouser.html')

@app.route('/avaliacaofisica')
@login_required
def avaliacaofisica():
    return render_template('avaliacaofisica.html')


@app.route('/adicionarInfo', methods=['GET', 'POST'])
@login_required
def adicionarInfo():
    if request.method == 'POST':
        nome = request.form.get('nome')
        sobrenome = request.form.get('sobrenome')
        endereco = request.form.get('endereco')
        data_nascimento_str = request.form.get('data_nascimento')
        contato = request.form.get('contato')
        forma_pagamento = request.form.get('forma_pagamento')
        ultimo_pagamento_str = request.form.get('ultimo_pagamento')

        # Validando e convertendo a data de nascimento
        try:
            data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date()
        except ValueError:
            flash('Formato de data inválido para Data de Nascimento.', 'danger')
            return redirect(url_for('user'))

        # Validando e convertendo a data do último pagamento
        try:
            ultimo_pagamento = datetime.strptime(ultimo_pagamento_str, "%Y-%m-%d").date()
        except ValueError:
            flash('Formato de data inválido para Último Pagamento.', 'danger')
            return redirect(url_for('user'))

        # Atualizando o usuário no banco de dados
        current_user.first_name = nome
        current_user.last_name = sobrenome
        current_user.endereco = endereco
        current_user.data_nascimento = data_nascimento
        current_user.contato = contato
        current_user.forma_pagamento = forma_pagamento
        current_user.ultimo_pagamento = ultimo_pagamento

        # Salvando as alterações
        db.session.commit()
        flash('Informações atualizadas com sucesso!', 'success')
        return redirect(url_for('user'))

    return render_template('adicionarInfo.html', current_user=current_user)

@app.route('/alteraçãodados')
@login_required
def alteraçãodados():
    return render_template('alteraçãodados.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return "Bem-vindo Usuário"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
