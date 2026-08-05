from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    name = "Flask"
    return render_template("index.html", username=name)

if __name__ == "__main__":
    #app.run(debug=True, use_reloader=False)
    app.run(host="0.0.0.0", port=5000, debug=True)