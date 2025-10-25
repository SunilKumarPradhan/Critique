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
       
       
       
       
    def add_review(self, username: str, title: str, media_type: str, 
                   rating: float, review_text: str = '') -> tuple[bool, str]:

        session = self.get_session()
        
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return False, f"User '{username}' not found"
        
        is_reviewed = len(review_text.strip()) > 0
        
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
    
    def get_all_reviews(self) -> list[Review]:
        session = self.get_session()
        return session.query(Review).order_by(Review.created_at.desc()).all()
    
    def get_all_reviews_grouped(self) -> dict:
        session = self.get_session()
        
        movies = session.query(Review).filter_by(media_type='movie').order_by(Review.created_at.desc()).all()
        songs = session.query(Review).filter_by(media_type='song').order_by(Review.created_at.desc()).all()
        webshows = session.query(Review).filter_by(media_type='webshow').order_by(Review.created_at.desc()).all()
        
        return {
            'movie': movies,
            'song': songs,
            'webshow': webshows
        }
    
    def get_reviews_by_media(self, title: str, media_type: str) -> list[Review]:
        session = self.get_session()
        
        return session.query(Review).filter(
            Review.title == title,
            Review.media_type == media_type
        ).order_by(Review.created_at.desc()).all()
    
    def get_reviews_by_user(self, username: str) -> list[Review]:
        session = self.get_session()
        
        return session.query(Review).filter_by(
            username=username
        ).order_by(Review.created_at.desc()).all()
    
    
    
    def search_by_title(self, title: str, media_type: str) -> list[Review]:
        session = self.get_session()
        
        return session.query(Review).filter(
            Review.title.ilike(f'%{title}%'),
            Review.media_type == media_type
        ).order_by(Review.created_at.desc()).all()
    
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
    
    def get_highest_rated_by_user(self, username: str) -> Review:
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
    
    def get_user_review_count(self, username: str) -> int:
        session = self.get_session()
        return session.query(Review).filter_by(username=username).count()
    
    def get_media_review_count(self, title: str, media_type: str) -> int:
        session = self.get_session()
        return session.query(Review).filter(
            Review.title == title,
            Review.media_type == media_type
        ).count()