from flask import Flask, render_template, send_from_directory, request, session, redirect, url_for
import os
import csv
import sqlite3
from flask import Flask 
from database import init_db, db
import models
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from models import Student, Skill, StudentSkill
from routes.auth import auth_bp
from routes.skills import skills_bp

app = Flask(__name__)

app.secret_key = "campus_skill_exchange"

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        # Check whether the student exists
        student = Student.query.filter_by(email=email).first()

        # Verify the password
        if not student or not check_password_hash(
            student.password, password
        ):
            return render_template(
                "login.html",
                error="Invalid email or password."
            )

        # Clear old session data
        session.clear()

        # Store logged-in student's details
        session["user_id"] = student.student_id
        session["full_name"] = student.name
        session["user_name"] = student.name
        session["username"] = student.name
        session["email"] = student.email
        session["department"] = student.department or ""
        session["semester"] = student.semester or ""

        return redirect(url_for("dashboard"))

    return render_template("login.html")




@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        department = request.form.get("department", "")
        semester = request.form.get("semester", "")

        if not all([full_name, username, email, password]):
            return render_template(
                "register.html",
                error="Please fill in all required fields."
            )

        if password != confirm_password:
            return render_template(
                "register.html",
                error="Passwords do not match."
            )

       
        try:
            existing_student = Student.query.filter(
                (Student.email == email)
            ).first()

            if existing_student:
                return render_template(
                    "register.html",
                    error="Email already exists. Please log in."
                )

            student = Student(
                name=full_name,
                email=email,
                password=generate_password_hash(password),
                department=department or None,
                semester=semester
            )

            db.session.add(student)
            db.session.commit()

            session.clear()
            session["user_id"] = student.student_id
            session["full_name"] = student.name
            session["username"] = username
            session["email"] = student.email
            session["department"] = student.department
            session["semester"] = student.semester
            session["user_name"] = student.name

            return redirect(url_for("dashboard"))

        except IntegrityError:
            db.session.rollback()
            return render_template(
                "register.html",
                error="Username or email already exists."
            )

        except Exception:
            db.session.rollback()
            app.logger.exception("Registration failed")
            return render_template(
                "register.html",
                error="Account creation failed. Check the terminal."
            )


       

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():

    user_name = session.get("user_name", "Student")

    return render_template(
        "dashboard.html",
        user_name=user_name
    )


@app.route("/profile")
def profile():

    return render_template(
        "profile.html",
        full_name=session.get("full_name", ""),
        username=session.get("username", ""),
        email=session.get("email", ""),
        department=session.get("department", ""),
        semester=session.get("semester", ""),
        bio=session.get("bio", ""),
        profile_picture=session.get("profile_picture")
    )


@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():

    if request.method == "POST":

        session["full_name"] = request.form.get("full_name")
        session["username"] = request.form.get("username")
        session["email"] = request.form.get("email")
        session["department"] = request.form.get("department")
        session["semester"] = request.form.get("semester")
        session["bio"] = request.form.get("bio")

        session["user_name"] = session["full_name"]

        photo = request.files.get("profile_picture")

        if photo and photo.filename:

            extension = os.path.splitext(photo.filename)[1]

            filename = "profile_" + str(session.get("username", "user")) + extension

            photo.save(
                os.path.join(UPLOAD_FOLDER, filename)
            )

            session["profile_picture"] = filename

        return redirect(url_for("profile"))

    return render_template(
        "edit_profile.html",
        full_name=session.get("full_name", ""),
        username=session.get("username", ""),
        email=session.get("email", ""),
        department=session.get("department", ""),
        semester=session.get("semester", ""),
        bio=session.get("bio", ""),
        profile_picture=session.get("profile_picture")
    )

@app.route("/change-password", methods=["GET", "POST"])
def change_password():

    if not session.get("user_id"):
        return redirect(url_for("login"))

    error = None
    success = None

    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        student = Student.query.filter_by(
            student_id=session["user_id"]
        ).first()

        if not student:
            return redirect(url_for("login"))

        if not check_password_hash(student.password, current_password):
            error = "Current password is incorrect."

        elif len(new_password) < 8:
            error = "New password must be at least 8 characters."

        elif new_password != confirm_password:
            error = "New passwords do not match."

        elif check_password_hash(student.password, new_password):
            error = "New password must be different from the current password."

        else:
            try:
                student.password = generate_password_hash(new_password)
                db.session.commit()
                success = "Password changed successfully."

            except Exception:
                db.session.rollback()
                app.logger.exception("Password change failed")
                error = "Could not change password. Please try again."

    return render_template(
        "change_password.html",
        error=error,
        success=success
    )



@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )

def get_student_skills(student_id, skill_type):
    records = StudentSkill.query.filter_by(
        student_id=student_id,
        skill_type=skill_type
    ).all()

    return [record.skill.skill_name for record in records]


