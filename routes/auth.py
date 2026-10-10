
from flask import Blueprint, request,current_app
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from database import db
from models import Student

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    hashed_password = generate_password_hash(password)
    department = data.get("department", "").strip()
    semester = data.get("semester")

    if not name or not email or not password:
        return {
            "error": "Name, email, and password are required."
        }, 400

    if len(password) < 8:
        return {
            "error": "Password must contain at least 8 characters."
        }, 400
    
   

    try:
        student = Student(
            name=name,
            email=email,
            password=hashed_password,
            department=department or None,
            semester=int(semester) if semester not in (None, "") else None
        )

        db.session.add(student)
        db.session.commit()

        return {
            "message": "Registration successful!",
            "student": {
                "student_id": student.student_id,
                "name": student.name,
                "email": student.email
            }
        }, 201

    except ValueError:
        db.session.rollback()
        return {"error": "Semester must be a valid number."}, 400

    except IntegrityError:
        db.session.rollback()
        return {"error": "This email is already registered."}, 409

    except Exception:
        db.session.rollback()
        current_app.logger.exception("Registration failed")
        return {"error": "Registration failed. Check server logs."}, 500

    

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return {
            "error": "Email and password are required."
        }, 400

    student = Student.query.filter_by(email=email).first()

    if not student or not check_password_hash(
        student.password, password
    ):
        return {
            "error": "Invalid email or password."
        }, 401

    return {
        "message": "Login successful!",
        "student": {
            "student_id": student.student_id,
            "name": student.name,
            "email": student.email
        }
    }, 200

@auth_bp.route("/profile/<int:student_id>", methods=["GET"])
def get_profile(student_id):
    student = Student.query.get(student_id)

    if not student:
        return {"error": "Student not found."}, 404

    return {
        "student": {
            "student_id": student.student_id,
            "name": student.name,
            "email": student.email,
            "department": student.department,
            "semester": student.semester
        }
    }, 200
