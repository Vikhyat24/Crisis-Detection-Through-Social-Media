"""
Flask Web App for Live Crisis Detection
Accepts place name + radius, scrapes social media, runs ML classification.
Run: python app_web.py  →  Open http://localhost:5000
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crisis_detector import CrisisDetector
from utils import clean_tweet, geocode_place
from scrapers import MultiSourceScraper

# ============================================================
# Create Flask app
# ============================================================
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Global objects
detector = CrisisDetector()
scraper = MultiSourceScraper()

# Store scan results in memory
scan_state = {
    "is_scanning": False,
    "location": "",
    "radius_km": 50,
    "lat": None,
    "lon": None,
    "results": [],       # list of classified posts
    "errors": {},        # scraper errors
    "last_scan_time": None,
    "total_scanned": 0,
    "crisis_count": 0,
    "source_counts": {},
}
scan_lock = threading.Lock()


# ============================================================
# Routes
# ============================================================

@app.route("/")
def index():
    """Serve the main dashboard page"""
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def start_scan():
    """
    Start scanning a location for crisis data.
    POST body: {"location": "Chennai", "radius": 50}
    """
    data = request.get_json()
    location = data.get("location", "").strip()
    radius_km = data.get("radius", 50)

    # Validate
    if not location:
        return jsonify({"error": "Please enter a location"}), 400

    try:
        radius_km = int(radius_km)
        if radius_km < 1 or radius_km > 5000:
            radius_km = 50
    except (ValueError, TypeError):
        radius_km = 50

    if scan_state["is_scanning"]:
        return jsonify({"error": "A scan is already running. Please wait."}), 400

    # Geocode the location
    lat, lon = geocode_place(location)

    if lat is None or lon is None:
        return jsonify({
            "error": f"Could not find coordinates for '{location}'. Try a more specific name."
        }), 400

    # Start scan in background thread
    thread = threading.Thread(
        target=_run_scan,
        args=(location, lat, lon, radius_km)
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        "message": f"Scanning {location} ({radius_km}km radius)...",
        "status": "started",
        "lat": lat,
        "lon": lon,
        "radius_km": radius_km,
    })


@app.route("/api/results", methods=["GET"])
def get_results():
    """Get the latest scan results"""
    with scan_lock:
        return jsonify({
            "is_scanning": scan_state["is_scanning"],
            "location": scan_state["location"],
            "radius_km": scan_state["radius_km"],
            "lat": scan_state["lat"],
            "lon": scan_state["lon"],
            "results": scan_state["results"],
            "errors": scan_state["errors"],
            "last_scan_time": scan_state["last_scan_time"],
            "total_scanned": scan_state["total_scanned"],
            "crisis_count": scan_state["crisis_count"],
            "source_counts": scan_state["source_counts"],
        })


@app.route("/api/status", methods=["GET"])
def get_status():
    """Get scan status (lightweight, for polling)"""
    return jsonify({
        "is_scanning": scan_state["is_scanning"],
        "location": scan_state["location"],
        "total_scanned": scan_state["total_scanned"],
        "crisis_count": scan_state["crisis_count"],
        "last_scan_time": scan_state["last_scan_time"],
    })


# ============================================================
# Background scan logic
# ============================================================

def _run_scan(location, lat, lon, radius_km):
    """Run the full scrape + classify pipeline in background"""
    global scan_state

    with scan_lock:
        scan_state["is_scanning"] = True
        scan_state["location"] = location
        scan_state["radius_km"] = radius_km
        scan_state["lat"] = lat
        scan_state["lon"] = lon
        scan_state["results"] = []
        scan_state["errors"] = {}
        scan_state["crisis_count"] = 0
        scan_state["total_scanned"] = 0
        scan_state["source_counts"] = {}

    try:
        # Step 1: Scrape from all sources with geo params
        raw_posts, errors = scraper.scrape(
            location, lat=lat, lon=lon,
            radius_km=radius_km, timeout=25
        )

        with scan_lock:
            scan_state["errors"] = errors

        # Step 2: Classify each post with the ML model
        classified_results = []

        for post in raw_posts:
            text = post.get("text", "")
            cleaned = clean_tweet(text)

            if len(cleaned) < 5:
                continue

            # Run ML model prediction
            is_crisis, confidence = detector.predict(cleaned)

            classified_results.append({
                "text": text[:300],
                "cleaned_text": cleaned,
                "source": post.get("source", "unknown"),
                "timestamp": post.get("timestamp", datetime.now().isoformat()),
                "location": post.get("location", location),
                "url": post.get("url", ""),
                "is_crisis": is_crisis,
                "confidence": round(confidence, 3),
            })

        # Sort: crisis posts first, then by confidence
        classified_results.sort(
            key=lambda x: (x["is_crisis"], x["confidence"]),
            reverse=True,
        )

        # Count by source
        source_counts = {}
        for r in classified_results:
            src = r["source"]
            source_counts[src] = source_counts.get(src, 0) + 1

        # Update global state
        crisis_count = sum(1 for r in classified_results if r["is_crisis"])

        with scan_lock:
            scan_state["results"] = classified_results
            scan_state["total_scanned"] = len(classified_results)
            scan_state["crisis_count"] = crisis_count
            scan_state["source_counts"] = source_counts
            scan_state["last_scan_time"] = datetime.now().isoformat()

    except Exception as e:
        print(f"Scan error: {e}")
        with scan_lock:
            scan_state["errors"]["system"] = str(e)

    finally:
        with scan_lock:
            scan_state["is_scanning"] = False


# ============================================================
# Run the server
# ============================================================

if __name__ == "__main__":
    print("=" * 55)
    print("  Crisis Detection - Live Social Media Monitor")
    print("  Open http://localhost:5000 in your browser")
    print("=" * 55)

    # Check if ML model loaded
    info = detector.get_model_info()
    if info["model_loaded"]:
        print(f"  ML Model: {info['model_type']} loaded")
    else:
        print("  ML Model: NOT loaded (using keyword fallback)")

    print(f"  Sources: {', '.join(scraper.get_active_sources())}")
    print("=" * 55)

    app.run(debug=False, host="0.0.0.0", port=5000)
