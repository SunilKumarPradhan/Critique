"""SQLAlchemy database models"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship('Review', back_populates='user')
    
    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}')>"


class Review(Base):
    __tablename__ = 'reviews'
    
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False, index=True)
    username = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    media_type = Column(String(20), nullable=False, index=True)  # 'movie', 'song', 'webshow'
    rating = Column(Float, nullable=True)
    review_text = Column(String(1000), default='')
    is_reviewed = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    

    user = relationship('User', back_populates='reviews')
    
    # Constraints upon the table level argument 
    __table_args__ = (
        CheckConstraint('rating IS NULL OR (rating >= 1.0 AND rating <= 5.0)', 
                       name='check_rating_range'),
    )
    
    def __repr__(self):
        return f"<Review(id={self.review_id}, title='{self.title}', type='{self.media_type}', rating={self.rating})>"