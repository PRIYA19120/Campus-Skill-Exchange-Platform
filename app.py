
from flask import (
    Flask,
    render_template,
    send_from_directory,
    request,
    session,
    redirect,
    url_for,
    flash
)
import os
import csv
from datetime import datetime

from database import init_db, db
import models

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from models import (
    Student,
    Skill,
    StudentSkill,
    Availability,
    LearningRequest
)

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

        student = Student.query.filter_by(email=email).first()

        if not student or not check_password_hash(
            student.password, password
        ):
            return render_template(
                "login.html",
                error="Invalid email or password."
            )

        session.clear()
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
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        department = request.form.get("department", "").strip()
        semester = request.form.get("semester", "").strip()

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
            existing_student = Student.query.filter_by(
                email=email
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
                semester=semester or None
            )

            db.session.add(student)
            db.session.commit()

            session.clear()
            session["user_id"] = student.student_id
            session["full_name"] = student.name
            session["username"] = username
            session["email"] = student.email
            session["department"] = student.department or ""
            session["semester"] = student.semester or ""
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
    if not session.get("user_id"):
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name", "Student")
    )


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    student = db.session.get(Student, session["user_id"])

    if not student:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "profile.html",
        full_name=student.name,
        username=session.get("username", student.name),
        email=student.email,
        department=student.department or "",
        semester=student.semester or "",
        bio=student.bio or "",
        profile_picture=session.get("profile_picture")
    )


