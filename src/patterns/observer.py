"""Observer Pattern - Notification System"""
from typing import Dict, Set, Any


class Observer:
    """Base observer interface"""
    
    def update(self, message: str, data: Dict[str, Any]):
        """Called when notification is triggered"""
        pass


class MediaObserver(Observer):
    """Observer for media-specific notifications"""
    
    def __init__(self, username: str, media_title: str):
        self.username = username
        self.media_title = media_title
    
    def update(self, message: str, data: Dict[str, Any]):
        """Display notification when subscribed media is reviewed"""
        # Check if this notification is for the subscribed media
        if data.get('title', '').lower() == self.media_title.lower():
            # Don't notify if the reviewer is the subscriber themselves
            if data.get('username') != self.username:
                print(f"\n[NOTIFICATION] For {self.username}: A review has been added for '{data['title']}'")
                print(f"               Reviewer: {data['username']} | Rating: {data['rating']:.1f}/5.0\n")


class NotificationSubject:
    """Subject that manages observers and sends notifications"""
    
    def __init__(self):
        self._observers: Set[Observer] = set()
        # Track subscriptions: {username: {media_title: observer}}
        self._subscriptions: Dict[str, Dict[str, MediaObserver]] = {}
    
    def subscribe(self, username: str, media_title: str) -> bool:
        """Subscribe a user to notifications for a specific media"""
        if username not in self._subscriptions:
            self._subscriptions[username] = {}
        
        # Check if already subscribed
        if media_title.lower() in [title.lower() for title in self._subscriptions[username].keys()]:
            return False
        
        # Create observer
        observer = MediaObserver(username, media_title)
        self._subscriptions[username][media_title] = observer
        self._observers.add(observer)
        
        return True
    
    def unsubscribe(self, username: str, media_title: str) -> bool:
        """Unsubscribe a user from notifications for a specific media"""
        if username not in self._subscriptions:
            return False
        
        # Find matching subscription (case-insensitive)
        for title, observer in list(self._subscriptions[username].items()):
            if title.lower() == media_title.lower():
                self._observers.discard(observer)
                del self._subscriptions[username][title]
                return True
        
        return False
    
    def get_user_subscriptions(self, username: str) -> list:
        """Get all media titles a user is subscribed to"""
        if username not in self._subscriptions:
            return []
        return list(self._subscriptions[username].keys())
    
    def notify(self, message: str, data: Dict[str, Any]):
        """Notify all observers"""
        for observer in self._observers:
            observer.update(message, data)
    
    def clear_user_subscriptions(self, username: str):
        """Clear all subscriptions for a user"""
        if username in self._subscriptions:
            for observer in self._subscriptions[username].values():
                self._observers.discard(observer)
            del self._subscriptions[username]


# Global notification subject instance
notification_subject = NotificationSubject()