from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from src.auth import Auth
from src.agent import AIAgent
from src.study_planner import StudyPlanner
from src.roadmap_generator import RoadmapGenerator
from src.content_explainer import ContentExplainer
from src.notes_extractor import NotesExtractor
from src.progress_tracker import ProgressTracker
from src.quiz_creator import QuizCreator
from src.motivation_prompter import MotivationPrompter
from src.assignment_manager import AssignmentManager
from src.peer_matcher import PeerMatcher

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize modules
auth = Auth()
ai_agent = AIAgent()
study_planner = StudyPlanner()
roadmap_generator = RoadmapGenerator()
content_explainer = ContentExplainer()
notes_extractor = NotesExtractor()
progress_tracker = ProgressTracker()
quiz_creator = QuizCreator()
motivation_prompter = MotivationPrompter()
assignment_manager = AssignmentManager()
peer_matcher = PeerMatcher()

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if auth.login(username, password):
            session["user_id"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    response = ai_agent.process_prompt(prompt)
    return jsonify({"response": response})

@app.route("/api/study-plan", methods=["POST"])
def generate_study_plan():
    data = request.json
    plan = study_planner.create_plan(data)
    return jsonify(plan)

@app.route("/api/roadmap", methods=["POST"])
def generate_roadmap():
    data = request.json
    roadmap = roadmap_generator.generate(data)
    return jsonify(roadmap)

@app.route("/api/explain", methods=["POST"])
def explain_topic():
    data = request.json
    explanation = content_explainer.explain(data["topic"])
    return jsonify(explanation)

@app.route("/api/notes", methods=["POST"])
def extract_notes():
    file = request.files["file"]
    notes = notes_extractor.extract(file)
    return jsonify(notes)

@app.route("/api/progress", methods=["GET"])
def track_progress():
    progress = progress_tracker.get_progress()
    return jsonify(progress)

@app.route("/api/quiz", methods=["POST"])
def generate_quiz():
    data = request.json
    quiz = quiz_creator.create_quiz(data["topic"])
    return jsonify(quiz)

@app.route("/api/motivation", methods=["GET"])
def get_motivation():
    motivation = motivation_prompter.get_prompt()
    return jsonify(motivation)

@app.route("/api/assignments", methods=["POST"])
def manage_assignments():
    data = request.json
    assignments = assignment_manager.manage(data)
    return jsonify(assignments)

@app.route("/api/peer-match", methods=["POST"])
def peer_match():
    data = request.json
    matches = peer_matcher.match(data)
    return jsonify(matches)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if auth.register(username, password):
            return redirect(url_for("login"))
        else:
            return render_template("register.html", error="Username already exists")
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)