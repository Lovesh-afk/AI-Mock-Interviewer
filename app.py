from flask import Flask, render_template, request, session, redirect, url_for, flash
from google import genai
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///interviews.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ─── Models ───────────────────────────────────────────────
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    interviews = db.relationship("Interview", backref="user", lazy=True)

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    avg_score = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# ─── AI Functions ─────────────────────────────────────────
def generate_questions(role, difficulty):
    prompt = f"""Generate exactly 5 {difficulty} level interview questions for a {role} role.
    {difficulty} means:
    - Beginner: basic concepts, definitions, simple problems
    - Intermediate: practical application, problem solving, moderate complexity
    - Advanced: system design, optimization, complex scenarios
    Return only the questions, numbered 1-5, one per line. No explanations."""
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    )
    lines = response.text.strip().split("\n")
    questions = []
    for line in lines:
        line = line.strip()
        if line and len(line) > 5:
            line = re.sub(r"^\d+[\.\)\-\s]+", "", line).strip()
            if line:
                questions.append(line)
    return questions[:5]

def evaluate_answer(question, answer, role):
    prompt = f"""You are an expert interviewer for a {role} role.
Question: {question}
Candidate's Answer: {answer}

Evaluate this answer and provide:
1. A score out of 10 (just the number, e.g. 7)
2. What was good about the answer
3. What could be improved
4. An ideal sample answer in 2-3 lines

Start your response with exactly this format:
SCORE: [number]

Then continue with the rest of the feedback."""
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    )
    return response.text

# ─── Auth Routes ──────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return render_template("register.html")
        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("index"))
        flash("Invalid username or password!", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ─── Main Routes ──────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        role = request.form.get("role")
        difficulty = request.form.get("difficulty", "Intermediate")
        try:
            questions = generate_questions(role, difficulty)
        except Exception as e:
            return render_template("index.html", error="AI server is busy, please try again.")
        session["questions"] = questions
        session["role"] = role
        session["difficulty"] = difficulty
        session["current"] = 0
        session["feedbacks"] = []
        return render_template("interview.html",
                             question=questions[0],
                             number=1,
                             total=5,
                             role=role,
                             difficulty=difficulty)
    return render_template("index.html")

@app.route("/answer", methods=["POST"])
def answer():
    if "user_id" not in session:
        return redirect(url_for("login"))
    answer_text = request.form.get("answer")
    questions = session.get("questions")
    current = session.get("current")
    role = session.get("role")
    difficulty = session.get("difficulty")
    feedbacks = session.get("feedbacks")

    try:
        feedback = evaluate_answer(questions[current], answer_text, role)
    except Exception as e:
        feedback = "SCORE: 0\n⚠️ AI feedback unavailable right now."

    score_match = re.search(r"SCORE:\s*(\d+)", feedback)
    score = int(score_match.group(1)) if score_match else 0
    clean_feedback = re.sub(r"SCORE:\s*\d+\n?", "", feedback).strip()

    feedbacks.append({
        "question": questions[current],
        "answer": answer_text,
        "feedback": clean_feedback,
        "score": score
    })
    session["feedbacks"] = feedbacks
    session["current"] = current + 1

    if current + 1 >= 5:
        avg_score = round(sum(f["score"] for f in feedbacks) / len(feedbacks), 1)
        # Save to database
        interview = Interview(
            user_id=session["user_id"],
            role=role,
            difficulty=difficulty,
            avg_score=avg_score
        )
        db.session.add(interview)
        db.session.commit()
        return render_template("results.html", feedbacks=feedbacks, role=role, avg_score=avg_score)

    return render_template("interview.html",
                         question=questions[current + 1],
                         number=current + 2,
                         total=5,
                         role=role,
                         difficulty=difficulty)

@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect(url_for("login"))
    interviews = Interview.query.filter_by(user_id=session["user_id"]).order_by(Interview.date.desc()).all()
    return render_template("history.html", interviews=interviews)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)