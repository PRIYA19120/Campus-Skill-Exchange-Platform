
from flask import Flask 
from database import init_db, db
import models
from routes.auth import auth_bp

app = Flask(__name__)

# Initialize the MySQL database connection
init_db(app)


app.register_blueprint(auth_bp)

@app.route("/")
def home():
    return "Campus Skill Exchange Backend is running!"


@app.route("/test-db")
def test_db():
    try:
        with db.engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")

        return {"message": "MySQL database connected successfully!"}, 200

    except Exception as e:
        app.logger.exception("Database connection failed")
        return {"error": "Database connection failed. Check server logs."}, 500


@app.route("/create-tables")
def create_tables():
    try:
        with app.app_context():
            db.create_all()
        return {"message": "All database tables created successfully!"}, 200
    except Exception:
        app.logger.exception("Table creation failed")
        return {"error": "Table creation failed. Check server logs."}, 500

if __name__ == "__main__":
    app.run(debug=True)