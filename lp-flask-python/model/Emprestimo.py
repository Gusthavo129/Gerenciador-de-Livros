from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import Flask
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emprestimos.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
db = SQLAlchemy(app)


class Emprestimo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    livro_id = db.Column(db.Integer, nullable=False)
    data_emprestimo = db.Column(db.DateTime, default=datetime.utcnow)
    data_devolucao_prevista = db.Column(db.DateTime, nullable=False)
    data_devolucao_real = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default='Ativo')

    def __repr__(self):
        return (f"<Emprestimo ID={self.id}, UsuarioID={self.usuario_id}, LivroID={self.livro_id}, "
                f"Status={self.status}, DevoluçãoPrevista={self.data_devolucao_prevista}>")

    def concluir_emprestimo(self):

        self.data_devolucao_real = datetime.utcnow()
        self.status = "Concluído"

    def is_atrasado(self):
        if not self.data_devolucao_real:
            return datetime.utcnow() > self.data_devolucao_prevista
        return False

    def validar_dados(self):
        if self.usuario_id <= 0:
            raise ValueError("O usuário ID deve ser um número positivo.")
        if self.livro_id <= 0:
            raise ValueError("O livro ID deve ser um número positivo.")
        if self.data_devolucao_prevista < self.data_emprestimo:
            raise ValueError("A data de devolução prevista deve ser após a data do empréstimo.")

    @classmethod
    def obter_emprestimos_ativos(cls):
        return cls.query.filter_by(status="Ativo").all()