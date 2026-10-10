
import os
from urllib.parse import quote_plus

from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()


def init_db(app):
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "12728")
    name = os.getenv("DB_NAME", "defaultdb")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if not all([host, user, password, name]):
        raise RuntimeError(
            "Database settings are missing. Check your .env file."
        )

    password = quote_plus(password)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "connect_args": {
            "ssl": {"ca": os.path.join(os.path.dirname(__file__), "ca.pem")}
        }
    }

    db.init_app(app)