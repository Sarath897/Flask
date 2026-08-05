from flask import Blueprint
from flask import render_template
from flask import request

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("register.html")


@main.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    age = int(request.form["age"])
    fee = float(request.form["fee"])

    gst = fee * 0.18
    total = fee + gst

    return render_template(
        "result.html",
        name=name,
        age=age,
        fee=fee,
        gst=round(gst, 2),
        total=round(total, 2)
    )