import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.manager import DatabaseManager
from src.models.db_models import Media


def populate_db():
    db = DatabaseManager()
    
    db.drop_tables()
    db.create_tables()
    
    stats = {
        'movies': 0,
        'songs': 0,
        'webshows': 0
    }
    
    json_path = Path(__file__).parent.parent / 'data' / 'media.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with db.session_scope() as session:
        for movie_data in data.get('movies', []):
            media = Media(
                title=movie_data['title'],
                media_type=movie_data['media_type']
            )
            session.add(media)
            stats['movies'] += 1
    
    with db.session_scope() as session:
        for song_data in data.get('songs', []):
            media = Media(
                title=song_data['title'],
                media_type=song_data['media_type']
            )
            session.add(media)
            stats['songs'] += 1
    
    with db.session_scope() as session:
        for show_data in data.get('webshows', []):
            media = Media(
                title=show_data['title'],
                media_type=show_data['media_type']
            )
            session.add(media)
            stats['webshows'] += 1
    
    print(f"Movies added: {stats['movies']}")
    print(f"Songs added: {stats['songs']}")
    print(f"Web Shows added: {stats['webshows']}")
    print(f"Total: {sum(stats.values())}")


if __name__ == "__main__":
    populate_db()