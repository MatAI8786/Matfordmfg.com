from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, static_folder="static")

# Home Route
@app.route("/")
def home():
    return render_template("home.html")

# About Page Route
@app.route("/about")
def about():
    return render_template("about.html")

# Services Page Route
@app.route("/services")
def services():
    return render_template("services.html")

# Contact Page Route
@app.route("/contact")
def contact():
    return render_template("contact.html")

# Mori Machines Page Route
@app.route("/mori-machines")
def mori_machines():
    return render_template("mori_machines.html")

@app.route("/test_hero")              
def test_hero():
    return render_template("test_hero.html")

if __name__ == "__main__":
    app.run(debug=True)
