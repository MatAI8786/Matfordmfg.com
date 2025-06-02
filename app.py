# app.py
import os
import tempfile
import smtplib
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    flash
)
from werkzeug.utils import secure_filename
from email.message import EmailMessage

# ─── CONFIGURATION ────────────────────────────────────────────────────────────────

app = Flask(__name__, static_folder="static")
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
    """
    Receives the AJAX POST from the “Request Free Consultation” modal:
      - title    → subject line
      - body     → detailed message
      - attachments → zero or more files

    Sends an email to a fixed recipient (e.g. your sales inbox), with any attachments,
    then cleans up the temporary files and returns HTTP 200 (“OK”) on success.
    """
    # 1) Extract form fields
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()

    # 2) Handle file uploads
    saved_files = []
    files = request.files.getlist("attachments")
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)
            saved_files.append(save_path)

    # 3) Build the email
    #   - Make sure EMAIL_ADDRESS / EMAIL_PASSWORD are set in the environment
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        # Missing configuration → return an error
        return (
            jsonify({"error": "Server email is not configured."}),
            500,
        )

    msg = EmailMessage()
    msg["Subject"] = f"New Consultation Request: {title}"
    msg["From"] = EMAIL_ADDRESS
    # ← Replace this with whatever address you want to receive these requests
    msg["To"] = "your_sales_inbox@matfordmfg.com"
    msg.set_content(
        f"A new consultation request has arrived.\n\n"
        f"Subject: {title}\n\n"
        f"Message:\n{body}\n"
    )

    # Attach any uploaded files
    for file_path in saved_files:
        try:
            with open(file_path, "rb") as f:
                file_data = f.read()
                # Derive a generic MIME type; you can refine if desired
                maintype = "application"
                subtype = "octet-stream"
                msg.add_attachment(
                    file_data,
                    maintype=maintype,
                    subtype=subtype,
                    filename=os.path.basename(file_path),
                )
        except Exception as e:
            # If an attachment fails to read, just skip it
            print(f"Could not attach {file_path}: {e}")
            continue

    # 4) Connect via SMTP and send
    try:
        # Example uses Gmail's SMTP over SSL on port 465
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as smtp_error:
        # If email fails, clean up and return error 500
        for fp in saved_files:
            try:
                os.remove(fp)
            except:
                pass
        print("SMTP send failed:", smtp_error)
        return (
            jsonify({"error": "Could not send email. Try again later."}),
            500,
        )

    # 5) Clean up the temporary files
    for fp in saved_files:
        try:
            os.remove(fp)
        except:
            pass

    # 6) Return a JSON “OK” response (your front‐end JS can interpret this)
    return jsonify({"status": "OK"}), 200


# ─── MAIN RUNNER ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # app.run(debug=True) → in production, turn debug=False
    app.run(debug=True)
