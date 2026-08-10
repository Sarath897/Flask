from flask import Flask, render_template, request, redirect
import pickle
import sqlite3
import pandas as pd

app = Flask(__name__)


# =========================================================
# LOAD MODEL
# =========================================================

with open("model.pkl", "rb") as f:
    model = pickle.load(f)


# =========================================================
# LOAD SCALER
# =========================================================

with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)


# =========================================================
# FEATURES
# =========================================================

FEATURES = [
    "Air_Temperature_K",
    "Process_Temperature_K",
    "Rotational_Speed_RPM",
    "Torque_Nm",
    "Tool_Wear_min",
    "Machine_Age_years",
    "Operating_Hours"
]


# =========================================================
# DATABASE
# =========================================================

def init_db():

    conn = sqlite3.connect("predictions.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            air_temperature REAL,

            process_temperature REAL,

            rotational_speed REAL,

            torque REAL,

            tool_wear REAL,

            machine_age REAL,

            operating_hours REAL,

            prediction INTEGER,

            probability REAL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# PREDICTION
# =========================================================

@app.route("/predict", methods=["GET", "POST"])
def predict():

    # -------------------------
    # OPEN PREDICTION PAGE
    # -------------------------

    if request.method == "GET":

        return render_template("predict.html")


    # -------------------------
    # GET FORM VALUES
    # -------------------------

    air_temperature = float(
        request.form["air_temperature"]
    )

    process_temperature = float(
        request.form["process_temperature"]
    )

    rotational_speed = float(
        request.form["rotational_speed"]
    )

    torque = float(
        request.form["torque"]
    )

    tool_wear = float(
        request.form["tool_wear"]
    )

    machine_age = float(
        request.form["machine_age"]
    )


    # =====================================================
    # OPERATING HOURS - HH:MM
    # =====================================================

    operating_hours_text = request.form["operating_hours"]

    hours, minutes = operating_hours_text.split(":")

    operating_hours = (
        float(hours) +
        (float(minutes) / 60)
    )


    # =====================================================
    # VALUES FOR ML MODEL
    # =====================================================

    values = [

        air_temperature,

        process_temperature,

        rotational_speed,

        torque,

        tool_wear,

        machine_age,

        operating_hours
    ]


    # =====================================================
    # CREATE DATAFRAME
    # =====================================================

    data = pd.DataFrame(
        [values],
        columns=FEATURES
    )


    # =====================================================
    # SCALE INPUT
    # =====================================================

    scaled = scaler.transform(data)


    # =====================================================
    # PREDICTION
    # =====================================================

    prediction = int(
        model.predict(scaled)[0]
    )


    # =====================================================
    # PROBABILITY
    # =====================================================

    probability = float(
        model.predict_proba(scaled)[0][1]
    )


    # =====================================================
    # RESULT
    # =====================================================

    result = (

        "Maintenance Required"

        if prediction == 1

        else

        "Machine Operating Normally"
    )


    # =====================================================
    # SAVE TO DATABASE
    # =====================================================

    conn = sqlite3.connect("predictions.db")


    conn.execute("""
        INSERT INTO predictions
        (
            air_temperature,
            process_temperature,
            rotational_speed,
            torque,
            tool_wear,
            machine_age,
            operating_hours,
            prediction,
            probability
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,

    (
        air_temperature,

        process_temperature,

        rotational_speed,

        torque,

        tool_wear,

        machine_age,

        operating_hours,

        prediction,

        probability
    ))


    conn.commit()

    conn.close()


    # =====================================================
    # RESULT PAGE
    # =====================================================

    return render_template(

        "result.html",

        result=result,

        prediction=prediction,

        probability=round(
            probability * 100,
            2
        ),

        air_temperature=air_temperature,

        process_temperature=process_temperature,

        rotational_speed=rotational_speed,

        torque=torque,

        tool_wear=tool_wear,

        machine_age=machine_age,

        # Keep original HH:MM
        operating_hours=operating_hours_text,

        # Numeric value used by ML
        operating_hours_numeric=operating_hours,

        values=values
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("predictions.db")

    conn.row_factory = sqlite3.Row


    # Get latest 20 predictions

    rows = conn.execute("""
        SELECT *
        FROM predictions
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()


    # Total predictions

    total = conn.execute("""
        SELECT COUNT(*)
        FROM predictions
    """).fetchone()[0]


    # Failure predictions

    failures = conn.execute("""
        SELECT COUNT(*)
        FROM predictions
        WHERE prediction = 1
    """).fetchone()[0]


    conn.close()


    return render_template(

        "dashboard.html",

        rows=rows,

        total=total,

        failures=failures,

        normal=total - failures
    )


# =========================================================
# CLEAR STORED PREDICTIONS
# =========================================================

@app.route("/clear_predictions", methods=["POST"])
def clear_predictions():

    conn = sqlite3.connect("predictions.db")


    # Delete all stored prediction records

    conn.execute("""
        DELETE FROM predictions
    """)


    # Save changes

    conn.commit()


    conn.close()


    # Go back to dashboard

    return redirect("/dashboard")


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)