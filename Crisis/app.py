import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import pandas as pd
import folium
import webbrowser
import os
from datetime import datetime
import json

from social_collector import SocialCollector
from crisis_detector import CrisisDetector
from map_visualizer import MapVisualizer
from utils import clean_tweet, preprocess_tweet, geocode_place


class CrisisDetectionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Crisis Detection Through Social Media - Real-Time Analysis")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize modules
        self.social_collector = SocialCollector()
        self.crisis_detector = CrisisDetector()
        self.map_visualizer = MapVisualizer()
        
        # Data storage
        self.tweets_data = []
        self.crisis_tweets = []
        self.is_collecting = False
        self.collection_thread = None
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        """Create the main user interface with tabs"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title = tk.Label(
            main_frame,
            text="🚨 Real-Time Crisis Detection System",
            font=("Helvetica", 16, "bold"),
            bg="#f0f0f0",
            fg="#d32f2f"
        )
        title.grid(row=0, column=0, sticky=tk.W, pady=10)
        
        # Create notebook (tabs)
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create tabs
        self.collector_frame = ttk.Frame(notebook)
        self.detector_frame = ttk.Frame(notebook)
        self.visualization_frame = ttk.Frame(notebook)
        self.results_frame = ttk.Frame(notebook)
        
        notebook.add(self.collector_frame, text="📥 Data Collector")
        notebook.add(self.detector_frame, text="🔍 Crisis Detector")
        notebook.add(self.visualization_frame, text="🗺️ Map & Visualization")
        notebook.add(self.results_frame, text="📊 Results")
        
        # Setup tabs
        self.setup_collector_tab()
        self.setup_detector_tab()
        self.setup_visualization_tab()
        self.setup_results_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            main_frame,
            textvariable=self.status_var,
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#e0e0e0"
        )
        status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
    def setup_collector_tab(self):
        """Setup tweet collection tab"""
        collector_frame = ttk.Frame(self.collector_frame, padding="15")
        collector_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.collector_frame.columnconfigure(0, weight=1)
        self.collector_frame.rowconfigure(0, weight=1)
        
        # Location input
        ttk.Label(collector_frame, text="Geolocation Parameters", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        ttk.Label(collector_frame, text="Latitude:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.lat_entry = ttk.Entry(collector_frame, width=20)
        self.lat_entry.insert(0, "24.7941004")
        self.lat_entry.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(collector_frame, text="Longitude:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.lon_entry = ttk.Entry(collector_frame, width=20)
        self.lon_entry.insert(0, "93.1170986")
        self.lon_entry.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(collector_frame, text="Radius:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.radius_entry = ttk.Entry(collector_frame, width=20)
        self.radius_entry.insert(0, "1000km")
        self.radius_entry.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(collector_frame, text="Place Name:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.place_entry = ttk.Entry(collector_frame, width=20)
        self.place_entry.insert(0, "Tamil Nadu")
        self.place_entry.grid(row=4, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(collector_frame, text="Min Tweets:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.min_tweets_entry = ttk.Entry(collector_frame, width=20)
        self.min_tweets_entry.insert(0, "50")
        self.min_tweets_entry.grid(row=5, column=1, sticky=tk.W, padx=5)
        
        # Collection source
        ttk.Label(collector_frame, text="Data Source:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.source_var = tk.StringVar(value="csv")
        ttk.Combobox(collector_frame, textvariable=self.source_var, values=["csv", "sample"], state="readonly", width=18).grid(row=6, column=1, sticky=tk.W, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(collector_frame)
        button_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        ttk.Button(
            button_frame,
            text="▶ Start Collection",
            command=self.start_collection
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="⏹ Stop Collection",
            command=self.stop_collection
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📂 Load CSV",
            command=self.load_csv
        ).pack(side=tk.LEFT, padx=5)
        
        # Log area
        ttk.Label(collector_frame, text="Collection Log:", font=("Helvetica", 10, "bold")).grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(15, 5))
        
        self.collector_log = scrolledtext.ScrolledText(collector_frame, height=12, width=60)
        self.collector_log.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        collector_frame.rowconfigure(9, weight=1)
        collector_frame.columnconfigure(1, weight=1)
        
    def setup_detector_tab(self):
        """Setup crisis detection tab"""
        detector_frame = ttk.Frame(self.detector_frame, padding="15")
        detector_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.detector_frame.columnconfigure(0, weight=1)
        self.detector_frame.rowconfigure(0, weight=1)
        
        ttk.Label(detector_frame, text="Crisis Detection Settings", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        ttk.Label(detector_frame, text="Confidence Threshold:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.confidence_entry = ttk.Entry(detector_frame, width=20)
        self.confidence_entry.insert(0, "0.5")
        self.confidence_entry.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Detection buttons
        button_frame = ttk.Frame(detector_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        ttk.Button(
            button_frame,
            text="🔍 Detect Crisis Tweets",
            command=self.detect_crisis
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📥 Load Model",
            command=self.load_model
        ).pack(side=tk.LEFT, padx=5)
        
        # Detection results
        ttk.Label(detector_frame, text="Detection Results:", font=("Helvetica", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(15, 5))
        
        self.detector_log = scrolledtext.ScrolledText(detector_frame, height=20, width=60)
        self.detector_log.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        detector_frame.rowconfigure(4, weight=1)
        detector_frame.columnconfigure(1, weight=1)
        
    def setup_visualization_tab(self):
        """Setup visualization tab"""
        viz_frame = ttk.Frame(self.visualization_frame, padding="15")
        viz_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.visualization_frame.columnconfigure(0, weight=1)
        self.visualization_frame.rowconfigure(0, weight=1)
        
        ttk.Label(viz_frame, text="Map & Visualization", font=("Helvetica", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Map type selection
        ttk.Label(viz_frame, text="Map Type:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.map_type_var = tk.StringVar(value="markers")
        ttk.Combobox(viz_frame, textvariable=self.map_type_var, values=["markers", "heatmap", "both"], state="readonly", width=18).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(viz_frame, text="Map Center Lat:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.map_lat_entry = ttk.Entry(viz_frame, width=20)
        self.map_lat_entry.insert(0, "24.7941004")
        self.map_lat_entry.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(viz_frame, text="Map Center Lon:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.map_lon_entry = ttk.Entry(viz_frame, width=20)
        self.map_lon_entry.insert(0, "93.1170986")
        self.map_lon_entry.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # Visualization buttons
        button_frame = ttk.Frame(viz_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=15)
        
        ttk.Button(
            button_frame,
            text="🗺️ Generate Crisis Map",
            command=self.generate_map
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="📍 Generate Heatmap",
            command=self.generate_heatmap
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🌐 Open in Browser",
            command=self.open_map_browser
        ).pack(side=tk.LEFT, padx=5)
        
        # Visualization log
        ttk.Label(viz_frame, text="Visualization Log:", font=("Helvetica", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(15, 5))
        
        self.viz_log = scrolledtext.ScrolledText(viz_frame, height=16, width=60)
        self.viz_log.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        viz_frame.rowconfigure(6, weight=1)
        viz_frame.columnconfigure(1, weight=1)
        
    def setup_results_tab(self):
        """Setup results display tab"""
        results_frame = ttk.Frame(self.results_frame, padding="15")
        results_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(1, weight=1)
        
        # Statistics
        ttk.Label(results_frame, text="Collection & Detection Statistics", font=("Helvetica", 12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=10)
        
        stats_frame = ttk.Frame(results_frame)
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Create text widget for stats
        self.results_text = scrolledtext.ScrolledText(results_frame, height=25, width=80)
        self.results_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Export buttons
        button_frame = ttk.Frame(results_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(
            button_frame,
            text="💾 Export Tweets to CSV",
            command=self.export_tweets
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="💾 Export Crisis Tweets",
            command=self.export_crisis_tweets
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🔄 Refresh Statistics",
            command=self.refresh_statistics
        ).pack(side=tk.LEFT, padx=5)
        
        results_frame.rowconfigure(2, weight=1)
        
    def start_collection(self):
        """Start tweet collection in a separate thread"""
        if self.is_collecting:
            messagebox.showwarning("Warning", "Collection already in progress!")
            return
            
        try:
            place_name = self.place_entry.get()
            lat_str = self.lat_entry.get()
            lon_str = self.lon_entry.get()
            
            # Always update coordinates from place name if provided
            if place_name:
                self.log_message("collector", f"Fetching coordinates for '{place_name}'...")
                lat, lon = geocode_place(place_name)
                if lat is not None and lon is not None:
                    self.lat_entry.delete(0, tk.END)
                    self.lat_entry.insert(0, str(lat))
                    self.lon_entry.delete(0, tk.END)
                    self.lon_entry.insert(0, str(lon))
                    lat_str = str(lat)
                    lon_str = str(lon)
                    self.log_message("collector", f"✓ Found coordinates: {lat}, {lon}")
                else:
                    # If geocoding fails, warn but try to use existing values if they exist
                    self.log_message("collector", f"⚠️ Could not find coordinates for '{place_name}', using existing values.")
                    if not lat_str or not lon_str:
                         messagebox.showerror("Error", f"Could not find coordinates for '{place_name}'")
                         return

            latitude = float(lat_str)
            longitude = float(lon_str)
            radius = self.radius_entry.get()
            min_tweets = int(self.min_tweets_entry.get())
            
            self.is_collecting = True
            self.collection_thread = threading.Thread(
                target=self._collection_worker,
                args=(latitude, longitude, radius, place_name, min_tweets),
                daemon=True
            )
            self.collection_thread.start()
            self.status_var.set("Collecting tweets...")
            self.log_message("collector", "Starting tweet collection...")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid values for coordinates and tweet count")
            self.is_collecting = False
            
    def _collection_worker(self, latitude, longitude, radius, place_name, min_tweets):
        """Worker thread for tweet collection"""
        try:
            source = self.source_var.get()
            if source == "csv":
                self.log_message("collector", f"Collecting {min_tweets} posts from location ({latitude}, {longitude})...")
                # This would normally use Selenium or Social Media API
                # For now, we'll use sample data
                self.tweets_data = self.social_collector.get_sample_posts(min_tweets, latitude, longitude)
                self.log_message("collector", f"✓ Successfully collected {len(self.tweets_data)} posts")
            else:
                self.tweets_data = self.social_collector.get_sample_posts(min_tweets, latitude, longitude)
                self.log_message("collector", f"✓ Loaded {len(self.tweets_data)} sample posts")
                
            self.status_var.set(f"Ready - {len(self.tweets_data)} posts collected")
        except Exception as e:
            self.log_message("collector", f"✗ Error during collection: {str(e)}")
            self.status_var.set("Error during collection")
        finally:
            self.is_collecting = False
            
    def stop_collection(self):
        """Stop tweet collection"""
        self.is_collecting = False
        self.log_message("collector", "Stopping tweet collection...")
        self.status_var.set("Collection stopped")
        
    def load_csv(self):
        """Load tweets from CSV file"""
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.dirname(os.path.abspath(__file__))
        )
        
        if filepath:
            try:
                df = pd.read_csv(filepath)
                self.tweets_data = df.to_dict('records')
                self.log_message("collector", f"✓ Loaded {len(self.tweets_data)} tweets from {os.path.basename(filepath)}")
                self.status_var.set(f"Loaded {len(self.tweets_data)} tweets from CSV")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
                
    def detect_crisis(self):
        """Detect crisis tweets using ML model"""
        if not self.tweets_data:
            messagebox.showwarning("Warning", "No tweets loaded. Please collect or load tweets first.")
            return
            
        try:
            threshold = float(self.confidence_entry.get())
            self.log_message("detector", f"Starting crisis detection on {len(self.tweets_data)} tweets...")
            self.log_message("detector", f"Using confidence threshold: {threshold}")
            
            self.crisis_tweets = []
            for idx, post in enumerate(self.tweets_data):
                post_text = post.get('Cleaned_Post', post.get('Cleaned_Tweet', post.get('Post', post.get('Tweet', ''))))
                
                # Clean and preprocess
                cleaned = clean_tweet(post_text)
                preprocessed = preprocess_tweet(cleaned)
                
                # Detect (using mock model for now)
                is_crisis, confidence = self.crisis_detector.predict(preprocessed)
                
                if is_crisis and confidence >= threshold:
                    post['Prediction'] = 1
                    post['Confidence'] = confidence
                    self.crisis_tweets.append(post)
                else:
                    post['Prediction'] = 0
                    post['Confidence'] = confidence
                    
                if (idx + 1) % 10 == 0:
                    self.log_message("detector", f"Processed {idx + 1}/{len(self.tweets_data)} posts...")
                    
            self.log_message("detector", f"✓ Detection complete. Found {len(self.crisis_tweets)} crisis posts")
            self.status_var.set(f"Detection complete - {len(self.crisis_tweets)} crisis posts found")
            
            # Display top crisis posts
            self.log_message("detector", "\n--- Top Crisis Posts ---")
            for idx, post in enumerate(self.crisis_tweets[:5], 1):
                text = post.get('Cleaned_Post', post.get('Cleaned_Tweet', post.get('Post', post.get('Tweet', ''))))[:100]
                conf = post.get('Confidence', 0)
                self.log_message("detector", f"{idx}. [{conf:.2%}] {text}...")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid confidence threshold")
        except Exception as e:
            self.log_message("detector", f"✗ Error during detection: {str(e)}")
            messagebox.showerror("Error", f"Detection failed: {str(e)}")
            
    def load_model(self):
        """Load pretrained ML model"""
        filepath = filedialog.askopenfilename(
            filetypes=[("Joblib files", "*.joblib"), ("Pickle files", "*.pkl"), ("All files", "*.*")],
            initialdir=os.path.dirname(os.path.abspath(__file__))
        )
        
        if filepath:
            try:
                self.crisis_detector.load_model(filepath)
                self.log_message("detector", f"✓ Model loaded: {os.path.basename(filepath)}")
                self.status_var.set(f"Model loaded: {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load model: {str(e)}")
                
    def generate_map(self):
        """Generate crisis map with markers"""
        if not self.crisis_tweets:
            messagebox.showwarning("Warning", "No crisis tweets detected. Please run detection first.")
            return
            
        try:
            lat = float(self.map_lat_entry.get())
            lon = float(self.map_lon_entry.get())
            
            self.log_message("viz", "Generating crisis map with markers...")
            
            # Convert to dataframe
            crisis_df = pd.DataFrame(self.crisis_tweets)
            
            # Generate map
            map_path = self.map_visualizer.create_crisis_map(
                crisis_df,
                center_lat=lat,
                center_lon=lon
            )
            
            self.log_message("viz", f"✓ Map saved to {map_path}")
            self.status_var.set(f"Map generated: {map_path}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid coordinates")
        except Exception as e:
            self.log_message("viz", f"✗ Error generating map: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate map: {str(e)}")
            
    def generate_heatmap(self):
        """Generate heatmap of crisis intensity"""
        if not self.crisis_tweets:
            messagebox.showwarning("Warning", "No crisis tweets detected. Please run detection first.")
            return
            
        try:
            lat = float(self.map_lat_entry.get())
            lon = float(self.map_lon_entry.get())
            
            self.log_message("viz", "Generating crisis heatmap...")
            
            # Convert to dataframe
            crisis_df = pd.DataFrame(self.crisis_tweets)
            
            # Generate heatmap
            heatmap_path = self.map_visualizer.create_heatmap(
                crisis_df,
                center_lat=lat,
                center_lon=lon
            )
            
            self.log_message("viz", f"✓ Heatmap saved to {heatmap_path}")
            self.status_var.set(f"Heatmap generated: {heatmap_path}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid coordinates")
        except Exception as e:
            self.log_message("viz", f"✗ Error generating heatmap: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate heatmap: {str(e)}")
            
    def open_map_browser(self):
        """Open generated map in web browser"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        map_files = ["crisis_map.html", "crisis_heatmap.html"]
        
        for map_file in map_files:
            map_path = os.path.join(base_dir, map_file)
            if os.path.exists(map_path):
                webbrowser.open('file://' + os.path.realpath(map_path))
                self.log_message("viz", f"Opened {map_file} in browser")
                return
                
        messagebox.showwarning("Warning", "No map file found. Please generate a map first.")
        
    def export_tweets(self):
        """Export all tweets to CSV"""
        if not self.tweets_data:
            messagebox.showwarning("Warning", "No tweets to export")
            return
            
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            df = pd.DataFrame(self.tweets_data)
            filename = f"tweets_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(base_dir, filename)
            df.to_csv(filepath, index=False)
            messagebox.showinfo("Success", f"Posts exported to {filename}")
            self.log_message("results", f"✓ Exported {len(self.tweets_data)} posts to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
            
    def export_crisis_tweets(self):
        """Export crisis tweets to CSV"""
        if not self.crisis_tweets:
            messagebox.showwarning("Warning", "No crisis posts to export")
            return
            
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            df = pd.DataFrame(self.crisis_tweets)
            filename = f"crisis_tweets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(base_dir, filename)
            df.to_csv(filepath, index=False)
            messagebox.showinfo("Success", f"Crisis posts exported to {filename}")
            self.log_message("results", f"✓ Exported {len(self.crisis_tweets)} crisis posts to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
            
    def refresh_statistics(self):
        """Refresh and display statistics"""
        self.results_text.delete(1.0, tk.END)
        
        stats = f"""
╔═══════════════════════════════════════════════════════════════╗
║              CRISIS DETECTION - STATISTICS REPORT              ║
╚═══════════════════════════════════════════════════════════════╝

📊 DATA COLLECTION STATISTICS
─────────────────────────────────────────────────────────────
• Total Posts Collected: {len(self.tweets_data)}
• Last Collection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Data Source: Loaded posts
• Status: Ready

🔍 CRISIS DETECTION STATISTICS
─────────────────────────────────────────────────────────────
• Total Crisis Posts Detected: {len(self.crisis_tweets)}
• Crisis Detection Rate: {(len(self.crisis_tweets)/max(len(self.tweets_data), 1)*100):.2f}%
• Non-Crisis Posts: {len(self.tweets_data) - len(self.crisis_tweets)}

📍 GEOLOCATION DISTRIBUTION
─────────────────────────────────────────────────────────────
"""
        
        if self.crisis_tweets:
            crisis_df = pd.DataFrame(self.crisis_tweets)
            if 'Geolocation' in crisis_df.columns:
                location_counts = crisis_df['Geolocation'].value_counts()
                for loc, count in location_counts.head(10).items():
                    stats += f"• {loc}: {count} posts\n"
                    
        stats += f"""
🎯 CONFIDENCE ANALYSIS
─────────────────────────────────────────────────────────────
"""
        
        if self.crisis_tweets:
            crisis_df = pd.DataFrame(self.crisis_tweets)
            if 'Confidence' in crisis_df.columns:
                avg_conf = crisis_df['Confidence'].mean()
                max_conf = crisis_df['Confidence'].max()
                min_conf = crisis_df['Confidence'].min()
                stats += f"• Average Confidence: {avg_conf:.2%}\n"
                stats += f"• Maximum Confidence: {max_conf:.2%}\n"
                stats += f"• Minimum Confidence: {min_conf:.2%}\n"
                
        stats += f"""
📁 OUTPUT FILES
─────────────────────────────────────────────────────────────
• Crisis Map: crisis_map.html
• Heatmap: crisis_heatmap.html
• Exported Tweets: tweets_export_*.csv
• Crisis Tweets: crisis_tweets_*.csv

═══════════════════════════════════════════════════════════════
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════════════════════
"""
        
        self.results_text.insert(tk.END, stats)
        self.log_message("results", "Statistics refreshed")
        
    def log_message(self, tab, message):
        """Log message to appropriate tab"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}\n"
        
        if tab == "collector":
            self.collector_log.insert(tk.END, formatted_msg)
            self.collector_log.see(tk.END)
        elif tab == "detector":
            self.detector_log.insert(tk.END, formatted_msg)
            self.detector_log.see(tk.END)
        elif tab == "viz":
            self.viz_log.insert(tk.END, formatted_msg)
            self.viz_log.see(tk.END)
        elif tab == "results":
            self.results_text.insert(tk.END, formatted_msg)
            self.results_text.see(tk.END)


def main():
    root = tk.Tk()
    app = CrisisDetectionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
