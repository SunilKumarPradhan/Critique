import sys
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.manager import DatabaseManager
from src.services.review_service import ReviewService


def bulk_reviews():
    db = DatabaseManager()
    review_service = ReviewService(db)
    
    json_path = Path(__file__).parent.parent / 'data' / 'bulk.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        reviews_data = json.load(f)
    
    total = len(reviews_data)
    success = 0
    failed = 0
    
    def process_review(review_data):
        username = review_data['username']
        media_type = review_data['media_type']
        title = review_data['title']
        rating = review_data['rating']
        review_text = review_data['review_text']
        
        user = db.get_user(username)
        if not user:
            db.add_user(username)
        
        result, _ = review_service.add_review_threaded(
            username, title, media_type, rating, review_text
        )
        
        return result
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_review, review) for review in reviews_data]
        
        for future in as_completed(futures):
            if future.result():
                success += 1
            else:
                failed += 1
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Total Reviews: {total}")
    print(f"Successfully Imported: {success}")
    print(f"Failed: {failed}")
    print(f"Time Taken: {duration:.2f} seconds")
    print(f"Reviews per Second: {total/duration:.2f}")
    
    db.close_session()


if __name__ == "__main__":
    bulk_reviews()