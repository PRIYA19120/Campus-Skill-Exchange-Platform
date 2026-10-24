import os
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "12728")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if not all([host, name, user, password]):
        raise RuntimeError(
            "Please configure DB_HOST, DB_NAME, DB_USER and DB_PASSWORD."
        )

    password = quote_plus(password)
    ca_path = os.path.join(app.root_path, "ca.pem")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
        f"?ssl_ca={quote_plus(ca_path)}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)