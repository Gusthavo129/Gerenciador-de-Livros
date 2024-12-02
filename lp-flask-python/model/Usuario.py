from flask_sqlalchemy import SQLAlchemy
from jose import jwt, exceptions
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['ALGORITHM'] = 'HS256'


db = SQLAlchemy(app)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.nome}>'

    def set_senha(self, senha):
        self.senha = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha, senha)


def generate_jwt(payload):
    payload['exp'] = datetime.utcnow() + timedelta(hours=1)
    token = jwt.encode(
        payload,
        app.config['SECRET_KEY'],
        algorithm=app.config['ALGORITHM']
    )
    return token


def verify_jwt(token):
    try:
        payload = jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithms=[app.config['ALGORITHM']]
        )
        return payload
    except exceptions.ExpiredSignatureError:
        return {"error": "Token expirado"}
    except exceptions.JWTError as e:
        print(f"Erro ao verificar JWT: {e}")
        return None