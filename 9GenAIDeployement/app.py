from flask import Flask, render_template, request
from services.openai_service import get_response
import markdown

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    prompt = request.form["prompt"]

    response = get_response(prompt)

       # Convert Markdown to HTML
    response_html = markdown.markdown(
        response,
        extensions=[
            "fenced_code",
            "tables"
        ]
    )


    return render_template(
        "result.html",
        prompt=prompt,
        response=response
    )


if __name__ == "__main__":
    app.run(debug=True)