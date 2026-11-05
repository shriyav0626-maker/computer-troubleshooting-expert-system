"""
engine.py
Inference engine for the Computer Troubleshooting Expert System.

How it works (forward chaining):
  1. Facts = the user's answers so far (question id -> "yes" / "no" / "unsure").
  2. Every rule of the chosen category is checked against the facts:
       fired     - all conditions are confirmed          -> a candidate diagnosis
       ruled_out - a condition is contradicted/unsure    -> rule cannot fire
       possible  - nothing contradicts it yet, but some conditions are unanswered
  3. If a fired rule is at least as important (priority) as every possible rule,
     it becomes the diagnosis.
  4. Otherwise the engine asks the next unanswered question of the most
     important possible rule.
  5. If no rule fired and none is still possible, the cause is "unknown".

Answers are passed around as a list of [question_id, value] pairs, because a list
keeps the order of the answers (needed for the Back button).
"""

from knowledge_base import (
    ANSWERS, CATEGORIES, DISCLAIMER, FALLBACK_STEPS, QUESTIONS, RULES,
)

ANSWER_LABELS = {"yes": "Yes", "no": "No", "unsure": "Not sure"}
CONFIDENCE_LEVELS = ["Low", "Medium", "High"]


# ------------------------------------------------------------------ helpers
def get_category(category_id):
    """Return the category dictionary, or None if the id is unknown."""
    for category in CATEGORIES:
        if category["id"] == category_id:
            return category
    return None


def rules_for(category_id):
    return [rule for rule in RULES if rule["category"] == category_id]


def clean_answers(category_id, answers):
    """Keep only valid answers: known question of this category, valid value, no repeats."""
    cleaned = []
    seen = set()
    for item in answers or []:
        try:
            qid, value = item
        except (TypeError, ValueError):
            continue
        if not isinstance(qid, str) or not isinstance(value, str):
            continue
        question = QUESTIONS.get(qid)
        if question is None or question["category"] != category_id:
            continue
        if value not in ANSWERS or qid in seen:
            continue
        seen.add(qid)
        cleaned.append([qid, value])
    return cleaned


def rule_to_text(rule):
    """Readable IF-THEN form of a rule, used on the result page."""
    parts = ["category = " + rule["category"]]
    for qid, value in rule["conditions"].items():
        parts.append(qid + " = " + value.upper())
    return "IF " + " AND ".join(parts) + " THEN " + rule["cause"]


# ------------------------------------------------------------- rule matching
def evaluate_rule(rule, facts):
    """Compare one rule with the known facts."""
    matched, contradicted, unsure, unanswered = [], [], [], []
    for qid, needed in rule["conditions"].items():
        given = facts.get(qid)
        if given is None:
            unanswered.append(qid)
        elif given == needed:
            matched.append(qid)
        elif given == "unsure":
            unsure.append(qid)
        else:
            contradicted.append(qid)

    if contradicted or unsure:
        status = "ruled_out"      # a 'Not sure' answer cannot confirm a condition
    elif unanswered:
        status = "possible"
    else:
        status = "fired"
    return {"status": status, "matched": matched, "contradicted": contradicted,
            "unsure": unsure, "unanswered": unanswered}


def choose_next_question(possible_rules, facts):
    """Ask the first unanswered condition of the most important possible rule."""
    for rule in sorted(possible_rules, key=lambda r: -r["priority"]):
        for qid in rule["conditions"]:
            if qid not in facts:
                return QUESTIONS[qid]
    return None


def find_alternatives(evaluations, skip_causes, limit):
    """Near-miss rules (at least 2 conditions matched, at most 1 failed) as alternative causes."""
    candidates = []
    for rule, ev in evaluations:
        if rule["urgent"] or rule["cause"] in skip_causes:
            continue
        if len(ev["matched"]) < 2:
            continue
        if len(ev["contradicted"]) + len(ev["unsure"]) > 1:
            continue
        candidates.append((len(ev["matched"]), rule["priority"], rule["cause"]))
    candidates.sort(key=lambda c: (-c[0], -c[1]))

    causes = []
    for _, _, cause in candidates:
        if cause not in causes:
            causes.append(cause)
        if len(causes) == limit:
            break
    return causes


def build_notes(category_id, facts):
    notes = []
    if "unsure" in facts.values():
        notes.append("Some of your answers were 'Not sure', so this result is less reliable. "
                     "Checking those points and running the diagnosis again may help.")
    for rule in rules_for(category_id):
        if rule["urgent"] and any(facts.get(q) == "unsure" for q in rule["conditions"]):
            notes.append("You were not sure about a safety warning sign. If there is any chance of "
                         "smoke, a burning smell, or a swollen battery, shut the computer down, "
                         "disconnect power only if it is safe, and ask a qualified technician for help.")
            break
    return notes


def explain_facts(question_ids, facts):
    return [{"question": QUESTIONS[q]["text"], "answer": ANSWER_LABELS[facts[q]]}
            for q in question_ids if q in facts]


