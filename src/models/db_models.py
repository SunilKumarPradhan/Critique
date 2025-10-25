from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    reviews = relationship('Review', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}')>"


class Review(Base):
    __tablename__ = 'reviews'
    
    # Primary key - unique for each review
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to User
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Review data
    username = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    media_type = Column(String(20), nullable=False, index=True)  # 'movie', 'song', 'webshow'
    rating = Column(Float, nullable=True)
    review_text = Column(String(1000), default='')
    is_reviewed = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship('User', back_populates='reviews')
    
    # Constraints
    __table_args__ = (
        CheckConstraint('rating IS NULL OR (rating >= 1.0 AND rating <= 5.0)', 
                       name='check_rating_range'),
    )
    
    def __repr__(self):
        return f"<Review(id={self.review_id}, title='{self.title}', rating={self.rating})>"