from flask import Flask, render_template, send_from_directory
import os
from flask import Flask, render_template, send_from_directory, request, session

app = Flask(__name__)
app.secret_key = "campus_skill_exchange"
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")

        session["user_name"] = username

        return render_template(
            "dashboard.html",
            user_name=username
        )

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        full_name = request.form.get("full_name")

        session["user_name"] = full_name

        return render_template(
            "dashboard.html",
            user_name=full_name
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
    return render_template("profile.html")

@app.route("/edit-profile")
def edit_profile():
    return render_template("edit_profile.html")

@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(
        os.path.join(app.root_path, "images"),
        filename
    )


if __name__ == "__main__":
    app.run(debug=True)