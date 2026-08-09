from flask import Flask, render_template, request
import pickle, sqlite3
import pandas as pd

app = Flask(__name__)

with open("model.pkl", "rb") as f:
    model = pickle.load(f)
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

FEATURES = ["Air_Temperature_K","Process_Temperature_K","Rotational_Speed_RPM",
            "Torque_Nm","Tool_Wear_min","Machine_Age_years","Operating_Hours"]

def init_db():
    conn = sqlite3.connect("predictions.db")
    conn.execute("""CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        air_temperature REAL, process_temperature REAL, rotational_speed REAL,
        torque REAL, tool_wear REAL, machine_age REAL, operating_hours REAL,
        prediction INTEGER, probability REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["GET","POST"])
def predict():
    if request.method == "GET":
        return render_template("predict.html")

    values = [
        float(request.form["air_temperature"]),
        float(request.form["process_temperature"]),
        float(request.form["rotational_speed"]),
        float(request.form["torque"]),
        float(request.form["tool_wear"]),
        float(request.form["machine_age"]),
        float(request.form["operating_hours"])
    ]

    data = pd.DataFrame([values], columns=FEATURES)
    scaled = scaler.transform(data)
    prediction = int(model.predict(scaled)[0])
    probability = float(model.predict_proba(scaled)[0][1])
    result = "Maintenance Required" if prediction else "Machine Operating Normally"

    conn = sqlite3.connect("predictions.db")
    conn.execute("""INSERT INTO predictions
        (air_temperature,process_temperature,rotational_speed,torque,tool_wear,
         machine_age,operating_hours,prediction,probability)
        VALUES (?,?,?,?,?,?,?,?,?)""", (*values, prediction, probability))
    conn.commit()
    conn.close()

    return render_template("result.html", result=result, prediction=prediction,
                           probability=round(probability*100,2), values=values)

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("predictions.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 20").fetchall()
    total = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    failures = conn.execute("SELECT COUNT(*) FROM predictions WHERE prediction=1").fetchone()[0]
    conn.close()
    return render_template("dashboard.html", rows=rows, total=total,
                           failures=failures, normal=total-failures)

if __name__ == "__main__":
    app.run(debug=True)
