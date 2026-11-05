"""
app.py
Flask web application for the Computer Troubleshooting Expert System.

The browser never decides the diagnosis. It only sends answers; the inference
engine (engine.py) decides the next question or the final result.

Session data (stored in a signed cookie):
    category_id : id of the chosen category
    answers     : ordered list of [question_id, "yes" | "no" | "unsure"]
"""

from flask import Flask, redirect, render_template, request, session, url_for

from engine import ANSWER_LABELS, infer
from knowledge_base import CATEGORIES, QUESTIONS, RULES

APP_TITLE = "Computer Troubleshooting Expert System"

app = Flask(__name__)
# Needed to sign the session cookie. Fine for a local student project;
# use a private random value if you ever deploy this online.
app.secret_key = "student-project-secret-key-change-me"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


# ---------------------------------------------------------------- helpers
@app.context_processor
def inject_globals():
    """Values available in every template."""
    return {"app_title": APP_TITLE, "rule_count": len(RULES)}


@app.after_request
def no_cache(response):
    """Stop the browser showing an outdated question page after Back/Forward."""
    response.headers["Cache-Control"] = "no-store"
    return response


def current_state():
    """Return (category_id, answers) from the session; category_id is None if not started."""
    return session.get("category_id"), session.get("answers", [])


def build_history(answers):
    """Turn stored answers into readable lines for the 'your answers so far' list."""
    history = []
    for qid, value in answers:
        question = QUESTIONS.get(qid)
        if question:
            history.append({"question": question["text"], "answer": ANSWER_LABELS.get(value, value)})
    return history


# ----------------------------------------------------------------- routes
@app.route("/")
def index():
    """Home page: title, description, and the category cards."""
    return render_template("index.html", categories=CATEGORIES, message=None)


@app.route("/start/<category_id>")
def start(category_id):
    """Begin a new diagnosis for the chosen category."""
    if category_id not in {c["id"] for c in CATEGORIES}:
        return render_template("index.html", categories=CATEGORIES,
                               message="That category does not exist. Please choose one below."), 404
    session.clear()
    session["category_id"] = category_id
    session["answers"] = []
    return redirect(url_for("question"))


@app.route("/question")
def question():
    """Show the current question, or jump to the result when the engine is finished."""
    category_id, answers = current_state()
    if category_id is None:
        return redirect(url_for("index"))

    step = infer(category_id, answers)
    session["answers"] = step["answers"]          # cleaned copy of the answers

    if step["status"] == "result":
        return redirect(url_for("result"))

    return render_template(
        "troubleshoot.html",
        category=step["category"],
        question=step["question"],
        number=step["number"],
        history=build_history(step["answers"]),
    )


@app.route("/answer", methods=["POST"])
def answer():
    """Receive one Yes / No / Not sure answer."""
    category_id, answers = current_state()
    if category_id is None:
        return redirect(url_for("index"))

    value = request.form.get("answer", "")
    question_id = request.form.get("question_id", "")

    step = infer(category_id, answers)
    # Accept the answer only if it is for the question currently being asked
    # (protects against double clicks and old browser pages).
    if (step["status"] == "question"
            and step["question"]["id"] == question_id
            and value in ANSWER_LABELS):
        session["answers"] = step["answers"] + [[question_id, value]]

    return redirect(url_for("question"))


@app.route("/back", methods=["POST"])
def back():
    """Undo the last answer. From the first question, return to the home page."""
    category_id, answers = current_state()
    if category_id is None:
        return redirect(url_for("index"))

    if answers:
        session["answers"] = answers[:-1]
        return redirect(url_for("question"))

    session.clear()
    return redirect(url_for("index"))


@app.route("/result")
def result():
    """Show the final diagnosis (or the 'cannot determine' message)."""
    category_id, answers = current_state()
    if category_id is None:
        return redirect(url_for("index"))

    step = infer(category_id, answers)
    if step["status"] == "question":
        return redirect(url_for("question"))

    return render_template(
        "result.html",
        category=step["category"],
        result=step["result"],
        answer_count=len(step["answers"]),
    )


@app.route("/restart", methods=["POST"])
def restart():
    """Clear everything and go back to the home page."""
    session.clear()
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found(error):
    return render_template("index.html", categories=CATEGORIES,
                           message="Page not found. Please start from the home page."), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
