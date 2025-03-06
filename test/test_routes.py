import pytest
from app import app
from app import User
from datetime import date, datetime
from app import  db, bcrypt, login_manager
from app import  db, bcrypt
from flask_login import login_user, current_user
import json
#--------------------#


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<title>Pagina Inicial</title>' in response.data



@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Desabilita CSRF para testes
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_register_get(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'<title>Cadastro</title>' in response.data

def test_register_post_success(client):
    response = client.post('/register', data={
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'contato': '123456789',
        'data_nascimento': '1990-01-01',
        'endereco': 'Test Address',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Cadastro realizado com sucesso!' in response.data
    assert User.query.filter_by(email='test@example.com').first() is not None

def test_register_post_password_mismatch(client):
    response = client.post('/register', data={
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test2@example.com',
        'contato': '123456789',
        'data_nascimento': '1990-01-01',
        'endereco': 'Test Address',
        'password': 'password123',
        'confirm_password': 'password456'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'As senhas nao coincidem' in response.data
    assert User.query.filter_by(email='test2@example.com').first() is None

def test_register_post_email_exists(client):
    # Crie um usuário com o mesmo email para simular um email já existente
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(first_name='Existing', last_name='User', email='existing@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    response = client.post('/register', data={
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'existing@example.com',
        'contato': '123456789',
        'data_nascimento': '1990-01-01',
        'endereco': 'Test Address',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Email j\xc3\xa1 cadastrado!' in response.data
    assert User.query.filter_by(email='existing@example.com').count() == 1

def test_register_post_invalid_date_format(client):
    response = client.post('/register', data={
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test3@example.com',
        'contato': '123456789',
        'data_nascimento': '01-01-1990', # formato errado
        'endereco': 'Test Address',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Formato de data inv\xc3\xa1lido para Data de Nascimento.' in response.data
    assert User.query.filter_by(email='test3@example.com').first() is None

def test_login_get(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data

def test_login_post_success_admin(client):
    # Crie um usuário admin
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='teste11@gmail.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    response = client.post('/login', data={
        'email': 'teste11@gmail.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Administrador</title>' in response.data
    assert current_user.is_authenticated

def test_login_post_success_user(client):
    # Crie um usuário normal
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='user@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    response = client.post('/login', data={
        'email': 'user@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Bem-vindo</title>' in response.data
    assert current_user.is_authenticated

def test_login_post_invalid_credentials(client):
    response = client.post('/login', data={
        'email': 'invalid@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login ou senha incorretos' in response.data
    assert not current_user.is_authenticated


@pytest.fixture
def test_administrador_logged_in(client):
    # Crie um usuário admin
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='teste11@gmail.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
    with client:
        response = client.post('/login', data={
            'email': 'teste11@gmail.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Acesse a rota /administrador
        response = client.get('/administrador')
        assert response.status_code == 200
        assert b'<title>Administrador</title>' in response.data

def test_administrador_not_logged_in(client):
    response = client.get('/administrador', follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data # Verifica se redireciona para login
    assert not current_user.is_authenticated

def test_buscaCli_logged_in(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='teste11@gmail.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'teste11@gmail.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Acesse a rota /buscaCli
        response = client.get('/buscaCli')
        assert response.status_code == 200
        assert b'<title>Suas informacoes</title>' in response.data

def test_buscaCli_not_logged_in(client):
    response = client.get('/buscaCli', follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data # Verifica se redireciona para login
    assert not current_user.is_authenticated

###---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------###
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Desabilita CSRF para testes
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_alteraCli_get_logged_in(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='user@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'user@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Acesse a rota /alteraCli (GET)
        response = client.get('/alteraCli')
        assert response.status_code == 200
        assert b'<title>Suas informacoes</title>' in response.data

def test_alteraCli_get_not_logged_in(client):
    response = client.get('/alteraCli', follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data # Verifica se redireciona para login
    assert not current_user.is_authenticated

def test_alteraCli_post_success(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(first_name='Test', last_name='User', email='test@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Faça a requisição POST para /alteraCli
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'endereco': 'New Address',
            'data_nascimento': '1990-01-01',
            'forma_pagamento': 'Credit Card',
            'dias_treino': 'Segunda, Quarta, Sexta'
        }
        response = client.post('/alteraCli', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        assert json.loads(response.data)['message'] == 'Usuário atualizado com sucesso!'

        # Verifique se o usuário foi atualizado no banco de dados
        updated_user = User.query.filter_by(email='test@example.com').first()
        assert updated_user.endereco == 'New Address'
        assert updated_user.data_nascimento == date(1990, 1, 1)



def test_alteraCli_post_invalid_date(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(first_name='Test', last_name='User', email='test@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Faça a requisição POST para /alteraCli com data inválida
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'endereco': 'New Address',
            'data_nascimento': '01-01-1990', # data inválida
            'forma_pagamento': 'Credit Card',
            'dias_treino': 'Segunda, Quarta, Sexta'
        }
        response = client.post('/alteraCli', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 400
        assert json.loads(response.data)['error'] == 'Formato de data inválido para Data de Nascimento.'
    
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Desabilita CSRF para testes
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_welcome_logged_in(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='user@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'user@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Acesse a rota /welcome
        response = client.get('/welcome')
        assert response.status_code == 200
        assert b'<title>Bem-vindo</title>' in response.data

def test_welcome_not_logged_in(client):
    response = client.get('/welcome', follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data # Verifica se redireciona para login
    assert not current_user.is_authenticated

def test_chat_logged_in(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='user@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'user@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Acesse a rota /chat
        response = client.get('/chat')
        assert response.status_code == 200
        assert b'<h2>Fale com um Personal</h2>' in response.data

def test_chat_not_logged_in(client):
    response = client.get('/chat', follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data # Verifica se redireciona para login
    assert not current_user.is_authenticated

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Desabilita CSRF para testes
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_treino_logged_in(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='user@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'user@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Acesse a rota /treino
        response = client.get('/treino')
        assert response.status_code == 200
        assert b'<title>Treinos da Semana</title>' in response.data

def test_treino_not_logged_in(client):
    response = client.get('/treino', follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data # Verifica se redireciona para login
    assert not current_user.is_authenticated

def test_user_logged_in(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='user@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'user@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Acesse a rota /user
        response = client.get('/user')
        assert response.status_code == 200
        assert b'<button class="btn btn-4 btn-sep icon-info">Alterar Ou Adicionar</button>' in response.data

def test_user_not_logged_in(client):
    response = client.get('/user', follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data # Verifica se redireciona para login
    assert not current_user.is_authenticated

def test_infouser_logged_in(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='user@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'user@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Acesse a rota /infouser
        response = client.get('/infouser')
        assert response.status_code == 200
        assert b'<div class="tabela_info">' in response.data

def test_infouser_not_logged_in(client):
    response = client.get('/infouser', follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data # Verifica se redireciona para login
    assert not current_user.is_authenticated


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Desabilita CSRF para testes
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_buscar_usuario_logged_in_success(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(first_name='Test', last_name='User', email='test@example.com', password=hashed_password, endereco='Test Address',  forma_pagamento='Credit Card', dias_treino='Segunda, Quarta, Sexta')
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        #assert current_user.is_authenticated

        # Faça a requisição GET para /buscar_usuario com nome
        response = client.get('/buscar_usuario?nome=Test')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['first_name'] == 'Test'
        assert data['last_name'] == 'User'
        assert data['endereco'] == 'Test Address'
        assert data['forma_pagamento'] == 'Credit Card'
        assert data['dias_treino'] == 'Dias de Treino não cadastrados'


def test_buscar_usuario_not_logged_in(client):
    response = client.get('/buscar_usuario?nome=Test', follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data # Verifica se redireciona para login
    assert not current_user.is_authenticated

@pytest.fixture
def test_alteraCli_get_logged_in(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='user@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'user@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Acesse a rota /alteraCli (GET)
        response = client.get('/alteraCli')
        assert response.status_code == 200
        assert b'<title>Suas informacoes</title>' in response.data

def test_alteraCli_get_not_logged_in(client):
    response = client.get('/alteraCli', follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data # Verifica se redireciona para login
    assert not current_user.is_authenticated

def test_alteraCli_post_success(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(first_name='Test', last_name='User', email='test@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Faça a requisição POST para /alteraCli
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'endereco': 'New Address',
            'data_nascimento': '1990-01-01',
            'forma_pagamento': 'Credit Card',
            'dias_treino': 'Segunda, Quarta, Sexta'
        }
        response = client.post('/alteraCli', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 200
        assert json.loads(response.data)['message'] == 'Usuário atualizado com sucesso!'

        # Verifique se o usuário foi atualizado no banco de dados
        updated_user = User.query.filter_by(email='test@example.com').first()
        assert updated_user.endereco == 'New Address'
        assert updated_user.data_nascimento == date(1990, 1, 1)

def test_alteraCli_post_invalid_date(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(first_name='Test', last_name='User', email='test@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        #assert current_user.is_authenticated

        # Faça a requisição POST para /alteraCli com data inválida
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'endereco': 'New Address',
            'data_nascimento': '01-01-1990', # data inválida
            'forma_pagamento': 'Credit Card',
            'dias_treino': 'Segunda, Quarta, Sexta'
        }
        response = client.post('/alteraCli', data=json.dumps(data), content_type='application/json')
        assert response.status_code == 400
        assert json.loads(response.data)['error'] == 'Formato de data inválido para Data de Nascimento.'

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Desabilita CSRF para testes
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_adicionarInfo_get_logged_in(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='user@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'user@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Acesse a rota /adicionarInfo (GET)
        response = client.get('/adicionarInfo')
        assert response.status_code == 200
        assert b'<legend>Dados Pessoais</legend>' in response.data

def test_adicionarInfo_get_not_logged_in(client):
    response = client.get('/adicionarInfo', follow_redirects=True)
    assert response.status_code == 200
    assert b'<title>Login</title>' in response.data # Verifica se redireciona para login
    assert not current_user.is_authenticated

def test_adicionarInfo_post_success(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='test@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Faça a requisição POST para /adicionarInfo
        response = client.post('/adicionarInfo', data={
            'nome': 'Test',
            'sobrenome': 'User',
            'endereco': 'New Address',
            'data_nascimento': '1990-01-01',
            'contato': '123456789',
            'forma_pagamento': 'Credit Card',
            'ultimo_pagamento': '2023-10-26'
        }, follow_redirects=True)
        assert response.status_code == 200

        # Verifique se o usuário foi atualizado no banco de dados
        updated_user = User.query.filter_by(email='test@example.com').first()
        assert updated_user.first_name == 'Test'
        assert updated_user.last_name == 'User'
        assert updated_user.endereco == 'New Address'
        assert updated_user.data_nascimento == date(1990, 1, 1)
        assert updated_user.ultimo_pagamento == date(2023, 10, 26)

def test_adicionarInfo_post_invalid_date_nascimento(client):
    # Crie um usuário
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
        user = User(email='test@example.com', password=hashed_password)
        db.session.add(user)
        db.session.commit()

    # Faça login
        response = client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        assert current_user.is_authenticated

        # Faça a requisição POST para /adicionarInfo com data de nascimento inválida
        response = client.post('/adicionarInfo', data={
            'nome': 'Test',
            'sobrenome': 'User',
            'endereco': 'New Address',
            'data_nascimento': '01-01-1990', # data inválida
            'contato': '123456789',
            'forma_pagamento': 'Credit Card',
            'ultimo_pagamento': '2023-10-26'
        }, follow_redirects=True)
        assert response.status_code == 200
