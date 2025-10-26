from contextlib import contextmanager
from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker, Session
from src.models.db_models import Base, User, Media, Review, Favorite
from config.settings import DB_URL


class DatabaseManager:    
    def __init__(self):
        self.engine = create_engine(DB_URL, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._session = None
        
    def get_session(self) -> Session:
        if self._session is None:
            self._session = self.SessionLocal()
        return self._session
    
    def close_session(self):
        if self._session:
            self._session.close()
            self._session = None

    @contextmanager
    def session_scope(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def create_tables(self):
        Base.metadata.create_all(self.engine)
        print("✅ Database tables created successfully")
    
    def drop_tables(self):
        Base.metadata.drop_all(self.engine)
        print("🗑️  All database tables dropped")
      
    def add_user(self, username: str) -> tuple[bool, str]:
        session = self.get_session()
        
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            return False, f"User '{username}' already exists"
        
        user = User(username=username)
        session.add(user)
        session.commit()
        
        return True, f"User '{username}' created successfully"
    
    def get_user(self, username: str) -> User:
        session = self.get_session()
        return session.query(User).filter_by(username=username).first()
    
    def get_all_users(self) -> list[User]:
        session = self.get_session()
        return session.query(User).order_by(User.created_at.desc()).all()
    
    def delete_user(self, username: str) -> tuple[bool, str]:
        session = self.get_session()
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return False, f"User '{username}' not found"
        
        session.delete(user)
        session.commit()
        
        return True, f"User '{username}' and all their reviews deleted"
    
    def get_or_create_media(self, title: str, media_type: str) -> Media:
        session = self.get_session()
        
        media = session.query(Media).filter_by(
            title=title,
            media_type=media_type
        ).first()
        
        if not media:
            media = Media(title=title, media_type=media_type)
            session.add(media)
            session.commit()
        
        return media
    
    def get_media_by_title(self, title: str, media_type: str) -> Media:
        session = self.get_session()
        return session.query(Media).filter_by(
            title=title,
            media_type=media_type
        ).first()
       
    def add_review(self, username: str, title: str, media_type: str, 
                   rating: float, review_text: str = '') -> tuple[bool, str]:

        session = self.get_session()
        
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return False, f"User '{username}' not found"
        
        media = self.get_or_create_media(title, media_type)
        
        review = Review(
            media_id=media.media_id,
            user_id=user.user_id,
            rating=rating,
            review_text=review_text
        )
        
        session.add(review)
        session.commit()
        
        return True, f"Review added for '{title}'"
    
    def get_all_media(self) -> list[Media]:
        session = self.get_session()
        return session.query(Media).order_by(Media.created_at.desc()).all()
    
    def get_all_media_grouped(self) -> dict:
        session = self.get_session()
        
        movies = session.query(Media).filter_by(media_type='movie').order_by(Media.title).all()
        songs = session.query(Media).filter_by(media_type='song').order_by(Media.title).all()
        webshows = session.query(Media).filter_by(media_type='webshow').order_by(Media.title).all()
        
        return {
            'movie': movies,
            'song': songs,
            'webshow': webshows
        }
    
    def get_all_reviews(self) -> list[Review]:
        session = self.get_session()
        return session.query(Review).order_by(Review.created_at.desc()).all()
    
    def get_reviews_by_media(self, title: str, media_type: str) -> list[Review]:
        session = self.get_session()
        
        media = session.query(Media).filter_by(
            title=title,
            media_type=media_type
        ).first()
        
        if not media:
            return []
        
        return session.query(Review).filter_by(
            media_id=media.media_id
        ).order_by(Review.created_at.desc()).all()
    
    def get_reviews_by_user(self, username: str) -> list[Review]:
        session = self.get_session()
        
        return session.query(Review).join(User).filter(
            User.username == username
        ).order_by(Review.created_at.desc()).all()
    
    def search_by_title(self, title: str, media_type: str) -> list[Media]:
        session = self.get_session()
        
        return session.query(Media).filter(
            Media.title.ilike(f'%{title}%'),
            Media.media_type == media_type
        ).order_by(Media.title).all()
    
    def delete_review(self, review_id: int) -> tuple[bool, str]:
        session = self.get_session()
        
        review = session.query(Review).filter_by(review_id=review_id).first()
        if not review:
            return False, f"Review ID {review_id} not found"
        
        session.delete(review)
        session.commit()
        
        return True, f"Review deleted successfully"

    def get_top_rated(self, media_type: str, limit: int = 5) -> list:
        session = self.get_session()
        
        results = session.query(
            Media.title,
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.review_id).label('review_count')
        ).join(
            Review, Media.media_id == Review.media_id
        ).filter(
            Media.media_type == media_type,
            Review.rating.isnot(None)
        ).group_by(
            Media.media_id,
            Media.title
        ).order_by(
            desc('avg_rating')
        ).limit(limit).all()
        
        return results
    
    def get_highest_rated_by_user(self, username: str, media_type: str = None):
        session = self.get_session()
        
        query = session.query(
            Media.title,
            Media.media_type,
            Review.rating
        ).join(
            Review, Media.media_id == Review.media_id
        ).join(
            User, Review.user_id == User.user_id
        ).filter(
            User.username == username,
            Review.rating.isnot(None)
        )
        
        if media_type:
            query = query.filter(Media.media_type == media_type)
        
        result = query.order_by(
            desc(Review.rating),
            desc(Review.created_at)
        ).first()
        
        if result:
            class HighestRated:
                def __init__(self, title, media_type, rating):
                    self.title = title
                    self.media_type = media_type
                    self.rating = rating
            
            return HighestRated(result.title, result.media_type, result.rating)
        
        return None
    
    def get_user_review_count(self, username: str) -> int:
        session = self.get_session()
        return session.query(Review).join(User).filter(
            User.username == username
        ).count()
    
    def get_media_review_count(self, title: str, media_type: str) -> int:
        session = self.get_session()
        
        media = session.query(Media).filter_by(
            title=title,
            media_type=media_type
        ).first()
        
        if not media:
            return 0
        
        return session.query(Review).filter_by(media_id=media.media_id).count()
    
    def get_media_stats(self, media: Media) -> dict:
        session = self.get_session()
        
        reviews = session.query(Review).filter_by(media_id=media.media_id).all()
        
        total_reviews = len(reviews)
        rated_reviews = [r for r in reviews if r.rating is not None]
        
        return {
            'total_reviews': total_reviews,
            'rated_reviews': len(rated_reviews),
            'avg_rating': sum(r.rating for r in rated_reviews) / len(rated_reviews) if rated_reviews else 0.0
        }
    
    # FAVORITE METHODS
    def add_favorite(self, username: str, title: str, media_type: str) -> tuple[bool, str]:
        session = self.get_session()
        
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return False, f"User '{username}' not found"
        
        media = self.get_or_create_media(title, media_type)
        
        existing = session.query(Favorite).filter_by(
            user_id=user.user_id,
            media_id=media.media_id
        ).first()
        
        if existing:
            return False, f"'{title}' is already in your favorites"
        
        favorite = Favorite(user_id=user.user_id, media_id=media.media_id)
        session.add(favorite)
        session.commit()
        
        return True, f"'{title}' added to favorites"
    
    def remove_favorite(self, username: str, title: str, media_type: str) -> tuple[bool, str]:
        session = self.get_session()
        
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return False, f"User '{username}' not found"
        
        media = session.query(Media).filter_by(title=title, media_type=media_type).first()
        if not media:
            return False, f"Media '{title}' not found"
        
        favorite = session.query(Favorite).filter_by(
            user_id=user.user_id,
            media_id=media.media_id
        ).first()
        
        if not favorite:
            return False, f"'{title}' is not in your favorites"
        
        session.delete(favorite)
        session.commit()
        
        return True, f"'{title}' removed from favorites"
    
    def get_user_favorites(self, username: str) -> list:
        session = self.get_session()
        
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return []
        
        favorites = session.query(Media).join(Favorite).filter(
            Favorite.user_id == user.user_id
        ).order_by(Favorite.created_at.desc()).all()
        
        return favorites
    
    def get_users_who_favorited(self, title: str, media_type: str) -> list[str]:
        session = self.get_session()
        
        media = session.query(Media).filter_by(title=title, media_type=media_type).first()
        if not media:
            return []
        
        users = session.query(User.username).join(Favorite).filter(
            Favorite.media_id == media.media_id
        ).all()
        
        return [u.username for u in users]