from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    return "Login Page"

@app.route("/register")
def register():
    return "Create Account Page"

@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(
        os.path.join(app.root_path, "images"),
        filename
    )

if __name__ == "__main__":
    app.run(debug=True)