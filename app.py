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

# Ensure Flask Serves Static Files Properly
@app.route('/static/images/<path:filename>')
def serve_static_images(filename):
    return send_from_directory(os.path.join(app.root_path, 'static/images'), filename)

if __name__ == "__main__":
    app.run(debug=True)
