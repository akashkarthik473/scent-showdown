import os
import random
from cs50 import SQL
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from flask_session import Session

app = Flask(__name__)


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///database.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def index():
    """Initialize the tournament and render the first matchup."""
    ids = [row["image_id"]
           for row in db.execute("SELECT image_id FROM fragrances")]

    if not ids:
        return "No fragrances found in the database.", 404

    random.shuffle(ids)

    session["remaining_ids"] = ids
    session["champion_id"] = None

    # For the first round, if we have at least 2 fragrances
    if len(ids) >= 2:
        challenger1 = session["remaining_ids"].pop()
        challenger2 = session["remaining_ids"].pop()
        # Display them; no champion yet
        return render_template("index.html", ids=[challenger1, challenger2])
    else:
        # Only one fragrance, it wins by default
        session["champion_id"] = ids[0]
        # Redirect to hall_of_fame since we have the winner
        return redirect(url_for('hall_of_fame'))


@app.route("/save_vote", methods=["POST"])
def save_vote():
    # Ensure we have a JSON request
    if not request.is_json:
        return jsonify({"error": "Unsupported Media Type: Expected JSON"}), 415

    data = request.get_json()
    voted_id = data.get("image_id")
    displayed_ids = data.get("displayed_ids")

    if not voted_id:
        return jsonify({"error": "Image ID is required"}), 400

    # Validate fragrance in DB
    image_exists = db.execute("SELECT 1 FROM fragrances WHERE image_id = ?", voted_id)
    if not image_exists:
        return jsonify({"error": "Invalid image ID"}), 400

    if not displayed_ids or len(displayed_ids) != 2:
        return jsonify({"error": "No displayed images info provided"}), 400

    old_champion = session.get("champion_id")

    # Determine the new champion
    # If no champion yet, set the voted_id as champion
    if old_champion is None:
        session["champion_id"] = voted_id
    else:
        # If we already have a champion and voted_id is different, replace the champion
        if voted_id != old_champion:
            session["champion_id"] = voted_id
        # If voted_id == old_champion, do nothing (champion stays the same)

    # Check if this was the final matchup
    if not session["remaining_ids"]:
        # Now that the final champion is determined, update the DB to record this final win
        final_champion = session["champion_id"]
        db.execute("""
            INSERT INTO wins (image_id, wins)
            VALUES (?, 1)
            ON CONFLICT(image_id) DO UPDATE SET wins = wins + 1
        """, final_champion)

        return jsonify({
            "message": "No more challengers left!",
            "final_champion": final_champion
        })

    # Otherwise, there are still challengers left
    new_challenger = session["remaining_ids"].pop()
    current_champion = session["champion_id"]

    return jsonify({
        "message": "Vote processed!",
        "next_round_ids": [current_champion, new_challenger]
    })




@app.route("/hall_of_fame")
def hall_of_fame():
    # Fetch top fragrances by their number of wins
    top_fragrances = db.execute("SELECT image_id, wins FROM wins ORDER BY wins DESC LIMIT 10")

    champion_id = session.get("champion_id")

    return render_template("hall_of_fame.html", top_fragrances=top_fragrances, champion=champion_id)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
