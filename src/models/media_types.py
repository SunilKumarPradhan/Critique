from abc import ABC, abstractmethod

class Media(ABC):
    def __init__(self, title, media_type):
        self.title = title
        self.media_type = media_type
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(title='{self.title}')>"

class Movie(Media):
    def __init__(self, title):
        super().__init__(title, 'movie')

class Song(Media):
    def __init__(self, title):
        super().__init__(title, 'song')

class WebShow(Media):
    def __init__(self, title):
        super().__init__(title, 'webshow')