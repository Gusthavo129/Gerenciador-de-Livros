from flask_sqlalchemy import SQLAlchemy
from jose import jwt, exceptions
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
app.config['ALGORITHM'] = 'HS256'


db = SQLAlchemy(app)


class Livros(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(80), nullable=False)
    autor = db.Column(db.String(80), nullable=False)
    categoria = db.Column(db.String(80), nullable=False)
    publicacao = db.Column(db.Integer, nullable=True)
    exemplares = db.Column(db.Integer, nullable=False)
    disponiveis = db.Column(db.Integer, nullable=False)


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
        return {"erro": "Token expirado"}
    except exceptions.JWTError as e:
        print(f"Erro ao verificar JWT: {e}")
        return {"erro": "Token inválido"}