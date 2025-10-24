import threading
from typing import Dict, Any
from src.database.manager import DatabaseManager
from src.cache.redis_cache import cache
from src.patterns.observer import notification_subject


class ReviewService:
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._lock = threading.Lock()
    
    def add_review_threaded(self, username: str, title: str, media_type: str,
                       rating: float, review_text: str = '') -> tuple[bool, str]:
        with self._lock:
            success, message = self.db.update_or_create_review(
                username, title, media_type, rating, review_text
            )
            
            if success:
                cache.clear_pattern(f"top_rated:{media_type}:*")
                cache.delete(f"reviews:all")
                
                notification_subject.notify(
                    f"New review for '{title}' by {username}",
                    {
                        'title': title,
                        'media_type': media_type,
                        'rating': rating,
                        'username': username
                    }
                )
            
            return success, message
    
    def get_top_rated_cached(self, media_type: str, limit: int = 5):
        cache_key = f"top_rated:{media_type}:{limit}"
        
        cached = cache.get(cache_key)
        if cached:
            print("[CACHE HIT]")
            return cached
        
        print("[CACHE MISS - Querying database]")
        results = self.db.get_top_rated(media_type, limit)
        
        data = [
            {
                'title': x.title,
                'avg_rating': float(x.avg_rating),
                'review_count': x.review_count
            }
            for x in results
        ]

        cache.set(cache_key, data)
        return data