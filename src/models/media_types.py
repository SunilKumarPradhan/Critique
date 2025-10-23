"""Media type classes for Factory Pattern"""
from abc import ABC, abstractmethod


class Media(ABC):
    """Abstract base class for media types"""
    
    def __init__(self, title, media_type):
        self.title = title
        self.media_type = media_type
    
    @abstractmethod
    def get_display_icon(self):
        """Return display icon for media type"""
        pass
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(title='{self.title}')>"


class Movie(Media):
    """Movie media type"""
    
    def __init__(self, title):
        super().__init__(title, 'movie')
    
    def get_display_icon(self):
        return "🎬"


class Song(Media):
    """Song media type"""
    
    def __init__(self, title):
        super().__init__(title, 'song')
    
    def get_display_icon(self):
        return "🎵"


class WebShow(Media):
    """Web show media type"""
    
    def __init__(self, title):
        super().__init__(title, 'webshow')
    
    def get_display_icon(self):
        return "📺"