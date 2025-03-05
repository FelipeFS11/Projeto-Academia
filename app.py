from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, request
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
            if user.email == 'teste11@gmail.com':
                return redirect(url_for('administrador'))
            else:
                return redirect(url_for('welcome'))
        else:
            flash('Login ou senha incorretos', 'danger')
    return render_template('login.html')

@app.route('/administrador')
@login_required
def administrador():
    return render_template('administrador.html')

@app.route('/buscaCli')
@login_required
def buscaCli():
    return render_template('buscaCli.html')

@app.route('/alteraCli', methods=['GET'])
@login_required
def alteraCli_get():
    return render_template('alteraCli.html', current_user=current_user)

@app.route('/alteraCli', methods=['POST'])
@login_required
def alteraCli():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Dados não fornecidos"}), 400

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    endereco = data.get('endereco')
    data_nascimento_str = data.get('data_nascimento')
    forma_pagamento = data.get('forma_pagamento')
    dias_treino = data.get('dias_treino')

    if not first_name or not last_name:
        return jsonify({"error": "Nome e sobrenome são obrigatórios"}), 400

    usuario = User.query.filter_by(first_name=first_name, last_name=last_name).first()

    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    # Validando e convertendo a data de nascimento
    try:
        data_nascimento = datetime.strptime(data_nascimento_str, "%Y-%m-%d").date() if data_nascimento_str else None
    except ValueError:
        return jsonify({"error": "Formato de data inválido para Data de Nascimento."}), 400

    try:   
        # Atualizando o usuário no banco de dados
        usuario.endereco = endereco
        usuario.data_nascimento = data_nascimento
        usuario.forma_pagamento = forma_pagamento
        usuario.dias_treino = dias_treino
    
        db.session.commit()
        return jsonify({"message": "Usuário atualizado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao atualizar usuário: {str(e)}"}), 500

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

from flask import jsonify

@app.route('/buscar_usuario')
@login_required
def buscar_usuario():
    nome = request.args.get('nome')

    if not nome:
        return jsonify({"error": "Nome não fornecido"}), 400
    
    usuario = User.query.filter(
        (User.first_name.ilike(f"%{nome}%")) | 
        (User.last_name.ilike(f"%{nome}%"))
    ).first()
    
    if not usuario:
        return jsonify({"error": "Usuário não encontrado"}), 404

    return jsonify({
        "first_name": usuario.first_name,
        "last_name": usuario.last_name,
        "endereco": usuario.endereco if usuario.endereco else "Não informado",
        "data_nascimento": usuario.data_nascimento.strftime('%Y-%m-%d') if usuario.data_nascimento else "Não informado",
        "forma_pagamento": usuario.forma_pagamento if usuario.forma_pagamento else "Não informado",
        "dias_treino": "Dias de Treino não cadastrados"
    })

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
