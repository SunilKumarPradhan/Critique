# 📺 Media Review System

A production-grade media review system with design patterns, caching, and multithreading.

## 🎯 Features

- **Factory Pattern**: Structured approach to handling different media types (Movie, Song, WebShow)
- **Observer Pattern**: Real-time notifications when reviews are added
- **Redis Caching**: Fast data retrieval for frequently accessed reviews
- **Multithreading**: Concurrent review submissions without data corruption
- **DB-Centric Queries**: All heavy lifting done by SQLite (GROUP BY, ORDER BY, LIMIT)

## 📋 Requirements

- Python 3.10+
- Redis (running on Docker or localhost)
- SQLite (included with Python)

## 🚀 Installation

1. **Activate virtual environment**
   ```powershell
   .\venv\Scripts\activate