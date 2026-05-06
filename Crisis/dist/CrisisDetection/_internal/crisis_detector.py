import joblib
import numpy as np
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
import os


class CrisisDetector:
    """Handles crisis detection using machine learning"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_loaded = False
        self._load_default_model()
        
    def _load_default_model(self):
        """Load default pre-trained model if available"""
        # Support PyInstaller frozen paths
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        model_paths = [
            os.path.join(base_dir, "final_mlp_model.joblib"),
        ]
        
        vectorizer_paths = [
            os.path.join(base_dir, "tfidf_vectorizer.joblib"),
        ]
        
        # Try to load model
        for model_path in model_paths:
            if os.path.exists(model_path):
                try:
                    self.model = joblib.load(model_path)
                    break
                except Exception as e:
                    print(f"Failed to load model from {model_path}: {e}")
        
        # Try to load vectorizer
        for vec_path in vectorizer_paths:
            if os.path.exists(vec_path):
                try:
                    self.vectorizer = joblib.load(vec_path)
                    break
                except Exception as e:
                    print(f"Failed to load vectorizer from {vec_path}: {e}")
        
        if self.model and self.vectorizer:
            self.model_loaded = True
    
    def load_model(self, model_path, vectorizer_path=None):
        """Load a pretrained model from file"""
        try:
            self.model = joblib.load(model_path)
            
            if vectorizer_path and os.path.exists(vectorizer_path):
                self.vectorizer = joblib.load(vectorizer_path)
            
            self.model_loaded = True
            return True
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")
    
    def train_model(self, X_train, y_train, X_test=None, y_test=None):
        """Train a new crisis detection model"""
        try:
            # Vectorize text
            if self.vectorizer is None:
                self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
                X_train_vec = self.vectorizer.fit_transform(X_train)
            else:
                X_train_vec = self.vectorizer.transform(X_train)
            
            # Train model
            self.model = MLPClassifier(hidden_layer_sizes=(256, 128), max_iter=500)
            self.model.fit(X_train_vec, y_train)
            
            # Evaluate if test data provided
            if X_test is not None and y_test is not None:
                X_test_vec = self.vectorizer.transform(X_test)
                score = self.model.score(X_test_vec, y_test)
                return score
            
            self.model_loaded = True
            return True
        except Exception as e:
            raise Exception(f"Failed to train model: {str(e)}")
    
    def predict(self, text, return_probabilities=True):
        """
        Predict if text indicates a crisis
        Returns: (is_crisis: bool, confidence: float)
        """
        if not self.model_loaded:
            # Use heuristic-based detection as fallback
            return self._heuristic_detection(text)
        
        try:
            # Vectorize text
            text_vec = self.vectorizer.transform([text])
            
            # Get prediction
            prediction = self.model.predict(text_vec)[0]
            
            # Get probability
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(text_vec)[0]
                confidence = probabilities[1] if prediction == 1 else probabilities[0]
            else:
                confidence = 0.5
            
            return bool(prediction), float(confidence)
        except Exception as e:
            print(f"Prediction error: {e}")
            return self._heuristic_detection(text)
    
    def _heuristic_detection(self, text):
        """Fallback heuristic-based crisis detection"""
        crisis_keywords = [
            'emergency', 'disaster', 'flood', 'earthquake', 'fire', 'accident',
            'crisis', 'danger', 'urgent', 'help needed', 'evacuation', 'injury',
            'severe', 'affected', 'rescue', 'alert', 'storm', 'cyclone', 'danger',
            'injured', 'death', 'hospital', 'police', 'ambulance', 'urgent',
            'critical', 'emergency', 'serious', 'severe', 'devastating'
        ]
        
        text_lower = text.lower()
        
        # Count crisis keyword matches
        crisis_count = sum(1 for keyword in crisis_keywords if keyword in text_lower)
        
        # Calculate confidence based on keyword matches
        confidence = min(crisis_count / 3.0, 1.0)  # Normalize to 0-1
        
        # Mark as crisis if confidence > 0.3
        is_crisis = confidence > 0.3
        
        return is_crisis, confidence
    
    def batch_predict(self, texts):
        """Predict crisis status for multiple texts"""
        predictions = []
        for text in texts:
            is_crisis, confidence = self.predict(text)
            predictions.append({
                'text': text,
                'is_crisis': is_crisis,
                'confidence': confidence
            })
        return predictions
    
    def save_model(self, model_path, vectorizer_path=None):
        """Save the trained model to file"""
        if self.model:
            joblib.dump(self.model, model_path)
        
        if self.vectorizer and vectorizer_path:
            joblib.dump(self.vectorizer, vectorizer_path)
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            'model_loaded': self.model_loaded,
            'model_type': type(self.model).__name__ if self.model else None,
            'vectorizer_type': type(self.vectorizer).__name__ if self.vectorizer else None,
        }
