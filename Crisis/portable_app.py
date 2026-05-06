"""
Portable Crisis Detection System — PyInstaller Entry Point
This wrapper handles frozen (exe) vs normal (python) execution paths.
Double-click the exe → browser opens → dashboard ready.
"""

import os
import sys
import webbrowser
import threading
import time

# ============================================================
# Path Resolution for PyInstaller
# ============================================================

def get_base_dir():
    """Get the base directory whether running as script or frozen exe"""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return sys._MEIPASS
    else:
        # Running as normal script
        return os.path.dirname(os.path.abspath(__file__))

def get_app_dir():
    """Get the directory where the exe lives (for runtime files)"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# Set up paths BEFORE importing anything else
BASE_DIR = get_base_dir()
APP_DIR = get_app_dir()

# Add base dir to Python path so imports work
sys.path.insert(0, BASE_DIR)

# Set NLTK data path to bundled data
nltk_data_path = os.path.join(BASE_DIR, 'nltk_data')
if os.path.exists(nltk_data_path):
    os.environ['NLTK_DATA'] = nltk_data_path

# ============================================================
# Now import the actual app modules
# ============================================================

from flask import Flask, render_template, request, jsonify
import threading
from datetime import datetime

from crisis_detector import CrisisDetector
from utils import clean_tweet, geocode_place
from scrapers import MultiSourceScraper

# ============================================================
# Create Flask app with correct template/static paths
# ============================================================

template_dir = os.path.join(BASE_DIR, 'templates')
static_dir = os.path.join(BASE_DIR, 'static')

app = Flask(__name__,
            template_folder=template_dir,
            static_folder=static_dir)
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
    "results": [],
    "errors": {},
    "last_scan_time": None,
    "total_scanned": 0,
    "crisis_count": 0,
    "source_counts": {},
}
scan_lock = threading.Lock()


# ============================================================
# Routes (identical to app_web.py)
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scan", methods=["POST"])
def start_scan():
    data = request.get_json()
    location = data.get("location", "").strip()
    radius_km = data.get("radius", 50)

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

    lat, lon = geocode_place(location)

    if lat is None or lon is None:
        return jsonify({
            "error": f"Could not find coordinates for '{location}'. Try a more specific name."
        }), 400

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
        raw_posts, errors = scraper.scrape(
            location, lat=lat, lon=lon,
            radius_km=radius_km, timeout=25
        )

        with scan_lock:
            scan_state["errors"] = errors

        classified_results = []

        for post in raw_posts:
            text = post.get("text", "")
            cleaned = clean_tweet(text)

            if len(cleaned) < 5:
                continue

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

        classified_results.sort(
            key=lambda x: (x["is_crisis"], x["confidence"]),
            reverse=True,
        )

        source_counts = {}
        for r in classified_results:
            src = r["source"]
            source_counts[src] = source_counts.get(src, 0) + 1

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
# Auto-open browser
# ============================================================

def open_browser():
    """Open the dashboard in the default browser after a short delay"""
    time.sleep(1.5)
    webbrowser.open("http://localhost:5000")


# ============================================================
# Main entry point
# ============================================================

if __name__ == "__main__":
    print()
    print("=" * 55)
    print("  CRISIS DETECTION SYSTEM - Portable Edition")
    print("=" * 55)
    print(f"  Dashboard: http://localhost:5000")
    print(f"  Press Ctrl+C to stop the server")
    print("=" * 55)

    info = detector.get_model_info()
    if info["model_loaded"]:
        print(f"  ML Model: {info['model_type']} loaded [OK]")
    else:
        print("  ML Model: Using keyword fallback")

    print(f"  Sources: {', '.join(scraper.get_active_sources())}")
    print("=" * 55)
    print()

    # Auto-open browser
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Flask
    try:
        app.run(debug=False, host="127.0.0.1", port=5000)
    except KeyboardInterrupt:
        print("\nServer stopped.")
