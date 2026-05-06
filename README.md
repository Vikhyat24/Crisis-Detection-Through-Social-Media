# Real-time Crisis Detection Model Using Social Media Posts

**📊 [Project Presentation](https://docs.google.com/presentation/d/1XSLAchbDEVoZfpL5zJNJKuibveE-X8EHiaOoiQatR94/)**

## Overview

An AI-powered tool that analyzes real-time social media posts to detect crisis events like riots, civil unrest, and natural disasters, providing live information to people in affected areas. This system combines machine learning with real-time data collection using Selenium to enhance situational awareness during emergency situations.

## Project Structure

```
├── README.md                                       # Project documentation
├── Crisis_Detection_Comprehensive_Report.md        # Technical report
├── Crisis_Detection_Social_Media.ipynb              # Main project notebook with ML models
├── Interface.ipynb                                  # Data extraction logic and user interface
├── run_app.bat                                      # Windows launcher for web dashboard
│
└── Crisis/                                          # Application code
    ├── app_web.py                                   # Flask web dashboard (main app)
    ├── app.py                                       # Tkinter desktop GUI
    ├── crisis_detector.py                           # ML model loading & prediction
    ├── map_visualizer.py                            # Folium map generation
    ├── social_collector.py                          # Sample data generator
    ├── utils.py                                     # Text cleaning & geocoding
    ├── config.py                                    # Configuration constants
    ├── run.py                                       # Smart launcher for desktop GUI
    ├── requirements.txt                             # Python dependencies
    ├── final_mlp_model.joblib                       # Trained MLP model (92.68% F1)
    ├── tfidf_vectorizer.joblib                      # TF-IDF vectorizer
    ├── cleaned_tweets_data_with_punctuation.csv     # Preprocessed dataset
    ├── latest_tweets_data.csv                       # Most recent scraped post data
    ├── templates/index.html                         # Web dashboard HTML
    ├── static/style.css                             # Web dashboard CSS
    ├── static/app.js                                # Web dashboard JavaScript
    └── scrapers/                                    # Multi-source data scrapers
        ├── __init__.py                              # Scraper orchestrator
        ├── reddit_scraper.py                        # Reddit JSON API
        ├── gdelt_scraper.py                         # GDELT news API
        ├── news_scraper.py                          # Google News RSS
        ├── bluesky_scraper.py                       # Bluesky AT Protocol
        ├── twitter_scraper.py                       # Twitter/X (Selenium)
        ├── instagram_scraper.py                     # Instagram (Selenium)
        └── threads_scraper.py                       # Meta Threads (Selenium)
```

## Key Features

- **Real-time Post Analysis**: Continuous monitoring and classification of posts for crisis detection
- **High Accuracy**: Machine learning model achieving 92.68% F1-score in crisis/non-crisis classification
- **Multiple Model Support**: Ensemble methods, neural networks, and deep learning models
- **Advanced Feature Engineering**: TF-IDF vectorization with dimensionality reduction options
- **GPS-based Filtering**: Location-aware crisis detection for targeted alerts
- **Interactive Map Interface**: Visual representation of crisis events with geographic context
- **Automated Data Collection**: Selenium-powered post scraping for real-time data ingestion
- **Multi-model Ensemble**: Combines multiple ML algorithms for improved reliability

## Interface
![Crisis Detection Model](https://drive.google.com/uc?id=1Cw_TOs-ff7B9pPknGoNjyWJJQq1wj_AY)

## Model Performance

| Model | Embedding | F1-Score | Performance Notes |
|-------|-----------|----------|-------------------|
| **MLP** | TF-IDF | **92.68%** | Best overall performance |
| **Random Forest** | TF-IDF | **92.24%** | Top ensemble method |
| **SVM** | TF-IDF | **91.43%** | Robust high-dimensional classifier |
| **XGBoost** | TF-IDF | **91.11%** | Efficient gradient boosting |
| **Logistic Regression** | TF-IDF | **91.07%** | Strong baseline performance |
| **Decision Tree** | TF-IDF | **90.87%** | Good non-linear pattern capture |
| **CNN** | TF-IDF | **89.68%** | Deep learning approach |

## Data Preprocessing

### Text Cleaning Pipeline
1. **Noise Removal**: Eliminates mentions, hashtags, URLs, and emojis
2. **Normalization**: Converts to lowercase and removes special characters
3. **Stopword Removal**: Filters out common non-informative words
4. **Lemmatization**: Reduces words to their base forms
5. **TF-IDF Vectorization**: Converts text to numerical features

## Deployment

### Development Workflow
```bash
# 1. Data Collection
# Run Interface.ipynb to collect new post data

# 2. Model Training
# Run Crisis_Detection_Social_Media.ipynb to train/update models

# 3. Real-time Monitoring
# Use trained models for live crisis detection

# 4. Visualization
# Generate updated maps and visualizations
```

### Production Considerations
- Model retraining with new data
- Performance monitoring and validation
- Scalability for high-volume processing
- Integration with alerting systems

## File Descriptions

### Core Files

- **`Interface.ipynb`**: Contains the data extraction logic and user interface for the crisis detection system. This notebook handles:
  - Post data collection using Selenium and preprocessing
  - Real-time data extraction workflows
  - User interface components for interaction

- **`Crisis_Detection_Social_Media.ipynb`**: Main project notebook containing:
  - Machine learning model implementations
  - Model training and evaluation
  - Feature engineering and text preprocessing
  - Performance comparisons across different algorithms

- **`ML_Project.pdf`**: Comprehensive project report documenting:
  - Project methodology and approach
  - Model architecture and design decisions
  - Results and performance analysis
  - Conclusions and future work

### Data Files

- **`cleaned_tweets_data_with_punctuation.csv`**: Primary dataset containing:
  - Preprocessed post text with punctuation preserved
  - Crisis/non-crisis labels
  - Additional metadata and features

- **`latest_tweets_data.csv`**: Most recent post data collected from:
  - Real-time scraping operations
  - Location-based filtering
  - Current crisis monitoring

### Model Files

- **`final_mlp_model.joblib`**: Serialized Multi-Layer Perceptron model
  - Best performing model (92.68% F1-score)
  - Trained on TF-IDF features
  - Ready for real-time inference

- **`tfidf_vectorizer.joblib`**: Pre-trained TF-IDF vectorizer
  - Feature extraction for text data
  - Consistent preprocessing pipeline
  - Required for model inference

### Visualization

- **`cleaned_tweets_map.html`**: Interactive map visualization showing:
  - Geographic distribution of crisis events
  - Location-based crisis intensity
  - Interactive filtering and exploration

## Technical Architecture

### Machine Learning Models
- **MLP (Multi-Layer Perceptron)**: Best neural network model (92.68% F1-score)
- **Random Forest**: Top-performing ensemble method (92.24% F1-score)
- **Support Vector Machine**: High-performance classifier (91.43% F1-score)
- **XGBoost**: Gradient boosting for complex pattern recognition (91.11% F1-score)
- **CNN**: Deep learning model for spatial feature extraction (89.68% F1-score)
- **Logistic Regression**: Baseline linear classifier (91.07% F1-score)

### Data Processing Pipeline
1. **Data Collection**: Automated post scraping using Selenium
2. **Text Preprocessing**: Cleaning, normalization, and tokenization
3. **Feature Engineering**: TF-IDF vectorization and dimensionality reduction
4. **Model Training**: Hyperparameter optimization and cross-validation
5. **Real-time Classification**: Live tweet analysis and crisis detection
6. **Visualization**: Interactive mapping and result presentation

## Dataset

The model is trained on a comprehensive dataset of 247,000 tweets:
- **Crisis tweets**: 129,000 samples
- **Non-crisis tweets**: 118,000 samples
- **Sources**: Multiple publicly available datasets including disaster-related tweets

## Installation

### Prerequisites
- Python 3.8+
- Jupyter Notebook/Lab
- Chrome browser (for Selenium scraping)
- ChromeDriver compatible with your Chrome version

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd crisis-detection-model

# Install required packages
pip install pandas numpy scikit-learn joblib matplotlib seaborn
pip install selenium beautifulsoup4 requests
pip install folium plotly
pip install xgboost tensorflow keras
pip install nltk textblob

# Download NLTK data
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt')"
```

## Usage

### Running the Main Project
```bash
# Start Jupyter Notebook
jupyter notebook

# Open and run the main project notebook
# 1. Open ML_Project_Tweet_Detection.ipynb
# 2. Run all cells to train models and evaluate performance
# 3. Use Interface.ipynb for data extraction and real-time monitoring
```

### Loading Pre-trained Models
```python
import joblib
import pandas as pd

# Load the trained model and vectorizer
model = joblib.load('final_mlp_model.joblib')
vectorizer = joblib.load('tfidf_vectorizer.joblib')

# Load and process new data
new_tweets = pd.read_csv('latest_tweets_data.csv')

# Transform text data
X_new = vectorizer.transform(new_tweets['text'])

# Make predictions
predictions = model.predict(X_new)
probabilities = model.predict_proba(X_new)
```

### Interactive Map Visualization
```python
# Open cleaned_tweets_map.html in a web browser
# Or use Python to display in Jupyter
from IPython.display import IFrame
IFrame('cleaned_tweets_map.html', width=800, height=600)
```

## Limitations

- **Language Support**: Currently optimized for English tweets
- **Data Dependencies**: Requires consistent data format and quality
- **Model Drift**: Performance may degrade over time without retraining
- **Geographic Coverage**: Limited by availability of location data
- **Real-time Constraints**: Processing speed vs. accuracy trade-offs

## Future Enhancements

- Multi-language support for global coverage
- Advanced transformer models (BERT, GPT-based)
- Real-time dashboard with live updates
- Mobile application for crisis alerts
- Integration with emergency response systems
- Improved deep learning architectures
- Ensemble methods combining top models

## Research References

This project builds upon key research contributions:
- **Ashktorab et al. (2014)**: Tweedr system for disaster tweet classification
- **Chaudhari & Govilkar (2015)**: ML techniques for sentiment classification
- **Nguyen et al. (2016)**: CNN-based disaster tweet classification


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- **Vikhyat Lamba** - vikhyat@example.com

## Acknowledgments

- Dataset contributors and open-source community
- IIIT Delhi for academic support
- Research contributions from the academic community
- Open-source libraries and frameworks

## Support

For questions, issues, or contributions, please contact the development team or create an issue in the repository.

---

**Note**: This is a research project developed for educational purposes. For production deployment in emergency response systems, additional validation, testing, and integration with official emergency services would be required.