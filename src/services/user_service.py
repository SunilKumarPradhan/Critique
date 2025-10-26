"""User Service - Simplified"""
from src.database.manager import DatabaseManager
from src.patterns.observer import notification_subject


class UserService:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def register_user(self, username: str) -> tuple[bool, str]:
        success, message = self.db.add_user(username)
        if success:
            notification_subject.register_observer(username)
        return success, message
    
    def add_to_favorites(self, username: str, title: str, media_type: str) -> tuple[bool, str]:
        return self.db.add_favorite(username, title, media_type)
    
    def remove_from_favorites(self, username: str, title: str, media_type: str) -> tuple[bool, str]:
        return self.db.remove_favorite(username, title, media_type)
    
    def get_favorites(self, username: str) -> list:
        return self.db.get_user_favorites(username)