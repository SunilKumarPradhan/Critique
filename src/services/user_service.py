"""User Service - Business logic for user operations"""
from src.database.manager import DatabaseManager
from src.patterns.observer import notification_subject


class UserService:
    """Handles user-related business logic"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def register_user(self, username: str) -> tuple[bool, str]:
        """Register a new user"""
        return self.db.add_user(username)
    
    def subscribe_to_media(self, username: str, media_title: str) -> tuple[bool, str]:
        """Subscribe user to notifications for a specific media"""
        # Check if user exists
        user = self.db.get_user(username)
        if not user:
            return False, f"User '{username}' not found"
        
        # Subscribe to notifications
        success = notification_subject.subscribe(username, media_title)
        
        if success:
            return True, f"Subscribed to notifications for '{media_title}'"
        else:
            return False, f"Already subscribed to '{media_title}'"
    
    def unsubscribe_from_media(self, username: str, media_title: str) -> tuple[bool, str]:
        """Unsubscribe user from notifications for a specific media"""
        success = notification_subject.unsubscribe(username, media_title)
        
        if success:
            return True, f"Unsubscribed from '{media_title}'"
        else:
            return False, f"Not subscribed to '{media_title}'"
    
    def get_subscriptions(self, username: str) -> list:
        """Get all media titles user is subscribed to"""
        return notification_subject.get_user_subscriptions(username)