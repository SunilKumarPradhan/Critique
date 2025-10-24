from src.models.media_types import Movie, Song, WebShow

class MediaFactory:
    """Factory to create different media types"""
    _media_types = {
        'movie': Movie,
        'song': Song,
        'webshow': WebShow
    }
    
    @classmethod
    def create_media(cls, media_type, title):
        """
        Create media object based on type
        
        Args:
            media_type: 'movie', 'song', or 'webshow'
            title: Media title
            
        Returns:
            Media object (Movie, Song, or WebShow)
            
        Raises:
            ValueError: If media_type is invalid
        """
        media_class = cls._media_types.get(media_type.lower())
        
        if not media_class:
            raise ValueError(f"Invalid media type: {media_type}. "
                           f"Must be one of: {', '.join(cls._media_types.keys())}")
        
        return media_class(title)
    
    @classmethod
    def get_all_types(cls):
        """Get list of all supported media types"""
        return list(cls._media_types.keys())