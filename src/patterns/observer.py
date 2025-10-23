"""Observer Pattern for review notifications"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Observer(ABC):
    """Abstract observer - receives notifications"""
    
    @abstractmethod
    def update(self, message: str, data: Dict[str, Any]):
        """Receive notification"""
        pass


class UserObserver(Observer):
    """Observer for individual users"""
    
    def __init__(self, username: str):
        self.username = username
    
    def update(self, message: str, data: Dict[str, Any]):
        """Print notification to console"""
        print(f"\n🔔 NOTIFICATION for {self.username}: {message}")
        if 'title' in data:
            print(f"   📌 Media: {data['title']}")
        if 'rating' in data:
            print(f"   ⭐ Rating: {data['rating']}")


class Subject:
    """Subject - manages observers and sends notifications"""
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._favorite_media: Dict[str, List[str]] = {}  # media_title -> [usernames]
    
    def attach(self, observer: Observer, media_title: str = None):
        """
        Attach observer to subject
        
        Args:
            observer: Observer to attach
            media_title: Optional - specific media to watch
        """
        if observer not in self._observers:
            self._observers.append(observer)
        
        # Track favorites
        if media_title:
            if media_title not in self._favorite_media:
                self._favorite_media[media_title] = []
            if observer.username not in self._favorite_media[media_title]:
                self._favorite_media[media_title].append(observer.username)
    
    def detach(self, observer: Observer):
        """Detach observer from subject"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, message: str, data: Dict[str, Any]):
        """
        Notify all observers
        
        Args:
            message: Notification message
            data: Additional data (title, rating, etc.)
        """
        # Notify specific users who favorited this media
        if 'title' in data and data['title'] in self._favorite_media:
            for username in self._favorite_media[data['title']]:
                for observer in self._observers:
                    if observer.username == username:
                        observer.update(message, data)
        else:
            # Notify all observers
            for observer in self._observers:
                observer.update(message, data)
    
    def get_observers_count(self):
        """Get number of observers"""
        return len(self._observers)


# Global notification subject
notification_subject = Subject()