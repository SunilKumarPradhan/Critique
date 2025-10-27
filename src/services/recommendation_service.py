import pickle
from pathlib import Path
from typing import List, Dict, Optional
from config.settings import SONG_MODEL, MOVIE_MODEL, SERIES_MODEL


class RecommendationService:
    
    def __init__(self):
        self.movie_model = None
        self.song_model = None
        self.series_model = None
        
        self._load_movie_model()
        self._load_song_model()
        self._load_series_model()
    
    def _load_movie_model(self):
        try:
            if MOVIE_MODEL.exists():
                with open(MOVIE_MODEL, 'rb') as f:
                    data = pickle.load(f)
                self.movie_model = {
                    'movies': data['movies'],
                    'similarity': data['similarity']
                }
                print(f"[OK] Movie model loaded ({len(data['movies'])} movies)")
            else:
                print(f"[WARNING] Movie model not found at: {MOVIE_MODEL}")
        except Exception as e:
            print(f"[ERROR] Loading movie model: {e}")
    
    def _load_song_model(self):
        try:
            if SONG_MODEL.exists():
                with open(SONG_MODEL, 'rb') as f:
                    data = pickle.load(f)
                self.song_model = {
                    'songs': data['songs'],
                    'similarity': data['similarity']
                }
                print(f"[OK] Song model loaded ({len(data['songs'])} songs)")
            else:
                print(f"[WARNING] Song model not found at: {SONG_MODEL}")
        except Exception as e:
            print(f"[ERROR] Loading song model: {e}")
    
    def _load_series_model(self):
        try:
            if SERIES_MODEL.exists():
                with open(SERIES_MODEL, 'rb') as f:
                    data = pickle.load(f)
                self.series_model = {
                    'shows': data['shows'],
                    'similarity': data['similarity']
                }
                print(f"[OK] Series model loaded ({len(data['shows'])} series)")
            else:
                print(f"[WARNING] Series model not found at: {SERIES_MODEL}")
        except Exception as e:
            print(f"[ERROR] Loading series model: {e}")
    
    def recommend(self, media_type: str, title: str, top_n: int = 5) -> Optional[List[Dict]]:
        """Unified recommendation interface"""
        if media_type == 'movie':
            return self._recommend_movies(title, top_n)
        elif media_type == 'song':
            return self._recommend_songs(title, top_n)
        elif media_type == 'webshow':
            return self._recommend_series(title, top_n)
        else:
            print(f"[ERROR] Invalid media type: {media_type}")
            return None
    
    def _recommend_movies(self, title: str, top_n: int = 5) -> Optional[List[Dict]]:
        if not self.movie_model:
            print("[ERROR] Movie model not available")
            return None
        
        movies = self.movie_model['movies']
        similarity = self.movie_model['similarity']
        
        try:
            idx = movies[movies['title'].str.lower() == title.lower()].index[0]
            movie_title = movies.iloc[idx]['title']
            
            distances = sorted(
                list(enumerate(similarity[idx])),
                reverse=True,
                key=lambda x: x[1]
            )
            
            results = []
            for similar_idx, score in distances[1:top_n+1]:
                rec_title = movies.iloc[similar_idx]['title']
                results.append({
                    'title': rec_title,
                    'score': int(score * 100)
                })
            
            return results
            
        except IndexError:
            print(f"[ERROR] Movie '{title}' not found in recommendation database")
            return None
    
    def _recommend_songs(self, input_name: str, top_n: int = 5) -> Optional[List[Dict]]:
        if not self.song_model:
            print("[ERROR] Song model not available")
            return None
        
        songs = self.song_model['songs']
        similarity = self.song_model['similarity']
        
        input_clean = input_name.lower().replace(" ", "")
        
        song_matches = songs[
            songs['SongName'].str.lower().str.replace(" ", "") == input_clean
        ]
        
        if song_matches.empty:
            print(f"[ERROR] Song '{input_name}' not found in recommendation database")
            return None
        
        idx = song_matches.index[0]
        
        distances = sorted(
            list(enumerate(similarity[idx])),
            reverse=True,
            key=lambda x: x[1]
        )
        
        results = []
        for similar_idx, score in distances[1:top_n+1]:
            rec_song = songs.iloc[similar_idx]['SongName']
            results.append({
                'title': rec_song,
                'score': int(score * 100)
            })
        
        return results
    
    def _recommend_series(self, title: str, top_n: int = 5) -> Optional[List[Dict]]:
        if not self.series_model:
            print("[ERROR] Series model not available")
            return None
        
        shows = self.series_model['shows']
        similarity = self.series_model['similarity']
        
        try:
            idx = shows[
                shows['Series Title'].str.lower() == title.lower()
            ].index[0]
            
            distances = sorted(
                list(enumerate(similarity[idx])),
                reverse=True,
                key=lambda x: x[1]
            )
            
            results = []
            for similar_idx, score in distances[1:top_n+1]:
                rec_title = shows.iloc[similar_idx]['Series Title']
                results.append({
                    'title': rec_title,
                    'score': int(score * 100)
                })
            
            return results
            
        except IndexError:
            print(f"[ERROR] Series '{title}' not found in recommendation database")
            return None