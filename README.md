# 🎬 Critique - Media Review System

A comprehensive media review and recommendation system built with Python, featuring design patterns, caching, and multithreading capabilities.

## 🎯 Features

- **Multi-Media Support**: Review and rate movies, songs, and web series
- **Smart Recommendations**: Get personalized recommendations based on your ratings
- **Real-time Notifications**: Subscribe to media titles and get notified of new reviews
- **Caching System**: Redis-based caching for improved performance
- **Thread-Safe Operations**: Concurrent review submissions with data integrity
- **Design Patterns**:
  - Factory Pattern for media type handling
  - Observer Pattern for notification system
- **CLI Interface**: User-friendly command-line interface

## 🏗️ Project Structure

```
critique/
├── config/               # Configuration settings
│   └── settings.py      # Global settings and constants
├── src/                 # Source code
│   ├── cache/          # Caching implementation
│   │   └── redis_cache.py
│   ├── cli/            # Command-line interface
│   │   └── main.py     # Main CLI implementation
│   ├── database/       # Database operations
│   │   └── manager.py  # SQLAlchemy database manager
│   ├── models/         # Data models
│   │   ├── db_models.py    # SQLAlchemy models
│   │   └── media_types.py  # Media type definitions
│   ├── patterns/       # Design pattern implementations
│   │   ├── factory.py     # Media factory pattern
│   │   └── observer.py    # Notification observer
│   └── services/       # Business logic services
│       ├── recommendation_service.py
│       ├── review_service.py
│       └── user_service.py
├── scripts/            # Utility scripts
├── pickles/           # Model files (gitignored)
└── requirements.txt   # Project dependencies
```

## � Requirements

- Python 3.10 or higher
- Redis server (for caching)
- SQLite (included with Python)
- Required Python packages:
  - SQLAlchemy
  - Redis
  - scikit-learn
  - pandas
  - loguru

## 🚀 Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SunilKumarPradhan/Critique.git
   cd Critique
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/MacOS:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start Redis server:
   ```bash
   # Make sure Redis is running on localhost:6379
   ```

5. Run the application:
   ```bash
   python run.py
   ```

## 💡 Usage

1. **Adding a New User**:
   - Select "Add New Reviewer" from main menu
   - Enter username when prompted

2. **Adding Reviews**:
   - Go to "Review Menu"
   - Select "Add New Review"
   - Follow the prompts to add your review

3. **Getting Recommendations**:
   - Navigate to "Review Menu"
   - Select "Get Recommendations"
   - Enter your username
   - Get personalized recommendations based on your ratings

4. **Searching Media**:
   - Use "Search by Title" in Review Menu
   - Enter title to search across movies, songs, or web series

5. **Subscribing to Notifications**:
   - Select "Subscribe to Notifications" from main menu
   - Choose media type and title
   - Get notified when new reviews are added

## 🔒 Data Storage

- Reviews and user data are stored in SQLite database
- Recommendation models are stored in pickle files
- Redis is used for caching frequently accessed data

## 🤝 Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

- Sunil Kumar Pradhan
- GitHub: [@SunilKumarPradhan](https://github.com/SunilKumarPradhan)