# 🎯 AI Mock Interviewer

An AI-powered mock interview web application that generates role-specific interview questions and provides instant feedback on your answers using Google's Gemini AI.

##  Live Demo
[Link will be added after deployment]

##  Features
- 🤖 AI-generated interview questions for any job role
- 📊 Instant AI feedback and scoring for each answer
- 🎯 Three difficulty levels: Beginner, Intermediate, Advanced
- ⏱️ 3-minute countdown timer per question (auto-submits)
- 📋 Interview history tracking with scores
- 🔐 Secure user authentication with password hashing
- 📈 Overall score with performance summary

## Tech Stack
- **Backend:** Python, Flask
- **AI:** Google Gemini API
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **ORM:** SQLAlchemy
- **Authentication:** Flask-Bcrypt (password hashing)
- **Frontend:** HTML, CSS, Bootstrap 5
- **Deployment:** Render

## ⚙️ Setup & Installation

1. Clone the repository
```bash
git clone https://github.com/Lovesh-afk/ai-mock-interviewer.git
cd ai-mock-interviewer
```

2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create `.env` file
```
GEMINI_API_KEY=your_gemini_api_key_here

5. Run the app
```bash
python app.py
```

6. Open http://127.0.0.1:5000 in your browser

## 📁 Project Structure
ai-mock-interviewer/
├── app.py              # Main Flask application
├── requirements.txt    # Project dependencies
├── .env               # Environment variables (not in repo)
├── templates/
│   ├── index.html     # Home page
│   ├── login.html     # Login page
│   ├── register.html  # Register page
│   ├── interview.html # Interview page with timer
│   ├── results.html   # Results with AI feedback
│   └── history.html   # Interview history
└── static/            # Static files

## 🔐 Security
- Passwords hashed using Bcrypt
- API keys stored in environment variables
- Session-based authentication
- Protected routes redirect to login

## 👨‍💻 Author
Lovesh Yadav — [GitHub](https://github.com/Lovesh-afk) · [LinkedIn](https://www.linkedin.com/in/lovesh-yadav-09104a392/)