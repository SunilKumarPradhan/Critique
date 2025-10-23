"""Configuration settings for the application"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database settings
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "media_review.db"
DB_URL = f"sqlite:///{DB_PATH}"

# Redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_DECODE_RESPONSES = True

# Cache settings
CACHE_TTL = 300  # 5 minutes

# Dataset paths (FIXED - pointing to 'datasets' folder)
DATASETS_DIR = BASE_DIR / "datasets"  # Changed from 'databases' to 'datasets'
SONGS_CSV = DATASETS_DIR / "SpotifySongs.csv"
MOVIES_CSV = DATASETS_DIR / "tmdb_5000_movies.csv"
WEBSERIES_CSV = DATASETS_DIR / "WebSeries.csv"

# Pickle model paths
PICKLES_DIR = BASE_DIR / "pickles"
SONG_MODEL = PICKLES_DIR / "song_model.pkl"
MOVIE_MODEL = PICKLES_DIR / "movie_model.pkl"
SERIES_MODEL = PICKLES_DIR / "series_model.pkl"

# Ensure directories exist
DB_DIR.mkdir(parents=True, exist_ok=True)
DATASETS_DIR.mkdir(parents=True, exist_ok=True)
PICKLES_DIR.mkdir(parents=True, exist_ok=True)