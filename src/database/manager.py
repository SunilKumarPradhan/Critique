from contextlib import contextmanager
from sqlalchemy import create_engine, desc, func
from sqlalchemy.orm import sessionmaker, Session
from src.models.db_models import Base, User, Review
from config.settings import DB_URL


class DatabaseManager:
    
    def __init__(self):

        self.engine = create_engine(DB_URL, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._session = None
        
        
# SESSION MANAGEMENT
    def get_session(self) -> Session:
        if self._session is None:
            self._session = self.SessionLocal()
        return self._session
    
    def close_session(self):
        if self._session:
            self._session.close()
            self._session = None



# CONTEXT MANAGEMENT
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope for database operations"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
# TABLE OPERATIONS  
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(self.engine)
        print("✅ Database tables created")
    
    def drop_tables(self):
        """Drop all database tables"""
        Base.metadata.drop_all(self.engine)
        print("🗑️  Database tables dropped")
    
# USER OPERATIONS  
    
    def add_user(self, username: str) -> tuple[bool, str]:
        session = self.get_session()
        
        # Check if user already exists
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            return False, f"User '{username}' already exists"
        
        user = User(username=username)
        session.add(user)
        session.commit()
        
        return True, f"User '{username}' created successfully"
    
    def get_user(self, username: str):
        session = self.get_session()
        return session.query(User).filter_by(username=username).first()
    
    def get_all_users(self):
        session = self.get_session()
        return session.query(User).order_by(User.created_at.desc()).all()
    
# REVIEW OPERATIONS  
    
    def add_review(self, username: str, title: str, media_type: str, 
                   rating: float, review_text: str = '') -> tuple[bool, str]:

        session = self.get_session()
        
        user = session.query(User).filter_by(username=username).first() #check user exists
        if not user:
            return False, f"User '{username}' not found"
        
        is_reviewed = len(review_text.strip()) > 0 #if there is no review text , it will be false
        
        review = Review(
            user_id=user.user_id,
            username=username,
            title=title,
            media_type=media_type,
            rating=rating,
            review_text=review_text,
            is_reviewed=is_reviewed
        )
        session.add(review)
        session.commit()
        
        return True, f"Review added for '{title}'"
    
    def update_or_create_review(self, username: str, title: str, media_type: str,
                                rating: float, review_text: str = '') -> tuple[bool, str]:
        """
        Update existing media entry OR create new one
        
        - If media exists (by title + type), UPDATE it with user's review
        - If media doesn't exist, CREATE new entry
        """
        session = self.get_session()
        
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return False, f"User '{username}' not found"
        
        # Check if media already exists (by title and media_type)
        existing_media = session.query(Review).filter_by(
            title=title,
            media_type=media_type
        ).first()
        
        is_reviewed = len(review_text.strip()) > 0
        
        if existing_media:
            # UPDATE existing entry
            existing_media.user_id = user.user_id
            existing_media.username = username
            existing_media.rating = rating
            existing_media.review_text = review_text
            existing_media.is_reviewed = is_reviewed
            session.commit()
            return True, f"Updated review for '{title}'"
        
        else:
            # CREATE new entry
            review = Review(
                user_id=user.user_id,
                username=username,
                title=title,
                media_type=media_type,
                rating=rating,
                review_text=review_text,
                is_reviewed=is_reviewed
            )
            session.add(review)
            session.commit()
            return True, f"Added new review for '{title}'"
    
    def get_all_reviews_grouped(self):
        session = self.get_session()
        
        movies = session.query(Review).filter_by(media_type='movie').order_by(Review.title).all()
        songs = session.query(Review).filter_by(media_type='song').order_by(Review.title).all()
        webshows = session.query(Review).filter_by(media_type='webshow').order_by(Review.title).all()
        
        return {
            'movie': movies,
            'song': songs,
            'webshow': webshows
        }
    
    def search_by_title(self, title: str, media_type: str):
        session = self.get_session()
        
        return session.query(Review).filter(
            Review.title.ilike(f'%{title}%'),
            Review.media_type == media_type
        ).all()
    
    def get_top_rated(self, media_type: str, limit: int = 5):
        session = self.get_session()
        
        results = session.query(
            Review.title,
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.review_id).label('review_count')
        ).filter(
            Review.media_type == media_type,
            Review.rating.isnot(None)
        ).group_by(
            Review.title
        ).order_by(
            desc('avg_rating')
        ).limit(limit).all()
        
        return results
    
    def get_highest_rated_by_user(self, username: str):
        session = self.get_session()
        
        highest = session.query(Review).filter_by(
            username=username
        ).filter(
            Review.rating.isnot(None)
        ).order_by(
            desc(Review.rating),
            desc(Review.created_at)
        ).first()
        
        return highest
    
# STATISTICS  this is optional
    
    def get_stats(self):
        session = self.get_session()
        
        total_users = session.query(User).count()
        
        total_media = session.query(Review).count()

        reviewed_media = session.query(Review).filter_by(is_reviewed=True).count() 
        
        movie_total = session.query(Review).filter_by(media_type='movie').count()
        movie_reviewed = session.query(Review).filter_by(media_type='movie', is_reviewed=True).count()
        
        song_total = session.query(Review).filter_by(media_type='song').count()
        song_reviewed = session.query(Review).filter_by(media_type='song', is_reviewed=True).count()
        
        webshow_total = session.query(Review).filter_by(media_type='webshow').count()
        webshow_reviewed = session.query(Review).filter_by(media_type='webshow', is_reviewed=True).count()
        
        return {
            'users': total_users,
            'total_media': total_media,
            'reviewed_media': reviewed_media,
            'movies': {'total': movie_total, 'reviewed': movie_reviewed},
            'songs': {'total': song_total, 'reviewed': song_reviewed},
            'webshows': {'total': webshow_total, 'reviewed': webshow_reviewed}
        }