import pytest
from app import app as flask_app
from app import db

@pytest.fixture
def app():
    # Forza l'uso di un DB in memoria per i test (velocissimo)
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
