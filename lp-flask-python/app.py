from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import dynaconf

app = Flask(__name__)
db = SQLAlchemy()
settings = dynaconf.FlaskDynaconf(
    app,
    settings_files=["settings.toml", ".secrets.toml"],
)
db.init_app(app)

import routes