# ----------------------------------------------------------- building results
def build_diagnosis(category, rule, evaluations, facts):
    confidence = rule["confidence"]
    if "unsure" in facts.values():
        confidence = CONFIDENCE_LEVELS[max(0, CONFIDENCE_LEVELS.index(confidence) - 1)]
    return {
        "found": True,
        "category": category,
        "rule_id": rule["id"],
        "rule_text": rule_to_text(rule),
        "cause": rule["cause"],
        "confidence": confidence,
        "steps": rule["steps"],
        "urgent": rule["urgent"],
        "explanation": explain_facts(rule["conditions"], facts),
        "alternatives": find_alternatives(evaluations, [rule["cause"]], 2),
        "notes": build_notes(category["id"], facts),
        "trace": [{"id": r["id"], "status": e["status"]} for r, e in evaluations],
        "disclaimer": DISCLAIMER,
    }


def build_unknown(category, evaluations, facts):
    return {
        "found": False,
        "category": category,
        "rule_id": None,
        "rule_text": None,
        "cause": "The cause could not be determined confidently",
        "confidence": "Not determined",
        "steps": FALLBACK_STEPS,
        "urgent": False,
        "explanation": explain_facts(list(facts), facts),
        "alternatives": find_alternatives(evaluations, [], 3),
        "notes": build_notes(category["id"], facts),
        "trace": [{"id": r["id"], "status": e["status"]} for r, e in evaluations],
        "disclaimer": DISCLAIMER,
    }


# ---------------------------------------------------------------- main entry
def infer(category_id, answers):
    """
    Run one step of forward chaining.

    Returns one of:
      {"status": "question", "question": {...}, "number": n, "answers": [...], "category": {...}}
      {"status": "result",   "result": {...},   "answers": [...], "category": {...}}
    Raises ValueError for an unknown category.
    """
    category = get_category(category_id)
    if category is None:
        raise ValueError("Unknown category: " + str(category_id))

    answers = clean_answers(category_id, answers)
    facts = dict(answers)
    evaluations = [(rule, evaluate_rule(rule, facts)) for rule in rules_for(category_id)]

    fired = [(r, e) for r, e in evaluations if e["status"] == "fired"]
    possible = [r for r, e in evaluations if e["status"] == "possible"]

    best = max(fired, key=lambda pair: pair[0]["priority"])[0] if fired else None
    top_possible = max((r["priority"] for r in possible), default=-1)

    if best is not None and best["priority"] >= top_possible:
        result = build_diagnosis(category, best, evaluations, facts)
        return {"status": "result", "result": result, "answers": answers, "category": category}

    if possible:
        question = choose_next_question(possible, facts)
        if question is not None:
            return {"status": "question", "question": question, "number": len(answers) + 1,
                    "answers": answers, "category": category}

    result = build_unknown(category, evaluations, facts)
    return {"status": "result", "result": result, "answers": answers, "category": category}


# ----------------------------------------------------------------- self-test
def run_self_test():
    problems = []

    # 1. Every rule must be reachable by answering questions as the rule requires.
    for rule in RULES:
        answers = []
        step = None
        for _ in range(20):
            step = infer(rule["category"], answers)
            if step["status"] == "result":
                break
            qid = step["question"]["id"]
            answers.append([qid, rule["conditions"].get(qid, "no")])
        if step["status"] != "result" or step["result"]["rule_id"] != rule["id"]:
            problems.append("Rule " + rule["id"] + " is not reachable")

    # 2. Answering 'Not sure' to everything must end in the 'unknown' result.
    for category in CATEGORIES:
        answers = []
        for _ in range(20):
            step = infer(category["id"], answers)
            if step["status"] == "result":
                break
            answers.append([step["question"]["id"], "unsure"])
        if step["status"] != "result" or step["result"]["found"]:
            problems.append("Category " + category["id"] + ": 'Not sure' did not give 'unknown'")

    # 3. Bad input must be ignored, not crash.
    try:
        infer(CATEGORIES[0]["id"], [["fake", "yes"], ["x"], None, [1, 2], "abc"])
    except Exception as error:
        problems.append("Bad input crashed the engine: " + repr(error))
    try:
        infer("not_a_category", [])
        problems.append("Unknown category was not rejected")
    except ValueError:
        pass

    print("Rules checked:", len(RULES))
    print("Problems     :", problems if problems else "none")


def run_console_demo():
    """Optional: try the engine in the terminal without Flask."""
    print("Categories:")
    for number, category in enumerate(CATEGORIES, start=1):
        print(" ", number, "-", category["title"])
    choice = int(input("Choose a number: ")) - 1
    category_id = CATEGORIES[choice]["id"]
    answers = []
    while True:
        step = infer(category_id, answers)
        if step["status"] == "result":
            result = step["result"]
            print("\nMost likely cause:", result["cause"], "(" + result["confidence"] + ")")
            for number, text in enumerate(result["steps"], start=1):
                print(" ", number, text)
            print("Rule used:", result["rule_text"])
            return
        reply = input(step["question"]["text"] + " [yes/no/unsure]: ").strip().lower()
        if reply in ANSWERS:
            answers.append([step["question"]["id"], reply])


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_console_demo()
    else:
        run_self_test()
