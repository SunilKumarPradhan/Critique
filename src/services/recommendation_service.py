"""Recommendation service for all media types"""
import pickle
from pathlib import Path
from typing import List, Dict, Optional
from config.settings import SONG_MODEL, MOVIE_MODEL, SERIES_MODEL


class RecommendationService:
    """Unified recommendation service for movies, songs, and web series"""
    
    def __init__(self):
        """Initialize recommendation models"""
        self.movie_model = None
        self.song_model = None
        self.series_model = None
        
        # Load models
        self._load_movie_model()
        self._load_song_model()
        self._load_series_model()
    
    # ==================== MODEL LOADING ====================
    
    def _load_movie_model(self):
        """Load movie recommendation model"""
        try:
            if MOVIE_MODEL.exists():
                with open(MOVIE_MODEL, 'rb') as f:
                    data = pickle.load(f)
                self.movie_model = {
                    'movies': data['movies'],
                    'similarity': data['similarity']
                }
                print(f"✅ Movie model loaded ({len(data['movies'])} movies)")
            else:
                print(f"⚠️  Movie model not found at: {MOVIE_MODEL}")
        except Exception as e:
            print(f"❌ Error loading movie model: {e}")
    
    def _load_song_model(self):
        """Load song recommendation model"""
        try:
            if SONG_MODEL.exists():
                with open(SONG_MODEL, 'rb') as f:
                    data = pickle.load(f)
                self.song_model = {
                    'songs': data['songs'],
                    'similarity': data['similarity']
                }
                print(f"✅ Song model loaded ({len(data['songs'])} songs)")
            else:
                print(f"⚠️  Song model not found at: {SONG_MODEL}")
        except Exception as e:
            print(f"❌ Error loading song model: {e}")
    
    def _load_series_model(self):
        """Load series recommendation model"""
        try:
            if SERIES_MODEL.exists():
                with open(SERIES_MODEL, 'rb') as f:
                    data = pickle.load(f)
                self.series_model = {
                    'shows': data['shows'],
                    'similarity': data['similarity']
                }
                print(f"✅ Series model loaded ({len(data['shows'])} series)")
            else:
                print(f"⚠️  Series model not found at: {SERIES_MODEL}")
        except Exception as e:
            print(f"❌ Error loading series model: {e}")
    
    # ==================== MOVIE RECOMMENDATIONS ====================
    
    def recommend_movies(self, title: str, top_n: int = 5) -> Optional[List[Dict]]:
        """Get movie recommendations"""
        if not self.movie_model:
            print("❌ Movie model not available")
            return None
        
        movies = self.movie_model['movies']
        similarity = self.movie_model['similarity']
        
        try:
            # Find movie (case-insensitive)
            idx = movies[movies['title'].str.lower() == title.lower()].index[0]
            movie_title = movies.iloc[idx]['title']
            
            # Get similar movies
            distances = sorted(
                list(enumerate(similarity[idx])),
                reverse=True,
                key=lambda x: x[1]
            )
            
            print(f"\n🎬 Recommendations for: {movie_title}")
            print("-" * 50)
            
            results = []
            for i, (similar_idx, score) in enumerate(distances[1:top_n+1], 1):
                rec_title = movies.iloc[similar_idx]['title']
                print(f"{i}. {rec_title} (Match: {score:.0%})")
                results.append({
                    'title': rec_title,
                    'similarity': score
                })
            
            return results
            
        except IndexError:
            print(f"❌ Movie '{title}' not found")
            self._suggest_movies(title)
            return None
    
    def _suggest_movies(self, keyword: str):
        """Suggest similar movie titles"""
        movies = self.movie_model['movies']
        results = movies[movies['title'].str.contains(keyword, case=False, na=False)]
        
        if not results.empty:
            print(f"\n💡 Did you mean:")
            for idx, row in results.head(5).iterrows():
                print(f"  • {row['title']}")
    
    # ==================== SONG RECOMMENDATIONS ====================
    
    def recommend_songs(self, input_name: str, top_n: int = 5) -> Optional[List[Dict]]:
        """Get song recommendations by song name or artist"""
        if not self.song_model:
            print("❌ Song model not available")
            return None
        
        songs = self.song_model['songs']
        similarity = self.song_model['similarity']
        
        input_clean = input_name.lower().replace(" ", "")
        
        # Try to find by song name
        song_matches = songs[
            songs['SongName'].str.lower().str.replace(" ", "") == input_clean
        ]
        
        if not song_matches.empty:
            idx = song_matches.index[0]
            song_name = songs.iloc[idx]['SongName']
            artist_name = songs.iloc[idx]['ArtistName']
            print(f"\n🎵 Found: {song_name} by {artist_name}")
        
        # Try by artist name
        elif input_clean in songs['ArtistName'].values:
            artist_songs = songs[songs['ArtistName'] == input_clean]
            idx = artist_songs.index[0]
            song_name = songs.iloc[idx]['SongName']
            artist_name = songs.iloc[idx]['ArtistName']
            print(f"\n🎤 Using: {song_name} by {artist_name}")
        
        else:
            print(f"❌ '{input_name}' not found")
            self._suggest_songs(input_clean)
            return None
        
        # Get recommendations
        distances = sorted(
            list(enumerate(similarity[idx])),
            reverse=True,
            key=lambda x: x[1]
        )
        
        print(f"\n🎶 Recommendations:")
        print("-" * 50)
        
        results = []
        for i, (similar_idx, score) in enumerate(distances[1:top_n+1], 1):
            rec_song = songs.iloc[similar_idx]['SongName']
            rec_artist = songs.iloc[similar_idx]['ArtistName']
            print(f"{i}. {rec_song} - {rec_artist} (Match: {score:.0%})")
            results.append({
                'song': rec_song,
                'artist': rec_artist,
                'similarity': score
            })
        
        return results
    
    def _suggest_songs(self, keyword: str):
        """Suggest similar songs or artists"""
        songs = self.song_model['songs']
        
        # Search artists
        artist_matches = songs[
            songs['ArtistName'].str.contains(keyword, case=False, na=False)
        ]
        
        if not artist_matches.empty:
            print(f"\n💡 Did you mean (Artists):")
            for artist in artist_matches['ArtistName'].unique()[:5]:
                print(f"  • {artist}")
        
        # Search songs
        song_matches = songs[
            songs['SongName'].str.lower().str.contains(keyword, na=False)
        ]
        
        if not song_matches.empty:
            print(f"\n💡 Did you mean (Songs):")
            for idx, row in song_matches.head(5).iterrows():
                print(f"  • {row['SongName']} - {row['ArtistName']}")
    
    # ==================== SERIES RECOMMENDATIONS ====================
    
    def recommend_series(self, title: str, top_n: int = 5) -> Optional[List[Dict]]:
        """Get web series recommendations"""
        if not self.series_model:
            print("❌ Series model not available")
            return None
        
        shows = self.series_model['shows']
        similarity = self.series_model['similarity']
        
        try:
            # Find series (case-insensitive)
            idx = shows[
                shows['Series Title'].str.lower() == title.lower()
            ].index[0]
            
            series_title = shows.iloc[idx]['Series Title']
            genre = shows.iloc[idx]['Genre']
            
            print(f"\n📺 Found: {series_title} ({genre})")
            
            # Get similar series
            distances = sorted(
                list(enumerate(similarity[idx])),
                reverse=True,
                key=lambda x: x[1]
            )
            
            print(f"\n🎬 Recommendations:")
            print("-" * 50)
            
            results = []
            for i, (similar_idx, score) in enumerate(distances[1:top_n+1], 1):
                rec_title = shows.iloc[similar_idx]['Series Title']
                rec_genre = shows.iloc[similar_idx]['Genre']
                print(f"{i}. {rec_title} ({rec_genre}) - Match: {score:.0%}")
                results.append({
                    'title': rec_title,
                    'genre': rec_genre,
                    'similarity': score
                })
            
            return results
            
        except IndexError:
            print(f"❌ Series '{title}' not found")
            self._suggest_series(title)
            return None
    
    def _suggest_series(self, keyword: str):
        """Suggest similar series titles"""
        shows = self.series_model['shows']
        results = shows[
            shows['Series Title'].str.contains(keyword, case=False, na=False)
        ]
        
        if not results.empty:
            print(f"\n💡 Did you mean:")
            for idx, row in results.head(5).iterrows():
                print(f"  • {row['Series Title']} ({row['Genre']})")
    
    # ==================== UNIFIED RECOMMENDATION ====================
    
    def recommend(self, media_type: str, title: str, top_n: int = 5):
        """Unified recommendation interface"""
        if media_type == 'movie':
            return self.recommend_movies(title, top_n)
        elif media_type == 'song':
            return self.recommend_songs(title, top_n)
        elif media_type == 'webshow':
            return self.recommend_series(title, top_n)
        else:
            print(f"❌ Invalid media type: {media_type}")
            return None