"""Observer Pattern for review notifications"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Observer(ABC):
    
    @abstractmethod
    def update(self, message: str, data: Dict[str, Any]):
        pass


class UserObserver(Observer):
    def __init__(self, username: str):
        self.username = username
    
    def update(self, message: str, data: Dict[str, Any]):
        print(f"\n[NOTIFICATION] {self.username}: {message}")
        if 'title' in data:
            print(f"  Media: {data['title']}")
        if 'rating' in data:
            print(f"  Rating: {data['rating']}")


class Subject:    
    def __init__(self):
        self._observers: List[Observer] = []
        self._favorite_media: Dict[str, List[str]] = {}
    
    def attach(self, observer: Observer, media_title: str = None):
        if observer not in self._observers:
            self._observers.append(observer)
        
        if media_title:
            if media_title not in self._favorite_media:
                self._favorite_media[media_title] = []
            if observer.username not in self._favorite_media[media_title]:
                self._favorite_media[media_title].append(observer.username)
    
    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, message: str, data: Dict[str, Any]):
        if 'title' in data and data['title'] in self._favorite_media:
            for username in self._favorite_media[data['title']]:
                for observer in self._observers:
                    if observer.username == username:
                        observer.update(message, data)
        else:
            for observer in self._observers:
                observer.update(message, data)
    
    def get_observers_count(self):
        return len(self._observers)


notification_subject = Subject()