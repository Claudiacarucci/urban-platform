import pytest
import os
from app import app as flask_app
from app import db
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

@pytest.fixture(scope='session')
def app():
    """
    Setup Database Test.
    - CI/CD (Jenkins): Usa DATABASE_URL (Container effimero).
    - Locale: Usa DB locale '_test' per non cancellare dati veri.
    """
    jenkins_db_url = os.environ.get('DATABASE_URL')

    if jenkins_db_url:
        final_uri = jenkins_db_url
    else:
        # Config Locale
        user = os.environ.get('DB_USER', 'postgres')
        pw   = os.environ.get('DB_PASS', 'password')
        host = os.environ.get('DB_HOST', 'localhost')
        db_name = os.environ.get('DB_NAME', 'urban_platform')
        test_db_name = f"{db_name}_test"
        final_uri = f"postgresql://{user}:{pw}@{host}:5432/{test_db_name}"

        # Creazione automatica DB test locale
        if 'DATABASE_URL' not in os.environ:
            sys_uri = f"postgresql://{user}:{pw}@{host}:5432/postgres"
            engine = create_engine(sys_uri, isolation_level='AUTOCOMMIT')
            try:
                with engine.connect() as conn:
                    conn.execute(f"CREATE DATABASE {test_db_name}")
            except ProgrammingError:
                pass
            finally:
                engine.dispose()

    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": final_uri,
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
