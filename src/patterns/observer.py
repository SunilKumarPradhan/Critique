"""Observer Pattern - Notification System for Favorite Media"""
from typing import Dict, Set, Any


class Observer:
    """Base observer interface"""
    
    def update(self, message: str, data: Dict[str, Any]):
        """Called when notification is triggered"""
        pass


class UserObserver(Observer):
    """Observer for user-specific notifications"""
    
    def __init__(self, username: str):
        self.username = username
    
    def update(self, message: str, data: Dict[str, Any]):
        """Display notification when favorite media is reviewed"""
        # Don't notify if the reviewer is the subscriber themselves
        if data.get('username') != self.username:
            print(f"  [🔔 NOTIFICATION for {self.username}]")
            print(f"  New review for your favorite '{data['title']}'")
            print(f"  Reviewer: {data['username']} | Rating: {data['rating']:.1f}/5.0")
            print()


class NotificationSubject:
    """Subject that manages observers and sends notifications"""
    
    def __init__(self):
        # Map username to observer: {username: UserObserver}
        self._observers: Dict[str, UserObserver] = {}
    
    def register_observer(self, username: str):
        """Register a user observer"""
        if username not in self._observers:
            self._observers[username] = UserObserver(username)
    
    def remove_observer(self, username: str):
        """Remove a user observer"""
        if username in self._observers:
            del self._observers[username]
    
    def notify_users(self, usernames: list[str], message: str, data: Dict[str, Any]):
        """Notify specific users about a review"""
        for username in usernames:
            if username in self._observers:
                self._observers[username].update(message, data)


# Global notification subject instance
notification_subject = NotificationSubject()