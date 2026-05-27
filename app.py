from flask import Flask, render_template, request
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    questions = None
    role = None
    if request.method == "POST":
        role = request.form.get("role")
        prompt = f"Give me 5 interview questions for a {role} role. Number them 1-5. Only give the questions, no explanations."
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )
        questions = response.text
    return render_template("index.html", questions=questions, role=role)

if __name__ == "__main__":
    app.run(debug=True)