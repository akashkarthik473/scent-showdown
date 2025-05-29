import os
import random
from cs50 import SQL
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///fragrances.db")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET"])
def index():
    """Start a new tournament"""
    fragrances = db.execute("SELECT id, name, image_url FROM fragrances")
    print(f"Number of fragrances found: {len(fragrances)}")  # Debug line
    print(f"Fragrances: {fragrances}")  # Debug line
    
    if len(fragrances) < 2:
        return "Not enough fragrances in the database.", 404

    random.shuffle(fragrances)
    session["remaining"] = fragrances
    session["champion"] = None

    challenger1 = session["remaining"].pop()
    challenger2 = session["remaining"].pop()

    return render_template("index.html", options=[challenger1, challenger2])

@app.route("/save_vote", methods=["POST"])
def save_vote():
    if not request.is_json:
        return jsonify({"error": "Expected JSON request"}), 415

    data = request.get_json()
    voted_id = data.get("voted_id")
    displayed_ids = data.get("displayed_ids")

    if not voted_id or not displayed_ids or len(displayed_ids) != 2:
        return jsonify({"error": "Invalid input data"}), 400

    # Validate ID
    valid = db.execute("SELECT 1 FROM fragrances WHERE id = ?", voted_id)
    if not valid:
        return jsonify({"error": "Invalid fragrance ID"}), 400

    old_champion = session.get("champion")
    if old_champion is None:
        session["champion"] = db.execute("SELECT * FROM fragrances WHERE id = ?", voted_id)[0]
    else:
        if voted_id != old_champion["id"]:
            session["champion"] = db.execute("SELECT * FROM fragrances WHERE id = ?", voted_id)[0]

    if not session["remaining"]:
        final_id = session["champion"]["id"]
        db.execute("""
            INSERT INTO wins (id, wins)
            VALUES (?, 1)
            ON CONFLICT(id) DO UPDATE SET wins = wins + 1
        """, final_id)
        return jsonify({
            "message": "Tournament complete.",
            "final_champion": session["champion"]
        })

    next_challenger = session["remaining"].pop()
    return jsonify({
        "message": "Next round.",
        "next_round": [session["champion"], next_challenger]
    })

@app.route("/hall_of_fame")
def hall_of_fame():
    results = db.execute("""
        SELECT f.id, f.name, f.image_url, w.wins
        FROM wins w
        JOIN fragrances f ON f.id = w.id
        ORDER BY w.wins DESC
        LIMIT 10
    """)
    champion = session.get("champion")
    return render_template("hall_of_fame.html", top_fragrances=results, champion=champion)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
