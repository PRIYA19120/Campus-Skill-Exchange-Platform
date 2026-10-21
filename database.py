from urllib.parse import quote_plus

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    host = "127.0.0.1"
    port = "3306"
    name = "campus_skill_exchange"
    user = "campus_user"
    password = "Sstps"

    password = quote_plus(password)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)