from typing import Dict, Set, Any


class Observer:  
    def update(self, message: str, data: Dict[str, Any]):
        pass


class UserObserver(Observer):    
    def __init__(self, username: str):
        self.username = username
    
    def update(self, message: str, data: Dict[str, Any]):
        if data.get('username') != self.username:
            print(f"  [🔔 NOTIFICATION for {self.username}]")
            print(f"  New review for your favorite '{data['title']}'")
            print(f"  Reviewer: {data['username']} | Rating: {data['rating']:.1f}/5.0")
            print()


class NotificationSubject:
    def __init__(self):
        self._observers: Dict[str, UserObserver] = {}
    
    def register_observer(self, username: str):
        if username not in self._observers:
            self._observers[username] = UserObserver(username)
    
    def remove_observer(self, username: str):
        if username in self._observers:
            del self._observers[username]
    
    def notify_users(self, usernames: list[str], message: str, data: Dict[str, Any]):
        for username in usernames:
            if username in self._observers:
                self._observers[username].update(message, data)


notification_subject = NotificationSubject()