from flask import Flask, render_template, send_from_directory, request, session, redirect, url_for
import os

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

        username = request.form.get("username")

        session["user_name"] = username
        session["username"] = username

        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        session["full_name"] = request.form.get("full_name")
        session["username"] = request.form.get("username")
        session["email"] = request.form.get("email")
        session["department"] = request.form.get("department")
        session["semester"] = request.form.get("semester")

        session["user_name"] = session["full_name"]

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


if __name__ == "__main__":
    app.run(debug=True)