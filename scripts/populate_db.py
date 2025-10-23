import sys
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.manager import DatabaseManager
from src.models.db_models import Review
from config.settings import SONGS_CSV, MOVIES_CSV, WEBSERIES_CSV


def populate_from_csv():
    
    print("=" * 70)
    print("📥 POPULATING DATABASE FROM CSV FILES")
    print("=" * 70)
    
    db = DatabaseManager()
    
    # Drop and recreate tables
    print("\n🗑️  Dropping existing tables...")
    db.drop_tables()
    
    print("🏗️  Creating new tables...")
    db.create_tables()
    
    # Create system user
    print("\n1️⃣  Creating system user...")
    success, msg = db.add_user("system")
    print(f"   {msg}")
    
    # Counter for statistics
    stats = {
        'songs': 0,
        'movies': 0,
        'webshows': 0,
        'errors': 0
    }
    
    # ==================== LOAD SONGS ====================
    print("\n2️⃣  Loading songs from CSV...")
    try:
        songs_df = pd.read_csv(SONGS_CSV)
        print(f"   📄 Total songs in CSV: {len(songs_df)}")
        
        # Check required columns
        if 'SongName' not in songs_df.columns or 'ArtistName' not in songs_df.columns:
            print(f"   ❌ Missing required columns. Found: {songs_df.columns.tolist()}")
        else:
            # Remove duplicates
            songs_df = songs_df.drop_duplicates(subset=['SongName', 'ArtistName'], keep='first')
            
            # Sample 33 songs
            songs_sample = songs_df.sample(n=min(33, len(songs_df)), random_state=42)
            
            with db.session_scope() as session:
                for idx, row in songs_sample.iterrows():
                    try:
                        # Create song title
                        song_title = f"{row['SongName']} - {row['ArtistName']}"
                        
                        review = Review(
                            user_id=1,
                            username="system",
                            title=song_title,
                            media_type='song',
                            rating=None,  # No rating initially
                            review_text='',
                            is_reviewed=False
                        )
                        session.add(review)
                        stats['songs'] += 1
                        
                    except Exception as e:
                        stats['errors'] += 1
                        print(f"   ❌ Error adding song at row {idx}: {e}")
            
            print(f"   ✅ Added {stats['songs']} songs")
    
    except FileNotFoundError:
        print(f"   ❌ File not found: {SONGS_CSV}")
    except Exception as e:
        print(f"   ❌ Error loading songs: {e}")
    
    # ==================== LOAD MOVIES ====================
    print("\n3️⃣  Loading movies from CSV...")
    try:
        movies_df = pd.read_csv(MOVIES_CSV)
        print(f"   📄 Total movies in CSV: {len(movies_df)}")
        
        # Check required columns
        if 'title' not in movies_df.columns:
            print(f"   ❌ Missing 'title' column. Found: {movies_df.columns.tolist()}")
        else:
            # Remove duplicates
            movies_df = movies_df.drop_duplicates(subset=['title'], keep='first')
            
            # Sample 33 movies
            movies_sample = movies_df.sample(n=min(33, len(movies_df)), random_state=42)
            
            with db.session_scope() as session:
                for idx, row in movies_sample.iterrows():
                    try:
                        review = Review(
                            user_id=1,
                            username="system",
                            title=row['title'],
                            media_type='movie',
                            rating=None,  # No rating initially
                            review_text='',
                            is_reviewed=False
                        )
                        session.add(review)
                        stats['movies'] += 1
                        
                    except Exception as e:
                        stats['errors'] += 1
                        print(f"   ❌ Error adding movie at row {idx}: {e}")
            
            print(f"   ✅ Added {stats['movies']} movies")
    
    except FileNotFoundError:
        print(f"   ❌ File not found: {MOVIES_CSV}")
    except Exception as e:
        print(f"   ❌ Error loading movies: {e}")
    
    # ==================== LOAD WEB SERIES ====================
    print("\n4️⃣  Loading web series from CSV...")
    try:
        webseries_df = pd.read_csv(WEBSERIES_CSV)
        print(f"   📄 Total web series in CSV: {len(webseries_df)}")
        
        # Check required columns
        if 'Series Title' not in webseries_df.columns:
            print(f"   ❌ Missing 'Series Title' column. Found: {webseries_df.columns.tolist()}")
        else:
            # Remove duplicates
            webseries_df = webseries_df.drop_duplicates(subset=['Series Title'], keep='first')
            
            # Sample 34 web series
            webseries_sample = webseries_df.sample(n=min(34, len(webseries_df)), random_state=42)
            
            with db.session_scope() as session:
                for idx, row in webseries_sample.iterrows():
                    try:
                        review = Review(
                            user_id=1,
                            username="system",
                            title=row['Series Title'],
                            media_type='webshow',
                            rating=None,  # No rating initially
                            review_text='',
                            is_reviewed=False
                        )
                        session.add(review)
                        stats['webshows'] += 1
                        
                    except Exception as e:
                        stats['errors'] += 1
                        print(f"   ❌ Error adding web series at row {idx}: {e}")
            
            print(f"   ✅ Added {stats['webshows']} web series")
    
    except FileNotFoundError:
        print(f"   ❌ File not found: {WEBSERIES_CSV}")
    except Exception as e:
        print(f"   ❌ Error loading web series: {e}")
    
        # ==================== SUMMARY ====================
    print("\n" + "=" * 70)
    print("📊 POPULATION SUMMARY")
    print("=" * 70)
    print(f"   Songs added:      {stats['songs']}")
    print(f"   Movies added:     {stats['movies']}")
    print(f"   Web Shows added:  {stats['webshows']}")
    print(f"   Total items:      {stats['songs'] + stats['movies'] + stats['webshows']}")
    print(f"   Errors:           {stats['errors']}")

    # Get final database stats
    db_stats = db.get_stats()
    print(f"\n📈 DATABASE STATS")
    print(f"   Total Users:      {db_stats['users']}")
    print(f"   Total Media:      {db_stats['total_media']}")  # CHANGED
    print(f"   Reviewed Media:   {db_stats['reviewed_media']}")  # CHANGED
    print(f"   - Songs:          {db_stats['songs']['total']} total, "
        f"{db_stats['songs']['reviewed']} reviewed")  # CHANGED
    print(f"   - Movies:         {db_stats['movies']['total']} total, "
        f"{db_stats['movies']['reviewed']} reviewed")  # CHANGED
    print(f"   - Web Shows:      {db_stats['webshows']['total']} total, "
        f"{db_stats['webshows']['reviewed']} reviewed")  # CHANGED
    print("=" * 70)
    print("✅ Database population complete!\n")

if __name__ == "__main__":
    populate_from_csv()