@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    student = db.session.get(Student, session["user_id"])

    if not student:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not full_name or not email:
            return render_template(
                "edit_profile.html",
                full_name=student.name,
                username=session.get("username", student.name),
                email=student.email,
                department=student.department or "",
                semester=student.semester or "",
                bio=student.bio or "",
                profile_picture=session.get("profile_picture"),
                error="Name and email are required."
            )

        duplicate_email = Student.query.filter(
            Student.email == email,
            Student.student_id != student.student_id
        ).first()

        if duplicate_email:
            return render_template(
                "edit_profile.html",
                full_name=student.name,
                username=session.get("username", student.name),
                email=student.email,
                department=student.department or "",
                semester=student.semester or "",
                bio=student.bio or "",
                profile_picture=session.get("profile_picture"),
                error="This email is already in use."
            )

        try:
            student.name = full_name
            student.email = email
            student.department = (
                request.form.get("department", "").strip() or None
            )
            student.semester = (
                request.form.get("semester", "").strip() or None
            )
            student.bio = request.form.get("bio", "").strip() or None

            photo = request.files.get("profile_picture")

            if photo and photo.filename:
                extension = os.path.splitext(photo.filename)[1]
                filename = f"profile_{student.student_id}{extension}"
                photo.save(os.path.join(UPLOAD_FOLDER, filename))
                session["profile_picture"] = filename

            db.session.commit()

            session["full_name"] = student.name
            session["user_name"] = student.name
            session["email"] = student.email
            session["department"] = student.department or ""
            session["semester"] = student.semester or ""

            return redirect(url_for("profile"))

        except Exception:
            db.session.rollback()
            app.logger.exception("Profile update failed")

            return render_template(
                "edit_profile.html",
                full_name=student.name,
                username=session.get("username", student.name),
                email=student.email,
                department=student.department or "",
                semester=student.semester or "",
                bio=student.bio or "",
                profile_picture=session.get("profile_picture"),
                error="Could not update profile. Check the terminal."
            )

    return render_template(
        "edit_profile.html",
        full_name=student.name,
        username=session.get("username", student.name),
        email=student.email,
        department=student.department or "",
        semester=student.semester or "",
        bio=student.bio or "",
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

        student = db.session.get(Student, session["user_id"])

        if not student:
            session.clear()
            return redirect(url_for("login"))

        if not check_password_hash(student.password, current_password):
            error = "Your current password is incorrect."
        elif len(new_password) < 8:
            error = "New password must contain at least 8 characters."
        elif new_password != confirm_password:
            error = "New password and confirm password do not match."
        elif check_password_hash(student.password, new_password):
            error = (
                "Please choose a password different from your current password."
            )
        else:
            try:
                student.password = generate_password_hash(new_password)
                db.session.commit()
                success = "Password changed successfully!"
            except Exception:
                db.session.rollback()
                app.logger.exception("Password change failed")
                error = "Unable to change password. Please try again."

    return render_template(
        "change_password.html",
        error=error,
        success=success
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


def get_student_skills(student_id, skill_type):
    records = StudentSkill.query.filter_by(
        student_id=student_id,
        skill_type=skill_type
    ).all()

    return [
        record.skill.skill_name
        for record in records
        if record.skill
    ]


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
        db.session.add(
            StudentSkill(
                student_id=student_id,
                skill_id=skill.skill_id,
                skill_type=skill_type
            )
        )

    db.session.commit()


@app.route("/my-skills", methods=["GET", "POST"])
def my_skills():
    student_id = session.get("user_id")

    if not student_id:
        return redirect(url_for("login"))

    if request.method == "POST":
        skill_name = request.form.get("skill", "").strip()

        try:
            save_student_skill(student_id, skill_name, "teach")
            flash("Teaching skill saved successfully.", "success")
        except Exception:
            db.session.rollback()
            app.logger.exception("Could not save teaching skill")
            flash("Could not save skill. Please try again.", "error")

        return redirect(url_for("my_skills"))

    return render_template(
        "my_skills.html",
        skills=get_student_skills(student_id, "teach")
    )


@app.route("/remove-skill/<skill>", methods=["GET", "POST"])
def remove_skill(skill):
    student_id = session.get("user_id")

    if not student_id:
        return redirect(url_for("login"))

    record = (
        StudentSkill.query.join(Skill)
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
        app.root_path,
        "dataset",
        "skills_dataset.csv"
    )

    available_skills = []

    try:
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

    except FileNotFoundError:
        app.logger.warning("Skills dataset not found: %s", dataset_path)

    search = request.args.get("search", "").strip().lower()

    if search:
        available_skills = [
            item for item in available_skills
            if search in item["skill"].lower()
            or search in item["category"].lower()
        ]

    return render_template(
        "learn_skills.html",
        skills=get_student_skills(student_id, "learn"),
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
        flash("Learning goal saved successfully.", "success")
    except Exception:
        db.session.rollback()
        app.logger.exception("Could not save learning skill")
        flash("Could not save learning goal. Please try again.", "error")

    return redirect(url_for("learn_skills"))


@app.route("/remove-learn-skill/<skill>", methods=["GET", "POST"])
def remove_learn_skill(skill):
    student_id = session.get("user_id")

    if not student_id:
        return redirect(url_for("login"))

    record = (
        StudentSkill.query.join(Skill)
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
            return "Could not remove learning skill. Check terminal.", 500

    return redirect(url_for("learn_skills"))


def get_common_availability(student_id, partner_id):
    """Return overlapping availability periods for two students."""
    my_slots = Availability.query.filter_by(
        student_id=student_id
    ).all()

    partner_slots = Availability.query.filter_by(
        student_id=partner_id
    ).all()

    common_slots = []
    seen = set()

    for my_slot in my_slots:
        for partner_slot in partner_slots:
            if my_slot.day_of_week.strip().lower() != (
                partner_slot.day_of_week.strip().lower()
            ):
                continue

            overlap_start = max(
                my_slot.start_time,
                partner_slot.start_time
            )
            overlap_end = min(
                my_slot.end_time,
                partner_slot.end_time
            )

            if overlap_start < overlap_end:
                day = my_slot.day_of_week.title()
                start_text = overlap_start.strftime("%I:%M %p")
                end_text = overlap_end.strftime("%I:%M %p")

                key = (day, start_text, end_text)

                if key not in seen:
                    seen.add(key)
                    common_slots.append({
                        "day": day,
                        "start": start_text,
                        "end": end_text,
                        "label": (
                            f"{day}: {start_text} - {end_text}"
                        )
                    })

    return common_slots


@app.route("/find-learning-partner")
def find_learning_partner():
    student_id = session.get("user_id")

    if not student_id:
        return redirect(url_for("login"))

    my_learning_records = StudentSkill.query.filter_by(
        student_id=student_id,
        skill_type="learn"
    ).all()

    my_learning_skill_ids = {
        record.skill_id for record in my_learning_records
    }

    my_learning_skills = [
        record.skill.skill_name
        for record in my_learning_records
        if record.skill
    ]

    matching_students = []

    if my_learning_skill_ids:
        teaching_records = (
            StudentSkill.query
            .filter(
                StudentSkill.skill_type == "teach",
                StudentSkill.skill_id.in_(my_learning_skill_ids),
                StudentSkill.student_id != student_id
            )
            .all()
        )

        partner_skill_map = {}

        for record in teaching_records:
            if not record.student or not record.skill:
                continue

            partner_id = record.student_id

            if partner_id not in partner_skill_map:
                partner_skill_map[partner_id] = {
                    "student": record.student,
                    "skills": {}
                }

            partner_skill_map[partner_id]["skills"][
                record.skill_id
            ] = record.skill

        for partner_id, data in partner_skill_map.items():
            partner = data["student"]
            matched_skills = list(data["skills"].values())

            matched_skill_items = []

            for skill in matched_skills:
                matched_skill_items.append({
                    "skill_id": skill.skill_id,
                    "skill_name": skill.skill_name
                })

            common_slots = get_common_availability(
                student_id,
                partner_id
            )

            matching_students.append({
                "student_id": partner.student_id,
                "name": partner.name,
                "username": partner.email.split("@")[0],
                "department": partner.department or "Not specified",
                "semester": partner.semester or "Not specified",
                "matched_skills": matched_skill_items,
                "common_availability": common_slots
            })

        matching_students.sort(
            key=lambda item: (
                -len(item["matched_skills"]),
                item["name"].lower()
            )
        )

    return render_template(
        "find_learning_partner.html",
        students=matching_students,
        my_learning_skills=my_learning_skills
    )


@app.route(
    "/send-learning-request/<int:partner_id>/<int:skill_id>",
    methods=["POST"]
)
def send_learning_request(partner_id, skill_id):
    student_id = session.get("user_id")

    if not student_id:
        return redirect(url_for("login"))

    if partner_id == student_id:
        flash("You cannot send a request to yourself.", "error")
        return redirect(url_for("find_learning_partner"))

    partner = db.session.get(Student, partner_id)
    skill = db.session.get(Skill, skill_id)

    if not partner or not skill:
        flash("Student or skill was not found.", "error")
        return redirect(url_for("find_learning_partner"))

    # The requester must have this skill in their learning goals.
    wants_to_learn = StudentSkill.query.filter_by(
        student_id=student_id,
        skill_id=skill_id,
        skill_type="learn"
    ).first()

    # The selected partner must offer to teach this skill.
    can_teach = StudentSkill.query.filter_by(
        student_id=partner_id,
        skill_id=skill_id,
        skill_type="teach"
    ).first()

    if not wants_to_learn or not can_teach:
        flash(
            "This student is not a valid match for the selected skill.",
            "error"
        )
        return redirect(url_for("find_learning_partner"))

    existing_request = LearningRequest.query.filter_by(
        student_id=student_id,
        partner_id=partner_id,
        skill_id=skill_id,
        status="Pending"
    ).first()

    if existing_request:
        flash(
            f"Your request for {skill.skill_name} is already pending.",
            "info"
        )
        return redirect(url_for("find_learning_partner"))

    try:
        learning_request = LearningRequest(
            student_id=student_id,
            partner_id=partner_id,
            skill_id=skill_id,
            status="Pending"
        )

        db.session.add(learning_request)
        db.session.commit()

        flash(
            f"Learning request sent to {partner.name} "
            f"for {skill.skill_name}!",
            "success"
        )

    except Exception:
        db.session.rollback()
        app.logger.exception("Learning request failed")
        flash(
            "Could not send the learning request. Please try again.",
            "error"
        )

    return redirect(url_for("find_learning_partner"))


@app.route("/match-result")
def match_result():
    if not session.get("user_id"):
        return redirect(url_for("login"))

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


@app.route("/skill-gap-analysis")
def skill_gap_analysis():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    return render_template("skill_gap_analysis.html")


# Initialize database and register blueprints.
init_db(app)
app.register_blueprint(auth_bp)
app.register_blueprint(skills_bp)


@app.route("/test-db")
def test_db():
    try:
        with db.engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")

        return {"message": "Database connected successfully!"}, 200

    except Exception:
        app.logger.exception("Database connection failed")
        return {
            "error": "Database connection failed. Check server logs."
        }, 500


@app.route("/create-tables")
def create_tables():
    try:
        with app.app_context():
            db.create_all()

        return {
            "message": "All database tables created successfully!"
        }, 200

    except Exception:
        app.logger.exception("Table creation failed")
        return {
            "error": "Table creation failed. Check server logs."
        }, 500


@app.route("/availability", methods=["GET", "POST"])
def availability():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    student_id = session["user_id"]
    error = None
    success = None

    if request.method == "POST":
        day = request.form.get("day_of_week", "").strip()
        start = request.form.get("start_time", "").strip()
        end = request.form.get("end_time", "").strip()

        allowed_days = {
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"
        }

        if not day or not start or not end:
            error = "Please select a day, start time, and end time."
        elif day.title() not in allowed_days:
            error = "Please select a valid day."
        else:
            try:
                start_time = datetime.strptime(
                    start, "%H:%M"
                ).time()

                end_time = datetime.strptime(
                    end, "%H:%M"
                ).time()

                if start_time >= end_time:
                    error = "End time must be later than start time."
                else:
                    entry = Availability(
                        student_id=student_id,
                        day_of_week=day.title(),
                        start_time=start_time,
                        end_time=end_time
                    )

                    db.session.add(entry)
                    db.session.commit()
                    success = "Availability saved successfully!"

            except ValueError:
                error = "Invalid time format. Please try again."

            except Exception:
                db.session.rollback()
                app.logger.exception("Availability save failed")
                error = (
                    "Could not save availability. Check the terminal."
                )

    saved_availability = Availability.query.filter_by(
        student_id=student_id
    ).order_by(
        Availability.availability_id.desc()
    ).all()

    return render_template(
        "availability.html",
        saved_availability=saved_availability,
        error=error,
        success=success
    )


@app.route(
    "/delete-availability/<int:availability_id>",
    methods=["POST"]
)
def delete_availability(availability_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    entry = Availability.query.filter_by(
        availability_id=availability_id,
        student_id=session["user_id"]
    ).first()

    if entry:
        try:
            db.session.delete(entry)
            db.session.commit()
        except Exception:
            db.session.rollback()
            app.logger.exception("Availability deletion failed")
            return (
                "Could not delete availability. Check terminal.",
                500
            )

    return redirect(url_for("availability"))


print("\n--- REGISTERED ROUTES ---")
for rule in app.url_map.iter_rules():
    print(rule, "->", rule.endpoint)
print("-------------------------\n")


if __name__ == "__main__":
    app.run(debug=True)
