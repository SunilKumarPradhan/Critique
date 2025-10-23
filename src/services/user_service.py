from src.database.manager import DatabaseManager
from src.patterns.observer import UserObserver, notification_subject

class UserService:

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def register_user(self, username: str) -> tuple[bool, str]:
        success, message = self.db.add_user(username)
        
        if success:
            observer = UserObserver(username)
            notification_subject.attach(observer)
        
        return success, message
    
    def subscribe_to_media(self, username: str, media_title: str):
        user = self.db.get_user(username)
        if not user:
            return False, f"User '{username}' not found"
        
        observer = None
        for obs in notification_subject._observers:
            if obs.username == username:
                observer = obs
                break
        
        if not observer:
            observer = UserObserver(username)
        
        notification_subject.attach(observer, media_title)
        return True, f"Subscribed to notifications for '{media_title}'"