def save_student_skill(student_id, skill_name, skill_type):
    skill_name = skill_name.strip()

    if not skill_name:
        return

    skill = Skill.query.filter(
        Skill.skill_name.ilike(skill_name)
    ).first()

    if not skill:
        skill = Skill(skill_name=skill_name)
        db.session.add(skill)
        db.session.flush()

    existing = StudentSkill.query.filter_by(
        student_id=student_id,
        skill_id=skill.skill_id,
        skill_type=skill_type
    ).first()

    if not existing:
        student_skill = StudentSkill(
            student_id=student_id,
            skill_id=skill.skill_id,
            skill_type=skill_type
        )
        db.session.add(student_skill)

    db.session.commit()

@app.route("/my-skills", methods=["GET", "POST"])
@app.route("/my-skills", methods=["GET", "POST"])
def my_skills():
    student_id = session.get("user_id")

    if not student_id:
        return redirect(url_for("login"))

    if request.method == "POST":
        skill_name = request.form.get("skill", "").strip()

        try:
            save_student_skill(student_id, skill_name, "teach")
        except Exception:
            db.session.rollback()
            app.logger.exception("Could not save teaching skill")
            return "Could not save skill. Check the terminal.", 500

        return redirect(url_for("my_skills"))

    skills = get_student_skills(student_id, "teach")

    return render_template("my_skills.html", skills=skills)


@app.route("/remove-skill/<skill>")
def remove_skill(skill):
    student_id = session.get("user_id")

    if not student_id:
        return redirect(url_for("login"))

    record = (
        StudentSkill.query
        .join(Skill)
        .filter(
            StudentSkill.student_id == student_id,
            StudentSkill.skill_type == "teach",
            Skill.skill_name == skill
        )
        .first()
    )

    if record:
        try:
            db.session.delete(record)
            db.session.commit()
        except Exception:
            db.session.rollback()
            app.logger.exception("Could not remove teaching skill")
            return "Could not remove skill. Check the terminal.", 500

    return redirect(url_for("my_skills"))


@app.route("/learn-skills")
def learn_skills():
    student_id = session.get("user_id")

    if not student_id:
        return redirect(url_for("login"))

    dataset_path = os.path.join(
        app.root_path, "dataset", "skills_dataset.csv"
    )

    available_skills = []

    with open(dataset_path, "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            skill_name = row.get("skill", "").strip()
            category_name = row.get("category", "").strip()

            if skill_name:
                available_skills.append({
                    "skill": skill_name,
                    "category": category_name
                })

    search = request.args.get("search", "").strip().lower()

    if search:
        available_skills = [
            item for item in available_skills
            if search in item["skill"].lower()
            or search in item["category"].lower()
        ]

    skills = get_student_skills(student_id, "learn")

    return render_template(
        "learn_skills.html",
        skills=skills,
        available_skills=available_skills,
        search=request.args.get("search", "").strip()
    )


@app.route("/add-learn-skill", methods=["POST"])
def add_learn_skill():
    student_id = session.get("user_id")

    if not student_id:
        return redirect(url_for("login"))

    skill_name = request.form.get("skill", "").strip()

    try:
        save_student_skill(student_id, skill_name, "learn")
    except Exception:
        db.session.rollback()
        app.logger.exception("Could not save learning skill")
        return "Could not save learning skill. Check the terminal.", 500

    return redirect(url_for("learn_skills"))


@app.route("/remove-learn-skill/<skill>")
def remove_learn_skill(skill):
    student_id = session.get("user_id")

    if not student_id:
        return redirect(url_for("login"))

    record = (
        StudentSkill.query
        .join(Skill)
        .filter(
            StudentSkill.student_id == student_id,
            StudentSkill.skill_type == "learn",
            Skill.skill_name == skill
        )
        .first()
    )

    if record:
        try:
            db.session.delete(record)
            db.session.commit()
        except Exception:
            db.session.rollback()
            app.logger.exception("Could not remove learning skill")
            return "Could not remove learning skill. Check the terminal.", 500

    return redirect(url_for("learn_skills"))



@app.route("/find-learning-partner")
def find_learning_partner():

    my_learning_skills = session.get("learn_skills", [])

    students = [
        {
            "name": "Aarav Sharma",
            "username": "aarav",
            "department": "BCA",
            "semester": "4",
            "skills": ["Python", "Java", "Data Structures"]
        },
        {
            "name": "Ananya Rawat",
            "username": "ananya",
            "department": "BCA",
            "semester": "3",
            "skills": ["HTML", "CSS", "JavaScript"]
        },
        {
            "name": "Rohan Singh",
            "username": "rohan",
            "department": "BCA",
            "semester": "5",
            "skills": ["C++", "Algorithms", "SQL"]
        }
    ]

    matching_students = []

    for student in students:

        matched_skills = [
            skill
            for skill in student["skills"]
            if skill in my_learning_skills
        ]

        if matched_skills:

            matching_students.append({
                **student,
                "matched_skills": matched_skills
            })

    return render_template(
        "find_learning_partner.html",
        students=matching_students,
        my_learning_skills=my_learning_skills
    )



@app.route("/match-result")
def match_result():
    return render_template("match_result.html")



@app.route("/images/<filename>")
def images(filename):

    return send_from_directory(
        os.path.join(app.root_path, "images"),
        filename
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))
@app.route('/skill-gap-analysis')
def skill_gap_analysis():
    return render_template('skill_gap_analysis.html')



# Initialize the MySQL database connection
init_db(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(skills_bp)


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