import pandas as pd
import os
from datetime import datetime, timedelta
import random


class SocialCollector:
    """Handles social media post collection from various sources"""
    
    def __init__(self):
        self.posts = []
        self.last_collection_time = None
        
    def get_sample_posts(self, count=50, center_lat=24.7941004, center_lon=93.1170986):
        """Generate sample posts for demonstration"""
        crisis_keywords = [
            "emergency", "disaster", "flood", "earthquake", "fire", "accident",
            "crisis", "danger", "urgent", "help needed", "evacuation", "injury",
            "severe", "affected", "rescue", "alert", "alert", "storm", "cyclone"
        ]
        
        normal_keywords = [
            "weather", "sunny", "nice day", "work", "meeting", "lunch",
            "happy", "excited", "weekend", "travel", "shopping", "cooking"
        ]
        
        sample_posts = []
        
        for i in range(count):
            # Mix crisis and normal posts
            is_crisis = random.random() < 0.3  # 30% crisis posts
            
            if is_crisis:
                keywords = random.choice(crisis_keywords)
                post_text = f"URGENT: {keywords} in the area. Please take precautions. {random.choice(['Stay safe', 'Call authorities', 'Seek shelter'])}"
            else:
                keywords = random.choice(normal_keywords)
                post_text = f"Just a normal day, {keywords}. Hope everyone is safe and sound."
                
            # Generate random coordinates around the area
            lat = center_lat + random.uniform(-0.1, 0.1)
            lon = center_lon + random.uniform(-0.1, 0.1)
            
            post = {
                'Post': post_text,
                'Tweet': post_text, # Keep legacy key for compatibility
                'Cleaned_Post': post_text.lower(),
                'Cleaned_Tweet': post_text.lower(), # Keep legacy key for compatibility
                'Geolocation': f"{lat:.4f}, {lon:.4f}",
                'Latitude': lat,
                'Longitude': lon,
                'Timestamp': (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat(),
                'Source': 'sample_data'
            }
            
            sample_posts.append(post)
            
        self.posts = sample_posts
        self.last_collection_time = datetime.now()
        return sample_posts
    
    def collect_from_csv(self, filepath):
        """Load posts from CSV file"""
        try:
            df = pd.read_csv(filepath)
            self.posts = df.to_dict('records')
            self.last_collection_time = datetime.now()
            return self.posts
        except Exception as e:
            raise Exception(f"Failed to load CSV: {str(e)}")
    
    def collect_from_api(self, latitude, longitude, radius, place_name, min_posts=50):
        """
        Collect posts from Social Media API
        Note: This requires API credentials
        """
        raise NotImplementedError("API collection requires credentials and API access")
    
    def collect_from_selenium(self, latitude, longitude, radius, place_name, min_posts=50):
        """
        Collect posts using Selenium web scraping
        Note: This is for demonstration only and respects rate limits
        """
        raise NotImplementedError("Selenium collection not implemented in this version")
    
    def get_posts(self):
        """Get collected posts"""
        return self.posts
    
    def clear_posts(self):
        """Clear collected posts"""
        self.posts = []
        
    def get_collection_stats(self):
        """Get collection statistics"""
        return {
            'total_posts': len(self.posts),
            'last_collection_time': self.last_collection_time,
            'unique_locations': len(set([t.get('Geolocation', '') for t in self.posts])),
        }
