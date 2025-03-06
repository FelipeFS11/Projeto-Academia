import pytest
from datetime import date
from app import User, db, load_user
from app import app  # Importe o app para usar o contexto

@pytest.fixture
def test_app():
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

def test_create_user(test_app):
    with test_app.app_context():
        user = User(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            data_nascimento=date(1990, 1, 1),
            endereco='123 Main St',
            contato='123-456-7890',
            password='password123',
            forma_pagamento='Credit Card',
            ultimo_pagamento=date(2023, 10, 26)
        )
        db.session.add(user)
        db.session.commit()
        assert User.query.filter_by(email='john.doe@example.com').first() is not None

def test_user_attributes(test_app):
    with test_app.app_context():
        user = User(
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            password='securepassword'
        )
        db.session.add(user)
        db.session.commit()
        retrieved_user = User.query.filter_by(email='jane.smith@example.com').first()
        assert retrieved_user.first_name == 'Jane'
        assert retrieved_user.last_name == 'Smith'
        assert retrieved_user.password == 'securepassword'

def test_load_user(test_app):
    with test_app.app_context():
        user = User(email='test@example.com', password='testpassword')
        db.session.add(user)
        db.session.commit()
        loaded_user = load_user(user.id)
        assert loaded_user == user