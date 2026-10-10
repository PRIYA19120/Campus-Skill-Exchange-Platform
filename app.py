from flask import Flask, render_template, send_from_directory, request, session, redirect, url_for
import os
import csv
import sqlite3
from flask import Flask 
from database import init_db, db
import models

from routes.auth import auth_bp
from routes.skills import skills_bp

app = Flask(__name__)



app.secret_key = "campus_skill_exchange"

UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Initialize MySQL and register API blueprints
init_db(app)

app.register_blueprint(auth_bp)
app.register_blueprint(skills_bp)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")

        session["user_name"] = username
        session["username"] = username

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

        conn = get_db()

        try:
            conn.execute(
                """
                INSERT INTO users
                (full_name, username, email, password, department, semester)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    full_name,
                    username,
                    email,
                    password,
                    department,
                    semester
                )
            )

            conn.commit()

        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="Username or email already exists."
            )

        finally:
            conn.close()

        session["user_id"] = None
        session["full_name"] = full_name
        session["username"] = username
        session["email"] = email
        session["department"] = department
        session["semester"] = semester
        session["user_name"] = full_name

        return redirect(url_for("dashboard"))

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


@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


@app.route("/my-skills", methods=["GET", "POST"])
def my_skills():

    skills = session.get("skills", [])

    if request.method == "POST":

        skill = request.form.get("skill")

        if skill and skill not in skills:
            skills.append(skill)

        session["skills"] = skills

        return redirect(url_for("my_skills"))

    return render_template(
        "my_skills.html",
        skills=skills
    )


@app.route("/remove-skill/<skill>")
def remove_skill(skill):

    skills = session.get("skills", [])

    if skill in skills:
        skills.remove(skill)

    session["skills"] = skills

    return redirect(url_for("my_skills"))


@app.route("/learn-skills")
def learn_skills():

    skills = session.get("learn_skills", [])

    dataset_path = os.path.join(
        app.root_path,
        "dataset",
        "skills_dataset.csv"
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
            item
            for item in available_skills
            if search in item["skill"].lower()
            or search in item["category"].lower()
        ]


    return render_template(
        "learn_skills.html",
        skills=skills,
        available_skills=available_skills,
        search=request.args.get("search", "").strip()
    )
@app.route("/add-learn-skill", methods=["POST"])
def add_learn_skill():

    skill = request.form.get("skill")

    skills = session.get("learn_skills", [])

    if skill and skill not in skills:
        skills.append(skill)

    session["learn_skills"] = skills

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


@app.route("/remove-learn-skill/<skill>")
def remove_learn_skill(skill):

    skills = session.get("learn_skills", [])

    if skill in skills:
        skills.remove(skill)

    session["learn_skills"] = skills

    return redirect(url_for("learn_skills"))

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


if __name__ == "__main__":
    app.run(debug=True)