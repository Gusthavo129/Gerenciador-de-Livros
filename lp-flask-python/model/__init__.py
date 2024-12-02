from model.Emprestimo import *
from model.Livro import *
from model.Usuario import *

with app.app_context():
    db.create_all()