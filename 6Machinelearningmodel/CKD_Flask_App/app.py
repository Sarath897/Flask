from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load model
model = pickle.load(open("models/finilized_model_SVC.sav", "rb"))

# Load scaler
scaler = pickle.load(open("models/scaler.pkl", "rb"))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    bgr = float(request.form["bgr"])
    bu = float(request.form["bu"])
    sc = float(request.form["sc"])
    pcv = float(request.form["pcv"])
    wc = float(request.form["wc"])

    #data = np.array([[bgr, bu, sc, pcv, wc]])

    data = pd.DataFrame(
    np.array([[bgr, bu, sc, pcv, wc]]),
    columns=["bgr", "bu", "sc", "pcv", "wc"]
)


    scaled_data = scaler.transform(data)

    prediction = model.predict(scaled_data)[0]

    if prediction == 1:
        result = "CKD Detected"
    else:
        result = "No CKD"

    return render_template("result.html", prediction=result)


if __name__ == "__main__":
    app.run(debug=True)