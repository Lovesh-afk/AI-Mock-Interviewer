from flask import Flask, render_template, request, session
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey123"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_questions(role):
    prompt = f"""Generate exactly 5 interview questions for a {role} role.
    Return only the questions, numbered 1-5, one per line. No explanations."""
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    )
    import re
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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        role = request.form.get("role")
        try:
            questions = generate_questions(role)
        except Exception as e:
            return render_template("index.html", error="AI server is busy, please try again in a moment.")
        session["questions"] = questions
        session["role"] = role
        session["current"] = 0
        session["feedbacks"] = []
        return render_template("interview.html", 
                             question=questions[0], 
                             number=1, 
                             total=5,
                             role=role)
    return render_template("index.html")

@app.route("/answer", methods=["POST"])
def answer():
    answer_text = request.form.get("answer")
    questions = session.get("questions")
    current = session.get("current")
    role = session.get("role")
    feedbacks = session.get("feedbacks")

    try:
        feedback = evaluate_answer(questions[current], answer_text, role)
    except Exception as e:
        feedback = "SCORE: 0\n⚠️ AI feedback unavailable right now."

    # Extract score from feedback
    import re
    score_match = re.search(r"SCORE:\s*(\d+)", feedback)
    score = int(score_match.group(1)) if score_match else 0

    # Remove the SCORE line from displayed feedback
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
        return render_template("results.html", feedbacks=feedbacks, role=role, avg_score=avg_score)

    return render_template("interview.html",
                         question=questions[current + 1],
                         number=current + 2,
                         total=5,
                         role=role)
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)