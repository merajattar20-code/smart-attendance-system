from flask import Flask, request, jsonify, render_template
import sqlite3
import math
from datetime import datetime

app = Flask(__name__)

DATABASE = "attendance.db"

# ---------------------------------
# College Location (change later)
# ---------------------------------

COLLEGE_LAT = 17.6599
COLLEGE_LON = 75.9064
ALLOWED_RADIUS = 200   # meters


# ---------------------------------
# Database Setup
# ---------------------------------

def get_db():
    return sqlite3.connect(DATABASE)


def init_db():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_email TEXT,
        latitude REAL,
        longitude REAL,
        date TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------------------------
# Distance Calculation (Haversine)
# ---------------------------------

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# ---------------------------------
# Routes
# ---------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------
# Register Student
# ---------------------------------

@app.route("/register", methods=["POST"])
def register():

    data = request.json
    name = data["name"]
    email = data["email"]

    conn = get_db()
    cursor = conn.cursor()

    try:

        cursor.execute(
            "INSERT INTO students(name,email) VALUES (?,?)",
            (name, email)
        )

        conn.commit()

        return jsonify({"status": "registered"})

    except:

        return jsonify({"status": "already exists"})


# ---------------------------------
# Mark Attendance
# ---------------------------------

@app.route("/mark-attendance", methods=["POST"])
def mark_attendance():

    data = request.json

    email = data["email"]
    latitude = float(data["latitude"])
    longitude = float(data["longitude"])

    distance = calculate_distance(
        latitude,
        longitude,
        COLLEGE_LAT,
        COLLEGE_LON
    )

    if distance > ALLOWED_RADIUS:

        return jsonify({
            "status": "denied",
            "message": "You are outside college campus",
            "distance": distance
        })

    now = datetime.now()

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO attendance(student_email,latitude,longitude,date,time) VALUES (?,?,?,?,?)",
        (
            email,
            latitude,
            longitude,
            now.date().isoformat(),
            now.time().isoformat()
        )
    )

    conn.commit()

    return jsonify({
        "status": "success",
        "message": "Attendance marked",
        "distance": distance
    })


# ---------------------------------
# Get Attendance History
# ---------------------------------

@app.route("/attendance/<email>")
def get_attendance(email):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT date,time FROM attendance WHERE student_email=?",
        (email,)
    )

    records = cursor.fetchall()

    result = []

    for r in records:

        result.append({
            "date": r[0],
            "time": r[1]
        })

    return jsonify(result)


# ---------------------------------
# Server Start
# ---------------------------------

if __name__ == "__main__":
    app.run(debug=True)
