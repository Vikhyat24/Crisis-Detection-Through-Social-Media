import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Initialize
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Compile regex patterns for optimization
url_pattern = re.compile(r'http\S+|www\S+|https\S+')
mention_pattern = re.compile(r'@\w+')
hashtag_pattern = re.compile(r'#\w+')
emoji_pattern = re.compile(r'[\U00010000-\U0010FFFF]')
special_char_pattern = re.compile(r'[^A-Za-z\s]')
whitespace_pattern = re.compile(r'\s+')


def clean_tweet(text):
    """
    Clean tweet text - remove URLs, mentions, special characters
    but keep basic punctuation
    """
    if not isinstance(text, str):
        return ""
    
    try:
        # Remove URLs
        text = url_pattern.sub("", text)
        
        # Remove mentions (@username)
        text = mention_pattern.sub("", text)
        
        # Remove hashtags symbols but keep the text
        text = hashtag_pattern.sub("", text)
        
        # Remove emojis
        text = emoji_pattern.sub("", text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = whitespace_pattern.sub(" ", text).strip()
        
        return text
        
    except Exception as e:
        print(f"Error cleaning tweet: {e}")
        return ""


def preprocess_tweet(text):
    """
    Preprocess tweet for ML model - lemmatization and stopword removal
    """
    if not isinstance(text, str):
        return ""
    
    try:
        # Remove special characters and numbers
        text = special_char_pattern.sub("", text)
        
        # Split into words
        words = text.split()
        
        # Remove stopwords
        words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Lemmatize
        words = [lemmatizer.lemmatize(word) for word in words]
        
        return " ".join(words)
        
    except Exception as e:
        print(f"Error preprocessing tweet: {e}")
        return ""


def extract_location(text):
    """Extract location patterns from text"""
    # Common location patterns
    location_keywords = [
        'tamil nadu', 'maharashtra', 'delhi', 'karnataka', 'kerala', 'punjab',
        'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata',
        'india', 'state', 'city', 'area', 'region', 'district'
    ]
    
    text_lower = text.lower()
    found_locations = [loc for loc in location_keywords if loc in text_lower]
    
    return found_locations


def extract_urgency_level(text, confidence):
    """Determine urgency level based on text and confidence"""
    urgent_keywords = [
        'emergency', 'immediate', 'urgent', 'now', 'asap', 'critical',
        'severe', 'dangerous', 'help', 'rescue', 'evacuate'
    ]
    
    text_lower = text.lower()
    keyword_count = sum(1 for keyword in urgent_keywords if keyword in text_lower)
    
    # Combine keyword count and model confidence
    urgency_score = (keyword_count * 0.2) + (confidence * 0.8)
    
    if urgency_score >= 0.8:
        return "CRITICAL"
    elif urgency_score >= 0.6:
        return "HIGH"
    elif urgency_score >= 0.4:
        return "MEDIUM"
    else:
        return "LOW"


def validate_coordinates(latitude, longitude):
    """Validate if coordinates are within valid ranges"""
    try:
        lat = float(latitude)
        lon = float(longitude)
        
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return True, lat, lon
        else:
            return False, None, None
    except (ValueError, TypeError):
        return False, None, None


def format_timestamp(timestamp):
    """Format timestamp for display"""
    try:
        from datetime import datetime
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp)
        else:
            dt = timestamp
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(timestamp)


def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    from math import radians, cos, sin, asin, sqrt
    
    try:
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371
        return c * r
    except Exception:
        return None


def batch_clean_tweets(tweets):
    """Clean a batch of tweets"""
    cleaned = []
    for tweet in tweets:
        if isinstance(tweet, dict):
            tweet_text = tweet.get('Tweet', tweet.get('Cleaned_Tweet', ''))
        else:
            tweet_text = str(tweet)
        
        cleaned_text = clean_tweet(tweet_text)
        cleaned.append(cleaned_text)
    
    return cleaned


def batch_preprocess_tweets(tweets):
    """Preprocess a batch of tweets"""
    preprocessed = []
    for tweet in tweets:
        if isinstance(tweet, dict):
            tweet_text = tweet.get('Tweet', tweet.get('Cleaned_Tweet', ''))
        else:
            tweet_text = str(tweet)
        
        preprocessed_text = preprocess_tweet(clean_tweet(tweet_text))
        preprocessed.append(preprocessed_text)
    
    return preprocessed


def get_statistics(tweets_data):
    """Calculate statistics from tweets data"""
    stats = {
        'total_tweets': len(tweets_data),
        'unique_locations': 0,
        'avg_confidence': 0,
        'crisis_tweets': 0,
        'normal_tweets': 0
    }
    
    if not tweets_data:
        return stats
    
    # Count unique locations
    locations = set()
    total_confidence = 0
    crisis_count = 0
    
    for tweet in tweets_data:
        if 'Geolocation' in tweet:
            locations.add(tweet['Geolocation'])
        
        if tweet.get('Prediction', 0) == 1:
            crisis_count += 1
            confidence = tweet.get('Confidence', 0)
            total_confidence += confidence
    
    stats['unique_locations'] = len(locations)
    stats['crisis_tweets'] = crisis_count
    stats['normal_tweets'] = len(tweets_data) - crisis_count
    
    if crisis_count > 0:
        stats['avg_confidence'] = total_confidence / crisis_count
    
    return stats


def format_for_export(tweets_data):
    """Format tweets data for export"""
    export_data = []
    
    for idx, tweet in enumerate(tweets_data, 1):
        export_item = {
            'ID': idx,
            'Tweet': tweet.get('Tweet', ''),
            'Cleaned_Tweet': tweet.get('Cleaned_Tweet', ''),
            'Location': tweet.get('Geolocation', ''),
            'Is_Crisis': tweet.get('Prediction', 0),
            'Confidence': tweet.get('Confidence', 0),
            'Timestamp': tweet.get('Timestamp', '')
        }
        export_data.append(export_item)
    
    return export_data


def geocode_place(place_name):
    """
    Get coordinates for a place name using OpenStreetMap Nominatim API
    Returns: (latitude, longitude) or (None, None)
    """
    import requests
    
    try:
        base_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": place_name,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "CrisisDetectionApp/1.0"
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
                
        return None, None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None
