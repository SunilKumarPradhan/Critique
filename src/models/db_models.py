from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reviews = relationship('Review', back_populates='user', cascade='all, delete-orphan')
    favorites = relationship('Favorite', back_populates='user', cascade='all, delete-orphan')


class Media(Base):
    __tablename__ = 'media'
    
    media_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    media_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reviews = relationship('Review', back_populates='media', cascade='all, delete-orphan')
    favorites = relationship('Favorite', back_populates='media', cascade='all, delete-orphan')
    
    __table_args__ = (
        UniqueConstraint('title', 'media_type', name='unique_media'),
    )


class Review(Base):
    __tablename__ = 'reviews'
    
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    media_id = Column(Integer, ForeignKey('media.media_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    rating = Column(Float, nullable=True)
    review_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', back_populates='reviews')
    media = relationship('Media', back_populates='reviews')


class Favorite(Base):
    __tablename__ = 'favorites'
    
    favorite_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    media_id = Column(Integer, ForeignKey('media.media_id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship('User', back_populates='favorites')
    media = relationship('Media', back_populates='favorites')
    
    __table_args__ = (
        UniqueConstraint('user_id', 'media_id', name='unique_user_favorite'),
    )