from flask import Flask, render_template, request, redirect
import mysql.connector
import os

from ai_model import predict_label
from image_ai import detect_objects
from video_ai import analyze_video
from audio_ai import analyze_audio

app = Flask(__name__)

# -----------------------------
# MYSQL CONNECTION
# -----------------------------

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Shruthi@1234",
    database="data_annotation_tool"
)

# -----------------------------
# UPLOAD FOLDER
# -----------------------------

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------
# HOME / LOGIN
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# DASHBOARD
# -----------------------------

@app.route("/dashboard")
def dashboard():

    cursor = db.cursor()

    # Total data
    cursor.execute(
        "SELECT COUNT(*) FROM annotations"
    )

    total = cursor.fetchone()[0]

    # Labeled data
    cursor.execute(
        "SELECT COUNT(*) FROM annotations WHERE label IS NOT NULL"
    )

    labeled = cursor.fetchone()[0]

    # Pending data
    pending = total - labeled

    cursor.close()

    return render_template(
        "dashboard.html",
        total=total,
        labeled=labeled,
        pending=pending
    )


# -----------------------------
# UPLOAD PAGE
# -----------------------------

@app.route("/upload")
def upload():

    return render_template("upload.html")


# -----------------------------
# LABEL DATA
# -----------------------------

@app.route("/label", methods=["POST"])
def label_data():

    input_type = request.form.get("input_type")


    # -----------------------------
    # TEXT
    # -----------------------------

    if input_type == "text":

        data = request.form.get("data")

        if not data:
            return "Please enter some text."

        # AI text classification
        ai_label = predict_label(data)

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO annotations (data, label)
            VALUES (%s, %s)
            """,
            (data, ai_label)
        )

        db.commit()
        cursor.close()

        return render_template(
            "text_result.html",
            text=data,
            label=ai_label
        )


    # -----------------------------
    # IMAGE
    # -----------------------------

    elif input_type == "image":

        image = request.files.get("image")

        if not image:
            return "Please select an image."

        image_path = os.path.join(
            UPLOAD_FOLDER,
            image.filename
        )

        image.save(image_path)

        # AI image analysis
        objects = detect_objects(image_path)

        detected_objects = ", ".join(objects)

        if not detected_objects:
            detected_objects = "No objects detected"

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO annotations (data, label)
            VALUES (%s, %s)
            """,
            (image.filename, detected_objects)
        )

        db.commit()
        cursor.close()

        return render_template(
            "image_result.html",
            objects=objects
        )


    # -----------------------------
    # VIDEO
    # -----------------------------

    elif input_type == "video":

        video = request.files.get("video")

        if not video:
            return "Please select a video."

        video_path = os.path.join(
            UPLOAD_FOLDER,
            video.filename
        )

        video.save(video_path)

        # AI video analysis
        result = analyze_video(video_path)

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO annotations (data, label)
            VALUES (%s, %s)
            """,
            (video.filename, result)
        )

        db.commit()
        cursor.close()

        return render_template(
            "video_result.html",
            result=result
        )


    # -----------------------------
    # AUDIO
    # -----------------------------

    elif input_type == "audio":

        audio = request.files.get("audio")

        if not audio:
            return "Please select an audio file."

        audio_path = os.path.join(
            UPLOAD_FOLDER,
            audio.filename
        )

        audio.save(audio_path)

        # AI audio analysis
        result = analyze_audio(audio_path)

        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO annotations (data, label)
            VALUES (%s, %s)
            """,
            (audio.filename, result)
        )

        db.commit()
        cursor.close()

        return render_template(
            "audio_result.html",
            sounds=result.split(", ")
        )


    return "Invalid input type."


# -----------------------------
# RECORDS
# -----------------------------

@app.route("/records")
def records():

    search = request.args.get("search", "")
    label = request.args.get("label", "All")

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT * FROM annotations
        WHERE data LIKE %s
    """

    params = [f"%{search}%"]

    if label != "All":

        query += " AND label = %s"

        params.append(label)

    cursor.execute(
        query,
        params
    )

    records = cursor.fetchall()

    cursor.close()

    return render_template(
        "records.html",
        records=records,
        search=search,
        label=label
    )


# -----------------------------
# DELETE
# -----------------------------

@app.route("/delete/<int:id>")
def delete(id):

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM annotations WHERE id = %s",
        (id,)
    )

    db.commit()

    cursor.close()

    return redirect("/records")


# -----------------------------
# EDIT
# -----------------------------

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        label = request.form.get("label")

        cursor.execute(
            """
            UPDATE annotations
            SET label = %s
            WHERE id = %s
            """,
            (label, id)
        )

        db.commit()

        cursor.close()

        return redirect("/records")


    cursor.execute(
        """
        SELECT * FROM annotations
        WHERE id = %s
        """,
        (id,)
    )

    record = cursor.fetchone()

    cursor.close()

    return render_template(
        "edit.html",
        record=record
    )


# -----------------------------
# RUN APPLICATION
# -----------------------------

if __name__ == "__main__":

    app.run(debug=True)