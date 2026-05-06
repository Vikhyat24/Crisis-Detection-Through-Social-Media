import folium
from folium.plugins import MarkerCluster, HeatMap
import pandas as pd
import os
from datetime import datetime


class MapVisualizer:
    """Handles map generation and visualization"""
    
    def __init__(self, output_dir=None):
        if output_dir is None:
            output_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = output_dir
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """Ensure output directory exists"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_crisis_map(self, crisis_df, center_lat=24.7941004, center_lon=93.1170986, zoom_start=6):
        """Create a crisis map with markers for crisis posts"""
        
        # Prepare data - ensure we have coordinates
        if 'Latitude' not in crisis_df.columns or 'Longitude' not in crisis_df.columns:
            if 'Geolocation' in crisis_df.columns:
                crisis_df[['Latitude', 'Longitude']] = crisis_df['Geolocation'].str.split(',', expand=True).astype(float)
            else:
                raise ValueError("No location data found in dataframe")
        
        # Create map
        crisis_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )
        
        # Add marker cluster
        marker_cluster = MarkerCluster(name='Crisis Posts').add_to(crisis_map)
        
        # Add markers for each crisis post
        for idx, row in crisis_df.iterrows():
            try:
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
                
                # specific key check
                post_text = row.get('Cleaned_Post', row.get('Cleaned_Tweet', row.get('Post', row.get('Tweet', 'No text'))))[:200]
                confidence = row.get('Confidence', 0)
                
                # Create popup
                popup_html = f"""
                <div style="font-family: Arial; font-size: 12px; width: 250px;">
                    <h4 style="color: #d32f2f; margin: 5px 0;">⚠️ Crisis Alert</h4>
                    <p><strong>Message:</strong> {post_text}</p>
                    <p><strong>Confidence:</strong> {confidence:.1%}</p>
                    <p><strong>Location:</strong> {lat:.4f}, {lon:.4f}</p>
                    <p><strong>Time:</strong> {row.get('Timestamp', datetime.now().isoformat())}</p>
                </div>
                """
                
                popup = folium.Popup(folium.Html(popup_html, script=True), max_width=300)
                
                # Determine marker color based on confidence
                if confidence >= 0.8:
                    color = 'red'
                    icon = 'exclamation'
                elif confidence >= 0.6:
                    color = 'orange'
                    icon = 'warning'
                else:
                    color = 'yellow'
                    icon = 'info-sign'
                
                folium.Marker(
                    location=[lat, lon],
                    popup=popup,
                    icon=folium.Icon(color=color, icon=icon),
                    tooltip=f"Crisis: {confidence:.1%} confidence"
                ).add_to(marker_cluster)
                
            except (ValueError, TypeError) as e:
                continue
        
        # Add layer control
        folium.LayerControl().add_to(crisis_map)
        
        # Save map
        output_path = os.path.join(self.output_dir, 'crisis_map.html')
        crisis_map.save(output_path)
        
        return output_path
    
    def create_heatmap(self, crisis_df, center_lat=24.7941004, center_lon=93.1170986, zoom_start=6):
        """Create a heatmap visualization of crisis intensity"""
        
        # Prepare data
        if 'Latitude' not in crisis_df.columns or 'Longitude' not in crisis_df.columns:
            if 'Geolocation' in crisis_df.columns:
                crisis_df[['Latitude', 'Longitude']] = crisis_df['Geolocation'].str.split(',', expand=True).astype(float)
            else:
                raise ValueError("No location data found in dataframe")
        
        # Create map
        heatmap = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles='CartoDB positron'
        )
        
        # Prepare heat data (latitude, longitude, intensity)
        heat_data = []
        for idx, row in crisis_df.iterrows():
            try:
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
                # Use confidence as intensity
                intensity = float(row.get('Confidence', 0.5))
                heat_data.append([lat, lon, intensity])
            except (ValueError, TypeError):
                continue
        
        if heat_data:
            # Add heatmap layer
            HeatMap(
                heat_data,
                name='Crisis Intensity',
                radius=25,
                blur=20,
                max_zoom=13,
                min_opacity=0.3
            ).add_to(heatmap)
        
        # Add markers with crisis posts
        marker_cluster = MarkerCluster(name='Crisis Locations').add_to(heatmap)
        
        for idx, row in crisis_df.iterrows():
            try:
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
                
                post_text = row.get('Cleaned_Post', row.get('Cleaned_Tweet', row.get('Post', row.get('Tweet', 'No text'))))[:150]
                confidence = row.get('Confidence', 0)
                
                popup_text = f"Crisis: {confidence:.1%}\n{post_text}..."
                
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_text,
                    icon=folium.Icon(color='red', icon='exclamation')
                ).add_to(marker_cluster)
                
            except (ValueError, TypeError):
                continue
        
        # Add layer control
        folium.LayerControl().add_to(heatmap)
        
        # Add title
        title_html = '''
        <div style="position: fixed; 
                    top: 10px; left: 50px; width: 300px; height: 80px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:16px; font-weight: bold; padding: 10px;
                    border-radius: 5px;">
            🔥 Crisis Intensity Heatmap
            <br><br>
            <span style="font-size: 12px; font-weight: normal;">
                Red areas indicate high crisis concentration
            </span>
        </div>
        '''
        heatmap.get_root().html.add_child(folium.Element(title_html))
        
        # Save heatmap
        output_path = os.path.join(self.output_dir, 'crisis_heatmap.html')
        heatmap.save(output_path)
        
        return output_path
    
    def create_combined_map(self, crisis_df, tweets_df=None, center_lat=24.7941004, center_lon=93.1170986, zoom_start=6):
        """Create a combined map with crisis and regular tweets"""
        
        # Prepare data
        if 'Latitude' not in crisis_df.columns or 'Longitude' not in crisis_df.columns:
            if 'Geolocation' in crisis_df.columns:
                crisis_df[['Latitude', 'Longitude']] = crisis_df['Geolocation'].str.split(',', expand=True).astype(float)
        
        # Create map
        combined_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )
        
        # Add crisis markers
        crisis_cluster = MarkerCluster(name='Crisis Tweets').add_to(combined_map)
        
        for idx, row in crisis_df.iterrows():
            try:
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
                
                tweet_text = row.get('Cleaned_Tweet', row.get('Tweet', 'No text'))[:200]
                confidence = row.get('Confidence', 0)
                
                popup_text = f"⚠️ CRISIS\n{confidence:.1%} confidence\n{tweet_text}"
                
                folium.Marker(
                    location=[lat, lon],
                    popup=popup_text,
                    icon=folium.Icon(color='red', icon='exclamation')
                ).add_to(crisis_cluster)
                
            except (ValueError, TypeError):
                continue
        
        # Add normal tweets if provided
        if tweets_df is not None and len(tweets_df) > 0:
            normal_cluster = MarkerCluster(name='Normal Tweets').add_to(combined_map)
            
            for idx, row in tweets_df.iterrows():
                try:
                    lat = float(row['Latitude'])
                    lon = float(row['Longitude'])
                    
                    tweet_text = row.get('Cleaned_Tweet', row.get('Tweet', 'No text'))[:200]
                    
                    folium.Marker(
                        location=[lat, lon],
                        popup=tweet_text,
                        icon=folium.Icon(color='blue', icon='info-sign')
                    ).add_to(normal_cluster)
                    
                except (ValueError, TypeError):
                    continue
        
        folium.LayerControl().add_to(combined_map)
        
        output_path = os.path.join(self.output_dir, 'combined_map.html')
        combined_map.save(output_path)
        
        return output_path
    
    def create_statistics_map(self, crisis_df, center_lat=24.7941004, center_lon=93.1170986, zoom_start=6):
        """Create a map with crisis statistics"""
        
        # Prepare data
        if 'Latitude' not in crisis_df.columns or 'Longitude' not in crisis_df.columns:
            if 'Geolocation' in crisis_df.columns:
                crisis_df[['Latitude', 'Longitude']] = crisis_df['Geolocation'].str.split(',', expand=True).astype(float)
        
        # Create map
        stats_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles='CartoDB positron'
        )
        
        # Group by location and create circles for each location cluster
        if 'Geolocation' in crisis_df.columns:
            location_groups = crisis_df.groupby('Geolocation')
            
            for location, group in location_groups:
                try:
                    lat, lon = map(float, location.split(','))
                    count = len(group)
                    avg_confidence = group['Confidence'].mean() if 'Confidence' in group.columns else 0.5
                    
                    # Circle radius based on count
                    radius = max(20, min(count * 5, 200))
                    
                    # Circle color based on confidence
                    if avg_confidence >= 0.8:
                        color = 'darkred'
                    elif avg_confidence >= 0.6:
                        color = 'red'
                    elif avg_confidence >= 0.4:
                        color = 'orange'
                    else:
                        color = 'yellow'
                    
                    popup_text = f"""
                    Location: {location}<br>
                    Crisis Tweets: {count}<br>
                    Avg Confidence: {avg_confidence:.1%}
                    """
                    
                    folium.Circle(
                        location=[lat, lon],
                        radius=radius,
                        popup=popup_text,
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.7,
                        weight=2
                    ).add_to(stats_map)
                    
                except ValueError:
                    continue
        
        output_path = os.path.join(self.output_dir, 'statistics_map.html')
        stats_map.save(output_path)
        
        return output_path
