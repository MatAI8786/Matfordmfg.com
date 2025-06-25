# app.py
import os
import tempfile
import smtplib
import re
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    flash,
    current_app
)

from werkzeug.utils import secure_filename
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()


# ─── CONFIGURATION ────────────────────────────────────────────────────────────────

# Serve templates from the 'docs' folder and static files from 'docs/static'
app = Flask(__name__, static_folder="docs/static", template_folder="docs")
# Used for flashing messages if needed
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change_this_to_a_random_key")

# Email‐sending configuration (set these as environment variables):
EMAIL_ADDRESS = os.environ.get("EMAIL_USER")     # e.g. "youraddress@gmail.com"
EMAIL_PASSWORD = os.environ.get("EMAIL_PASS")    # e.g. an app‐specific password

# Where uploaded attachments will be stored (temporary). Make sure this folder exists.
UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Only allow attachments with these extensions
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "doc", "docx", "txt"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


def allowed_file(filename):
    """
    Return True if filename's extension is in ALLOWED_EXTENSIONS.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ─── ORIGINAL PAGE ROUTES ──────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/mori-machines")
def mori_machines():
    return render_template("mori_machines.html")


# (Optional) any other test page you had before
@app.route("/test_hero")
def test_hero():
    return render_template("test_hero.html")


# ─── NEW: REQUEST QUOTE ENDPOINT ────────────────────────────────────────────────────

@app.route("/request_quote", methods=["POST"])
def request_quote():
    # 1) Extract & validate form fields
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    title = request.form.get("title", "").strip()
    body  = request.form.get("body", "").strip()

    # Basic field validation
    if not email or not EMAIL_REGEX.match(email):
        return jsonify({"error": "Please enter a valid email address."}), 400
    if not title:
        return jsonify({"error": "Subject cannot be empty."}), 400
    if not body:
        return jsonify({"error": "Message cannot be empty."}), 400

    # (Optional) loose phone check — uncomment if you want to enforce a pattern
    # PHONE_REGEX = re.compile(r"^[0-9 +()-]{7,20}$")
    # if phone and not PHONE_REGEX.match(phone):
    #     return jsonify({"error": "Please enter a valid phone number."}), 400

    # 2) Handle file uploads (unchanged)
    saved_files = []
    files = request.files.getlist("attachments")
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)
            saved_files.append(save_path)

    # 3) Check your email credentials
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return jsonify({"error": "Server email is not configured."}), 500

    # 4) Build the email
    msg = EmailMessage()
    msg["Subject"] = f"New Consultation Request: {title}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"]   = "your_sales_inbox@matfordmfg.com"
    msg.set_content(
        f"New request from {email}\n"
        f"Phone: {phone or 'n/a'}\n\n"
        f"Subject: {title}\n\n"
        f"{body}\n"
    )

    # 5) Attach uploaded files (unchanged)
    for fp in saved_files:
        try:
            with open(fp, "rb") as f:
                data = f.read()
                msg.add_attachment(data,
                                   maintype="application",
                                   subtype="octet-stream",
                                   filename=os.path.basename(fp))
        except Exception as e:
            current_app.logger.warning(f"Skipping attachment {fp}: {e}")

    # 6) Send via SMTP (unchanged)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as smtp_error:
        for fp in saved_files:
            try: os.remove(fp)
            except: pass
        current_app.logger.error(f"SMTP send failed: {smtp_error}")
        return jsonify({"error": "Could not send email. Try again later."}), 500

    # 7) Cleanup and return success
    for fp in saved_files:
        try: os.remove(fp)
        except: pass

    return jsonify({"status": "OK"}), 200

# ─── MAIN RUNNER ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # app.run(debug=True) → in production, turn debug=False
    app.run(debug=True)
