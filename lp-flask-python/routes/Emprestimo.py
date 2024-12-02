from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)


emprestimos = []

def validar_dados_emprestimo(dados):
    erros = []
    if not dados.get("usuario_id"):
        erros.append("O campo 'usuario_id' é obrigatório.")
    if not dados.get("livro_id"):
        erros.append("O campo 'livro_id' é obrigatório.")
    if not dados.get("data_devolucao_prevista"):
        erros.append("O campo 'data_devolucao_prevista' é obrigatório.")
    else:
        try:
            datetime.strptime(dados["data_devolucao_prevista"], "%Y-%m-%d")
        except ValueError:
            erros.append("A 'data_devolucao_prevista' deve estar no formato 'YYYY-MM-DD'.")
    return erros


@app.route("/emprestimos", methods=["POST"])
def criar_emprestimos():
    dados = request.json
    erros = validar_dados_emprestimo(dados)

    if erros:
        return jsonify({"erros": erros}), 400

    novo_emprestimo = {
        "id": len(emprestimos) + 1,
        "usuario_id": dados["usuario_id"],
        "livro_id": dados["livro_id"],
        "data_emprestimo": datetime.now().isoformat(),
        "data_devolucao_prevista": dados["data_devolucao_prevista"],
        "data_devolucao_real": None,
        "status": "Ativo"
    }

    emprestimos.append(novo_emprestimo)
    return jsonify(novo_emprestimo), 201


@app.route("/emprestimos", methods=["GET"])
def listar_emprestimos():
    return jsonify(emprestimos), 200


@app.route("/emprestimos/<int:id>", methods=["GET"])
def obter_emprestimo(id):
    emprestimo = next((e for e in emprestimos if e["id"] == id), None)

    if not emprestimo:
        return jsonify({"menssagem": "Empréstimo não encontrado"}), 404

    return jsonify(emprestimo), 200


@app.route("/emprestimos/<int:id>/devolver", methods=["PUT"])
def devolver_emprestimo(id):
    emprestimo = next((e for e in emprestimos if e["id"] == id), None)

    if not emprestimo:
        return jsonify({"mensagem": "Empréstimo não encontrado"}), 404

    if emprestimo["status"] == "Concluído":
        return jsonify({"mensagem": "O empréstimo já foi concluído."}), 400

    emprestimo["data_devolucao_real"] = datetime.now().isoformat()
    emprestimo["status"] = "Concluído"

    return jsonify({"mensagem": "Livro devolvido com sucesso", "emprestimo": emprestimo}), 200


@app.route("/emprestimos/<int:id>", methods=["DELETE"])
def deletar_emprestimo(id):
    global emprestimos
    emprestimo = next((e for e in emprestimos if e["id"] == id), None)

    if not emprestimo:
        return jsonify({"mensagem": "Empréstimo não encontrado"}), 404

    emprestimos = [e for e in emprestimos if e["id"] != id]
    return jsonify({"mensagem": "Empréstimo deletado com sucesso"}), 200


if __name__ == "__main__":
    app.run(debug=True)
