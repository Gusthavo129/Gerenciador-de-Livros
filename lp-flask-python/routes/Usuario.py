from flask import request, jsonify
from sqlalchemy import asc, desc
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

from app import app, db
from model import generate_jwt, verify_jwt
from model.Usuario import Usuario


@app.route('/registrar', methods=['POST'])
def registrar():
    data = request.get_json()
    if not data:
        return jsonify({"mensagem": "Requisição inválida, JSON esperado"}), 400
    if not all(k in data for k in ("nome", "email", "senha")):
        return jsonify({"mensagem": "Campos obrigatórios faltando!"}), 400

    hashed_password = generate_password_hash(data['senha'])
    new_usuario = Usuario(nome=data['nome'], email=data['email'], senha=hashed_password)

    try:
        db.session.add(new_usuario)
        db.session.commit()
        return jsonify({'id': new_usuario.id, 'nome': new_usuario.nome, 'email': new_usuario.email}), 201
    except Exception as e:
        db.session.rollback()
        if "unique constraint" in str(e).lower():
            return jsonify({"mensagem": "Usuário ou email já existe!"}), 400
        return jsonify({"mensagem": "Erro ao registrar usuário", "erro": str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"mensagem": "Requisição inválida, JSON esperado"}), 400
    if not all(k in data for k in ("nome", "senha")):
        return jsonify({"mensagem": "Campos obrigatórios faltando!"}), 400

    usuario = Usuario.query.filter_by(nome=data['nome']).first()

    if usuario and check_password_hash(usuario.senha, data['senha']):
        payload = {
            'exp': datetime.utcnow() + timedelta(minutes=30),
            'iat': datetime.utcnow(),
            'sub': str(usuario.id)
        }
        token = generate_jwt(payload)
        user_json = {'id': usuario.id, 'nome': usuario.nome, 'email': usuario.email}
        return jsonify({"token": token, "usuario": user_json}), 200

    return jsonify({"mensagem": "Nome ou senha incorretos"}), 422


@app.route("/usuarios", methods=["GET"])
def list_usuarios():
    query_params = request.args

    page = query_params.get('page', default=1, type=int)
    limit = query_params.get('limit', default=10, type=int)
    offset = (page - 1) * limit

    filters = []
    for field, value in query_params.items():
        if hasattr(Usuario, field):
            filters.append(getattr(Usuario, field) == value)

    sort_by = query_params.get('sort_by', default='id', type=str)
    sort_direction = query_params.get('sort_direction', default='asc', type=str)

    if sort_by not in Usuario.__table__.columns.keys():
        return jsonify({"mensagem": f"O campo {sort_by} não existe"}), 400

    order_by = asc(sort_by) if sort_direction == 'asc' else desc(sort_by)

    users = Usuario.query.filter(*filters).order_by(order_by).offset(offset).limit(limit).all()
    total_users = Usuario.query.filter(*filters).count()

    result = [{'id': user.id, 'nome': user.nome, 'email': user.email} for user in users]
    return jsonify({"users": result, "total": total_users, "page": page, "limit": limit}), 200


@app.route("/usuarios/<int:user_id>", methods=["DELETE"])
def deletar_Usuario(user_id):
    authorization = request.headers.get('Authorization')
    if not authorization or not authorization.startswith('Bearer '):
        return jsonify({'mensagem': "Falta o token"}), 401

    token = authorization.split(' ')[1]
    payload = verify_jwt(token)
    if not payload:
        return jsonify({'mensagem': "Token inválido ou expirado"}), 401

    user = Usuario.query.get(user_id)
    if not user:
        return jsonify({"mensagem": "Usuário não encontrado"}), 404

    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"mensagem": "Usuário deletado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensagem": "Erro no banco de dados", "erro": str(e)}), 500
