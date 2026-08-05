from flask import Blueprint, render_template, request

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def home():

    message = ""

    if request.method == "POST":

        userID = request.form.get("userID")

        message = f"Hello {userID}, Welcome to Flask!"

    return render_template(
        "index.html",
        message=message
    )