import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# Configurazione DB: Se siamo su K8s usa Postgres, altrimenti SQLite locale
db_path = os.path.join(os.path.dirname(__file__), 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///' + db_path)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.route('/')
def health_check():
    # Questa rotta serve a Kubernetes per capire se siamo vivi
    return jsonify({"status": "up", "service": "map-service"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
