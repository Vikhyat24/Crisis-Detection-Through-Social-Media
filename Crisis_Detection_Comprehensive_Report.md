# Crisis Detection Through Social Media
## Comprehensive Project Documentation & Technical Report

**Author:** Vikhyat  
**System Version:** 1.0 (Live Monitoring Enabled)  

---

## Table of Contents
1. [Project Overview & Objectives](#1-project-overview--objectives)
2. [Technology Stack & Dependencies](#2-technology-stack--dependencies)
3. [System Architecture & Pipeline](#3-system-architecture--pipeline)
4. [Data Collection Subsystem (Scrapers)](#4-data-collection-subsystem-scrapers)
5. [NLP Data Processing Pipeline](#5-nlp-data-processing-pipeline)
6. [Machine Learning Engine](#6-machine-learning-engine)
7. [Mapping & Visualization](#7-mapping--visualization)
8. [User Interfaces (GUI & Web Dashboard)](#8-user-interfaces-gui--web-dashboard)
9. [Step-by-Step Execution Guide](#9-step-by-step-execution-guide)

---

## 1. Project Overview & Objectives
The **Crisis Detection Through Social Media** project is an AI-powered system designed to analyze real-time text from various online platforms to detect crisis events such as riots, civil unrest, natural disasters, floods, and earthquakes. By monitoring live data, the system provides real-time information to affected people and emergency responders, significantly enhancing situational awareness.

**Core Objective:** To build a scalable, multi-source ingestion engine that applies Natural Language Processing (NLP) and Machine Learning (ML) to classify whether a text update constitutes a "Crisis" or "Non-Crisis", and plots these alerts on an interactive geographical map.

---

## 2. Technology Stack & Dependencies
The project relies on a robust open-source Python stack. 

*   **Core Programming Language:** Python 3.8+
*   **Machine Learning & NLP:**
    *   `scikit-learn` - For ML algorithms (MLP, Random Forest) and TF-IDF Text Vectorization.
    *   `nltk` (Natural Language Toolkit) - Used for stopword removal, lemmatization, and text cleaning.
    *   `joblib` - For serializing and deserializing the trained models.
*   **Data Collection (Scraping):**
    *   `requests` & `beautifulsoup4` - For REST API interactions.
    *   `selenium` - Used for browser automation (bypassing Twitter scraping restrictions).
    *   `feedparser` - For handling RSS News feeds (Google News).
*   **Data Manipulation & Visualization:**
    *   `pandas` - Data structuring and matrix manipulation.
    *   `folium` & `branca` - Generating interactive maps and heatmaps based on Leaflet.js.
*   **User Interfaces:**
    *   `tkinter` - Desktop GUI.
    *   `Flask` - Python web-framework serving the Live Web Dashboard.

---

## 3. System Architecture & Pipeline
The system operates in a multi-stage pipeline designed for both batch processing and live event streams:

1.  **Data Ingestion:** The `MultiSourceScraper` triggers concurrent threads to fetch text data from Twitter, Reddit, GDELT, Bluesky, and News RSS for a specific geolocation target.
2.  **Cleaning & Preprocessing:** Incoming unstructured text is cleaned using Regex patterns and NLTK to remove noise (URLs, emojis, etc.) and stopwords, and then lemmatized.
3.  **Feature Engineering:** Cleaned text is transformed into a numerical vector using a pre-trained TF-IDF Vectorizer.
4.  **Classification:** The matrix is fed into a trained Multi-Layer Perceptron (MLP) Neural Network which outputs a binary class (Crisis / Normal) alongside a Confidence Score (0.0 to 1.0).
5.  **Post-processing & Geocoding:** Crises are tagged with geographical coordinates.
6.  **Visualization & Feed:** Data is pushed to a Folium Engine that generates HTML maps (Markers & Heatmaps) and reflects on the GUI.

---

## 4. Data Collection Subsystem (Scrapers)
A notable feature of this project is its robust `MultiSourceScraper` module (located in `Crisis/scrapers/`). This implements threaded scraping across five distinct sources simultaneously.

*   **Twitter Scraper (Selenium):** Uses Headless Chrome via Selenium to automate a browser session, passing a custom user-agent to query Crisis keywords combined with the location name on X.com search. Falls back to Nitter instances if blocked.
*   **Reddit Scraper:** Queries Reddit's public JSON interface without OAuth, searching the last 24 hours of posts matching the target location and crisis keywords across all subreddits.
*   **GDELT Scraper:** Uses the Global Database of Events, Language, and Tone (GDELT) DOC 2.0 API to fetch global news intelligence about localized disasters.
*   **News RSS Scraper:** Relies on the `feedparser` library to digest the Google News RSS feed for the location query.
*   **Bluesky Scraper:** Leverages Bluesky's open AT Protocol API to fetch high-quality, chronological posts without authentication limitations.

---

## 5. NLP Data Processing Pipeline
Once text is sourced, it passes through `utils.py`. The NLP steps involve:
1.  **Regex Filtering:** Removing URLs, Mentions (@), Hashtag symbols (#), Emojis, and Special Characters.
2.  **Tokenization & Normalization:** Converting to lowercase and splitting strings by whitespace.
3.  **Stopword Removal:** Using `nltk.corpus.stopwords` to drop non-informative common words ('the', 'is', 'at').
4.  **Lemmatization:** Converting words to their root semantic origin using `WordNetLemmatizer` (e.g., 'running' -> 'run').

---

## 6. Machine Learning Engine
The `crisis_detector.py` module handles the ML core.

*   **Vectorization (TF-IDF):** The model uses a Term Frequency-Inverse Document Frequency Vectorizer trained on up to 5,000 max features, with an n-gram range of (1, 2).
*   **Final Model (MLP):** The best performer was the **Multi-Layer Perceptron (MLP Neural Network)** achieving a **92.68% F1-Score** over a dataset of 247,000 tweets. The MLP uses two hidden layers sized (256, 128) optimized using ADAM.
*   **Fallback Heuristics:** If the model files (`final_mlp_model.joblib`) are missing, the system dynamically switches to heuristic detection testing 30 predefined crisis keywords.

---

## 7. Mapping & Visualization
The `MapVisualizer` leverages **Folium** to generate interactive HTML maps natively in Python:
*   **Crisis Markers Map (`crisis_map.html`):** Point markers are color-coded (Red > 80% confidence, Orange > 60%, Yellow < 60%) with HTML Popups.
*   **Crisis Heatmap (`crisis_heatmap.html`):** Uses Folium's `HeatMap` plugin, assigning the ML Confidence Score as the 'intensity' of a coordinate.

---

## 8. User Interfaces (GUI & Web Dashboard)

### Tkinter Desktop Application (`app.py`)
Builds a robust Desktop GUI with tabs for:
*   **Data Collector:** Defining Latitude, Longitude, Radius, and Place Name.
*   **Crisis Detector:** Setting Confidence Thresholds and batch executing ML scans.
*   **Map & Visualization:** Exporting custom folium maps directly.
*   **Results:** Exporting generated tables to CSV.

### Live Flask Web App (`app_web.py`)
Spins up a local server routing an asynchronous dashboard on `localhost:5000`. Users enter a city name, and a background threaded scan launches all scrapers, classifies live texts, dynamically geocodes the region via OpenStreetMap Nominatim, and automatically renders a scrolling feed side-by-side with a live crisis map.

---

## 9. Step-by-Step Execution Guide

### Option A: The Automated Starter Menu
```bash
python run.py
```
The `run.py` script is a smart launcher that installs dependencies, downloads NLTK corpora, ensures the models are present, and boots the Tkinter Desktop Application.

### Option B: The Live Web Application
```bash
# 1. Activate your environment
.\.venv\Scripts\activate

# 2. Run the Flask Web Server
python Crisis/app_web.py

# 3. Open your browser
# Navigate to: http://localhost:5000
```
