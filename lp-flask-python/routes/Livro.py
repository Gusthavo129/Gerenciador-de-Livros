from flask import Flask, request, jsonify
from sqlalchemy import asc, desc
from datetime import datetime, timedelta

from app import app, db
from model import generate_jwt, verify_jwt
from model.Livro import Livros

app = Flask(__name__)


def resposta_erro(mensagem, status=400):
    return jsonify({"mensagem": mensagem}), status


def livros_to_dict(livros):
    return {
        "id": livros.id,
        "titulo": livros.titulo,
        "autor": livros.autor,
        "categoria": livros.categoria,
        "publicacao": livros.publicacao.strftime("%Y-%m-%d") if livros.publicacao else None,
        "exemplares": livros.exemplares,
        "disponiveis": livros.disponiveis,
    }


@app.route("/livros", methods=["POST"])
def adicionar_livros():
    dados = request.json

    titulo = dados.get("titulo")
    autor = dados.get("autor")
    publicacao = dados.get("publicacao")
    exemplares = dados.get("exemplares", 1)
    categoria = dados.get("categoria")

    if not titulo or not autor or not publicacao or not exemplares:
        return jsonify({"mensagem": "Título, autor, data de publicação e quantidade são obrigatórios"}), 400

    try:
        novo_livro = Livros (
            titulo= titulo,
            autor= autor,
            categoria= categoria,
            publicacao= datetime.strptime(publicacao, "%Y-%m-%d") if publicacao else None,
            exemplares= exemplares,
            disponiveis= exemplares
        )
        db.session.add(novo_livro)
        db.session.commit()

        return jsonify(novo_livro.to_dict()), 201
    except Exception as e:
        return jsonify({"mensagem": f"Erro ao adicionar livro: {str(e)}"}), 500


@app.route("/livros", methods=["GET"])
def listar_livros():
    livros = Livros.query.all()
    return jsonify([livros.to_dict() for livros in livros]), 200


@app.route("/livros/<int:id>", methods=["GET"])
def obter_livros(id):
    livros = Livros.query.get(id)

    if not livros:
        return jsonify({"mensagem": "Livro não encontrado"}), 404

    return jsonify(livros), 200


@app.route("/livros/<int:id>", methods=["PUT"])
def editar_livros(id):
    dados = request.json
    livros = Livros.query.get(id)

    if not livros:
        return jsonify({"mensagem": "Livro não encontrado"}), 404

    try:
        livros.titulo = dados.get("titulo", livros.titulo)
        livros.autor = dados.get("autor", livros.autor)
        livros.publicacao =datetime.strptime(dados.get("publicacao"), "%Y-%m-%d") if dados.get("publicacao") else livros.publicacao
        livros.exemplares = dados.get("exemplares", livros.exemplares)
        livros.categoria = dados.get("categoria", livros.categoria)


        if "exemplares" in dados and dados["exemplares"] < livros.disponiveis:
            livros.disponiveis = dados["exemplares"]

        db.session.commit()
        return jsonify(livros_to_dict(livros)), 200
    except Exception as e:
        return resposta_erro(f"Erro ao editar livro: {str(e)}", 500)


@app.route("/livros/<int:id>", methods=["DELETE"])
def remover_livros(id):
    livros = Livros.query.get(id)

    if not livros:
        return jsonify({"mensagem": "Livro não encontrado"}), 404

    try:
        db.session.delete(livros)
        db.session.commit()
        return jsonify({"mensagem": "Livro removido com sucesso"}), 200
    except Exception as e:
        return resposta_erro(f"Erro ao remover livro: {str(e)}", 500)


if __name__ == "__main__":
    app.run(debug=True)
