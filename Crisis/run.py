#!/usr/bin/env python3
"""
Quick Start Script for Crisis Detection GUI Application
Handles environment setup and application launch
"""

import sys
import os
import subprocess
import importlib.util

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def check_python_version():
    """Check if Python version is 3.7 or higher"""
    if sys.version_info < (3, 7):
        print("[ERROR] Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"[OK] Python version: {sys.version.split()[0]}")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'pandas', 'folium', 'sklearn', 'nltk', 'selenium', 'requests', 'joblib', 'branca'
    ]
    
    missing_packages = []
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
    
    if missing_packages:
        print("[ERROR] Missing packages:", ", ".join(missing_packages))
        return False
    
    print("[OK] All required packages are installed")
    return True


def install_dependencies():
    """Install missing dependencies"""
    print("\n[*] Installing dependencies...")
    
    requirements_file = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '-r', requirements_file],
            stdout=subprocess.DEVNULL
        )
        print("[OK] Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to install dependencies")
        print("Please install manually: pip install -r requirements.txt")
        return False


def download_nltk_data():
    """Download required NLTK data"""
    print("\n[*] Downloading NLTK data...")
    
    try:
        import nltk
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        print("[OK] NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"[WARN] Could not download NLTK data: {e}")
        print("The application may have reduced functionality")
        return True


def check_model_files():
    """Check if model files exist"""
    current_dir = os.path.dirname(__file__)
    model_file = os.path.join(current_dir, 'final_mlp_model.joblib')
    vectorizer_file = os.path.join(current_dir, 'tfidf_vectorizer.joblib')
    
    print("\n[*] Checking ML model files...")
    
    if os.path.exists(model_file):
        print("[OK] ML model found")
    else:
        print("[WARN] ML model not found - will use heuristic detection")
    
    if os.path.exists(vectorizer_file):
        print("[OK] TF-IDF vectorizer found")
    else:
        print("[WARN] TF-IDF vectorizer not found")
    
    return True


def launch_application():
    """Launch the GUI application"""
    print("\n>>> Launching Crisis Detection GUI Application...\n")
    
    app_file = os.path.join(os.path.dirname(__file__), 'app.py')
    
    try:
        subprocess.call([sys.executable, app_file])
    except KeyboardInterrupt:
        print("\n\nApplication closed by user")
    except Exception as e:
        print(f"\n[ERROR] Error launching application: {e}")
        return False
    
    return True


def main():
    """Main entry point"""
    print("=" * 61)
    print("   Crisis Detection Through Social Media - GUI Setup")
    print("=" * 61 + "\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        print("\n[*] Attempting to install missing dependencies...")
        if not install_dependencies():
            print("\n[ERROR] Setup failed. Please install dependencies manually:")
            print("   pip install -r requirements.txt")
            sys.exit(1)
    
    # Download NLTK data
    download_nltk_data()
    
    # Check model files
    check_model_files()
    
    # Launch application
    print("\n" + "=" * 61)
    success = launch_application()
    
    if success:
        print("\n[OK] Application closed successfully")
    else:
        print("\n[ERROR] Application closed with errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
