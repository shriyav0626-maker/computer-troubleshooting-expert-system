# Computer Troubleshooting Expert System

A web-based, rule-based (knowledge-based) AI expert system that diagnoses common computer
problems by asking questions and applying IF-THEN rules. Built with Python and Flask.

> This is a traditional expert system. It is **not** a trained machine-learning model and
> does not use generative AI, paid APIs, or a database.

## Features
- 10 problem categories and 45 IF-THEN rules
- One question at a time (Yes / No / Not sure), with Back and Restart
- Final diagnosis with confidence, numbered steps, alternative causes, and an explanation
- "Cannot determine confidently" result for unknown symptoms
- Safety warnings for smoke, burning smells, overheating damage, and swollen batteries
- Responsive design (desktop and mobile)

## Expert system components
| Component | File |
|---|---|
| Knowledge base (categories, questions, rules, solutions) | `knowledge_base.py` |
| Inference engine (forward chaining) and explanation facility | `engine.py` |
| User interface | `templates/`, `static/` |
| Web controller | `app.py` |

## How it reasons (forward chaining)
After every answer, the engine checks each rule of the chosen category against the known
facts. A rule is *fired* (all conditions match), *ruled out* (a condition does not match),
or *possible* (more answers needed). It asks the next question of the most important
possible rule, and stops when a fired rule has the highest priority. If nothing fits,
it reports that the cause cannot be determined.

## Run on Windows (VS Code terminal)
Open this folder in VS Code, open a terminal (Terminal > New Terminal), then:

```
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 in a browser. Stop the server with Ctrl+C.

If PowerShell blocks activation, run
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again.
Alternatively, double-click `run.bat` to do all of this automatically.

## Self-tests
```
python knowledge_base.py
python engine.py
```
Expected: 45 rules, no problems. `python engine.py demo` runs the engine in the terminal.

## Project structure
```
computer-troubleshooting-expert-system/
    app.py
    knowledge_base.py
    engine.py
    requirements.txt
    run.bat
    README.md
    templates/  base.html, index.html, troubleshoot.html, result.html
    static/     css/style.css, js/script.js
```

## Limitations
- Suggestions are possible causes, not guaranteed diagnoses.
- The system only knows the rules in its knowledge base.
- It cannot inspect the computer; it relies on the user's answers.
- Answering "Not sure" cannot confirm a condition, so it usually leads to the
  "cannot determine" result.
- For local use: before putting it online, set a random secret key, use debug=False,
  and add CSRF protection.
