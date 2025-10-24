from src.models.media_types import Movie, Song, WebShow

class MediaFactory:
    _media_types = {
        'movie': Movie, #movie is the type and Movie is the class
        'song': Song, #song is the type and Song is the class
        'webshow': WebShow #webshow is the type and WebShow is the class
    }
    
    @classmethod
    def create_media(cls, media_type, title):
        media_class = cls._media_types.get(media_type.lower())
        
        if not media_class:
            raise ValueError(f"Invalid media type: {media_type}. "
                           f"Must be one of: {', '.join(cls._media_types.keys())}")
        
        return media_class(title)
    
    @classmethod
    def get_all_types(cls):
        return list(cls._media_types.keys())