import json
import threading
from typing import Dict, Any
from src.database.manager import DatabaseManager
from src.cache.redis_cache import cache
from src.patterns.observer import notification_subject
from concurrent.futures import ThreadPoolExecutor


class ReviewService:
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._lock = threading.Lock()
    
    def add_review_threaded(self, username: str, title: str, media_type: str, 
                       rating: float, review_text: str = '') -> tuple[bool, str]:
        """Add review with thread safety"""
        with self._lock:
            success, message = self.db.add_review(
                username, title, media_type, rating, review_text
            )
        
        if success:
            # Clear cache
            cache.clear_pattern(f"top_rated:{media_type}:*")
            cache.delete(f"reviews:all")
            
            # Notify users who have this media in favorites
            users_to_notify = self.db.get_users_who_favorited(title, media_type)
            
            if users_to_notify:
                print()  # Add blank line before notifications
                notification_subject.notify_users(
                    users_to_notify,
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
        """Get top rated media with caching"""
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
    
    def bulk_import_reviews(self, json_path: str) -> dict:
        """Import reviews in bulk using multithreading"""
        results = {'total': 0, 'success': 0, 'failed': 0}
        
        with open(json_path, 'r') as f:
            reviews = json.load(f)
        
        results['total'] = len(reviews)
        
        def process(review):
            try:
                if not self.db.get_user(review['username']):
                    self.db.add_user(review['username'])
                
                return self.add_review_threaded(
                    review['username'],
                    review['title'],
                    review['media_type'],
                    review['rating'],
                    review.get('review_text', '')
                )[0]
            except:
                return False
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            for success in executor.map(process, reviews):
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
        
        return results