import threading
from typing import Dict, Any
from src.database.manager import DatabaseManager
from src.cache.redis_cache import cache
from src.patterns.observer import notification_subject


class ReviewService:
    """Handles review operations with caching and threading"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._lock = threading.Lock()  # Thread safety for concurrent submissions
    
    def add_review_threaded(self, username: str, title: str, media_type: str,
                       rating: float, review_text: str = '') -> tuple[bool, str]:

        with self._lock:
            # Update or create in database
            success, message = self.db.update_or_create_review(
                username, title, media_type, rating, review_text
            )
            
            if success:
                # Invalidate cache
                cache.clear_pattern(f"top_rated:{media_type}:*")
                cache.delete(f"reviews:all")
                
                # Notify observers
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
        """Get top-rated media with caching"""
        cache_key = f"top_rated:{media_type}:{limit}"
        
        # Check cache first
        cached = cache.get(cache_key)
        if cached:
            print("   💾 [Cache HIT]")
            return cached
        
        # Cache miss - query database
        print("   🔍 [Cache MISS - Querying DB]")
        results = self.db.get_top_rated(media_type, limit)
        
        # Convert to serializable format
        data = [
            {
                'title': r.title,
                'avg_rating': float(r.avg_rating),
                'review_count': r.review_count
            }
            for r in results
        ]
        
        # Store in cache
        cache.set(cache_key, data)
        
        return data