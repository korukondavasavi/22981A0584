from flask import Flask, request, jsonify, redirect
from datetime import datetime, timedelta
from db import init_db, get_db
from logger_middleware import setup_logger
from utils import generate_shortcode, is_valid_url
import sqlite3

app = Flask(__name__)
setup_logger(app)
init_db()

@app.route('/shorturls', methods=['POST'])
def create_short_url():
    data = request.json
    url = data.get("url")
    validity = data.get("validity", 30)
    shortcode = data.get("shortcode")

    if not url or not is_valid_url(url):
        return jsonify({"error": "Invalid or missing URL"}), 400

    if not shortcode:
        shortcode = generate_shortcode()
    
    expiry = datetime.utcnow() + timedelta(minutes=validity)

    db = get_db()
    try:
        db.execute(
            "INSERT INTO urls (shortcode, url, expiry, created_at) VALUES (?, ?, ?, ?)",
            (shortcode, url, expiry.isoformat(), datetime.utcnow().isoformat())
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Shortcode already exists"}), 409

    return jsonify({
        "shortLink": f"http://hostname:port/{shortcode}",
        "expiry": expiry.isoformat()
    }), 201

@app.route('/<shortcode>', methods=['GET'])
def redirect_url(shortcode):
    db = get_db()
    row = db.execute(
        "SELECT url, expiry FROM urls WHERE shortcode = ?", (shortcode,)
    ).fetchone()
    
    if not row:
        return jsonify({"error": "Shortcode does not exist"}), 404

    url, expiry = row
    if datetime.fromisoformat(expiry) < datetime.utcnow():
        return jsonify({"error": "Link has expired"}), 410

    # Track click
    db.execute("INSERT INTO clicks (shortcode, timestamp) VALUES (?, ?)", (shortcode, datetime.utcnow().isoformat()))
    db.commit()

    return redirect(url)

@app.route('/shorturls/<shortcode>', methods=['GET'])
def get_stats(shortcode):
    db = get_db()
    url_row = db.execute(
        "SELECT url, created_at, expiry FROM urls WHERE shortcode = ?", (shortcode,)
    ).fetchone()

    if not url_row:
        return jsonify({"error": "Shortcode not found"}), 404

    click_rows = db.execute(
        "SELECT timestamp FROM clicks WHERE shortcode = ?", (shortcode,)
    ).fetchall()

    return jsonify({
        "url": url_row[0],
        "created_at": url_row[1],
        "expiry": url_row[2],
        "clicks": len(click_rows),
        "click_details": [dict(timestamp=row[0]) for row in click_rows]
    })

if __name__ == '_main_':
    app.run(debug=True)