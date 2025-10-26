import threading
from src.database.manager import DatabaseManager
from src.services.review_service import ReviewService
from src.services.user_service import UserService
from src.services.recommendation_service import RecommendationService
from src.patterns.factory import MediaFactory


class MediaReviewCLI:
    def __init__(self):
        self.db = DatabaseManager()
        self.db.create_tables()
        self.review_service = ReviewService(self.db)
        self.user_service = UserService(self.db)
        
        print("[OK]Loading recommendation models...")
        self.recommendation_service = RecommendationService()
        print("\n✓ Recommendation system ready\n")
        
    # HELPER FUNCTIONS

    def print_header(self, text):
        print("\n" + "="*30)
        print(f"  {text}")
        print("="*30)

    def media_type_selector(self):
        print("\nSelect media type:")
        types = MediaFactory.get_all_types()
        for i, media_type in enumerate(types, 1):
            print(f"  {i}. {media_type.capitalize()}")
        
        choice = input("\nEnter choice (1-3): ").strip()
        media_map = {'1': 'movie', '2': 'song', '3': 'webshow'}
        return media_map.get(choice)

    # MENU FUNCTIONS
    def main_menu(self):
        while True:
            self.print_header("MEDIA REVIEW SYSTEM")
            print("\n  1. Show All Reviewers")
            print("  2. Add New Reviewer")
            print("  3. Review Menu")
            print("  4. Subscribe to Notifications")
            print("  5. Bulk Import Reviews")
            print("  6. Exit")

            choice = input("\n  Enter your choice (1-6): ").strip()
            
            if choice == '1':
                self.show_all_reviewers()
            elif choice == '2':
                self.add_new_reviewer()
            elif choice == '3':
                self.review_menu()
            elif choice == '4':
                self.subscribe_to_media()
            elif choice == '5':
                 self.bulk_import_reviews()
            elif choice == '6':
                print("  Thank you for using Media Review System!")
                self.db.close_session()
                break
            else:
                print("\n  [ERROR] Invalid choice! Please try again.")
            
            if choice != '6':
                input("\n  Press Enter to continue...")

    def show_all_reviewers(self):
        self.print_header("ALL REVIEWERS")
        users = self.db.get_all_users()
        
        if not users:
            print("\n  No reviewers found in the database.")
        else:
            print(f"\n  {'Username':<20} {'Total Reviews':<15} {'Subscriptions':<15}")
            print("  " + "-"*50)
            for u in users:
                review_count = self.db.get_user_review_count(u.username)
                sub_count = len(self.user_service.get_subscriptions(u.username))
                print(f"  {u.username:<20} {review_count:<15} {sub_count:<15}")
            print(f"\n  Total Reviewers: {len(users)}")

    def add_new_reviewer(self):
        self.print_header("ADD NEW REVIEWER")
        username = input("\n  Enter username: ").strip()

        if not username:
            print("\n  [ERROR] Username cannot be empty!")
            return
        
        success, message = self.user_service.register_user(username)
        
        if success:
            print(f"\n  ✓ {message}")
        else:
            print(f"\n  [WARNING] {message}")

    def review_menu(self):
        while True:
            self.print_header("REVIEW MENU")
            print("\n  1. View All Media")
            print("  2. Add New Review")
            print("  3. View Reviews for Specific Media")
            print("  4. Search by Title")
            print("  5. Get Top Rated")
            print("  6. Get Recommendations")
            print("  7. Back to Main Menu")
            
            choice = input("\n  Enter your choice (1-7): ").strip()
            
            if choice == '1':
                self.view_all_media()
            elif choice == '2':
                self.add_new_review()
            elif choice == '3':
                self.view_media()
            elif choice == '4':
                self.search_by_title()
            elif choice == '5':
                self.get_top_rated()
            elif choice == '6':
                self.get_recommendations()
            elif choice == '7':
                break
            else:
                print("\n  [ERROR] Invalid choice! Please try again.")
            
            if choice != '7':
                input("\n  Press Enter to continue...")

    def subscribe_to_media(self):
        self.print_header("SUBSCRIBE TO NOTIFICATIONS")
        
        username = input("\n  Enter your username: ").strip()
        if not username:
            print("\n  [ERROR] Username cannot be empty!")
            return
        
        user = self.db.get_user(username)
        if not user:
            print(f"\n  [ERROR] User '{username}' not found!")
            return
        
        media_type = self.media_type_selector()
        
        if not media_type:
            print("\n  [ERROR] Invalid media type!")
            return
        
        grouped = self.db.get_all_reviews_grouped()
        reviews = grouped.get(media_type, [])
        
        if reviews:
            unique_titles = list(set([r.title for r in reviews]))
            print(f"\n  Available {media_type}s:")
            for i, title in enumerate(unique_titles[:10], 1):
                print(f"    {i}. {title}")
            if len(unique_titles) > 10:
                print(f"    ... and {len(unique_titles) - 10} more")
        
        media_title = input(f"\n  Enter {media_type} title to subscribe: ").strip()
        if not media_title:
            print("\n  [ERROR] Media title cannot be empty!")
            return
        
        success, message = self.user_service.subscribe_to_media(username, media_title)
        
        if success:
            print(f"\n  ✓ {message}")
            print(f"  You will be notified when anyone reviews '{media_title}'")
        else:
            print(f"\n  [WARNING] {message}")

    def bulk_import_reviews(self):
        self.print_header("BULK IMPORT (MULTI-THREADED)")
        
        import time
        start = time.time()
        
        results = self.review_service.bulk_import_reviews('bulk_reviews.json')
        
        duration = time.time() - start
        
        print(f"\n  Total: {results['total']}")
        print(f"  Success: {results['success']}")
        print(f"  Failed: {results['failed']}")
        print(f"  Time: {duration:.2f}s")


    # SUB-MENU OPTIONS 
    def view_all_media(self):
        self.print_header("ALL MEDIA ITEMS")
        
        grouped = self.db.get_all_reviews_grouped()
        
        has_data = False
        
        for media_type, reviews in grouped.items():
            if reviews:
                has_data = True
                print(f"\n  {media_type.upper()}S ({len(reviews)} reviews)")
                print("  " + "-"*30)
                print(f"  {'Title':<30} {'Rating':<10} {'Reviewer':<15}")
                print("  " + "-"*30)
                
                for r in reviews:
                    rating = f"{r.rating:.1f}/5.0" if r.rating else "N/A"
                    title = r.title[:28] + ".." if len(r.title) > 30 else r.title
                    print(f"  {title:<30} {rating:<10} {r.username:<15}")
        
        if not has_data:
            print("\n  No reviews found in the database.")

    def view_media(self):
        self.print_header("VIEW MEDIA REVIEWS")
        
        media_type = self.media_type_selector()
        if not media_type:
            print("\n  [ERROR] Invalid media type!")
            return
        
        title = input(f"\n  Enter {media_type} title: ").strip()
        if not title:
            print("\n  [ERROR] Title cannot be empty!")
            return
        
        reviews = self.db.get_reviews_by_media(title, media_type)
        
        if not reviews:
            print(f"\n  No reviews found for '{title}'")
        else:
            print(f"\n  Reviews for: {title}")
            print("  " + "-"*75)
            print(f"  {'Reviewer':<15} {'Rating':<10} {'Review':<50}")
            print("  " + "-"*75)
            
            for r in reviews:
                rating = f"{r.rating:.1f}/5.0" if r.rating else "N/A"
                review = (r.review_text[:47] + "...") if len(r.review_text) > 50 else r.review_text or "No text"
                print(f"  {r.username:<15} {rating:<10} {review:<50}")
            
            print(f"\n  Total Reviews: {len(reviews)}")

    def add_new_review(self):
        self.print_header("ADD NEW REVIEW")
        
        username = input("\n  Enter your username: ").strip()
        if not username:
            print("\n  [ERROR] Username cannot be empty!")
            return
        
        user = self.db.get_user(username)
        if not user:
            print(f"\n  [WARNING] User '{username}' not found!")
            create = input("  Create this user? (y/n): ").strip().lower()
            if create == 'y':
                self.user_service.register_user(username)
            else:
                return
        
        media_type = self.media_type_selector()
        if not media_type:
            print("\n  [ERROR] Invalid media type!")
            return
        
        title = input(f"\n  Enter {media_type} title: ").strip()
        if not title:
            print("\n  [ERROR] Title cannot be empty!")
            return
        
        existing_reviews = self.db.get_reviews_by_media(title, media_type)
        if existing_reviews:
            print(f"\n  This {media_type} has {len(existing_reviews)} existing review(s):")
            print("\n  Existing ratings:")
            for rev in existing_reviews:
                print(f"    - {rev.username}: {rev.rating}/5.0")
        
        rating_input = input("\n  Enter rating (1.0 - 5.0): ").strip()
        
        try:
            rating = float(rating_input)
        except ValueError:
            print("\n  [ERROR] Rating must be a number!")
            return
        
        if rating < 1.0 or rating > 5.0:
            print("\n  [ERROR] Rating must be between 1.0 and 5.0!")
            return
        
        review_text = input("  Enter review text (press Enter to skip): ").strip()
        
        print("\n  Submitting review...")
        
        def submit_review():
            success, message = self.review_service.add_review_threaded(
                username, title, media_type, rating, review_text
            )
            if success:
                print(f"\n  ✓ {message}")
            else:
                print(f"\n  [ERROR] {message}")
        
        thread = threading.Thread(target=submit_review)
        thread.start()
        thread.join()

    def search_by_title(self):
        self.print_header("SEARCH BY TITLE")
        
        media_type = self.media_type_selector()
        if not media_type:
            print("\n  [ERROR] Invalid media type!")
            return
        
        title = input(f"\n  Enter {media_type} title to search: ").strip()
        if not title:
            print("\n  [ERROR] Search term cannot be empty!")
            return
        
        results = self.db.search_by_title(title, media_type)
        
        if not results:
            print(f"\n  No {media_type}s found matching '{title}'")
        else:
            print(f"\n  Found {len(results)} review(s):")
            print("  " + "-"*85)
            print(f"  {'Title':<25} {'Reviewer':<15} {'Rating':<10} {'Review':<35}")
            print("  " + "-"*85)

            for r in results:
                rating = f"{r.rating:.1f}/5.0" if r.rating else "N/A"
                review = (r.review_text[:32] + "...") if len(r.review_text) > 35 else r.review_text or "No text"
                title_short = r.title[:22] + ".." if len(r.title) > 25 else r.title
                print(f"  {title_short:<25} {r.username:<15} {rating:<10} {review:<35}")

    def get_top_rated(self):
        self.print_header("TOP RATED")
        
        media_type = self.media_type_selector()
        if not media_type:
            print("\n  [ERROR] Invalid media type!")
            return
        
        results = self.review_service.get_top_rated_cached(media_type, limit=5)
        
        if not results:
            print(f"\n  No rated {media_type}s found!")
        else:
            print(f"\n  Top {len(results)} {media_type.capitalize()}(s):")
            print("  " + "-"*65)
            print(f"  {'Rank':<8} {'Title':<35} {'Avg Rating':<12} {'Reviews':<10}")
            print("  " + "-"*65)
            
            for i, r in enumerate(results, 1):
                title = r['title'][:33] + ".." if len(r['title']) > 35 else r['title']
                print(f"  {i:<8} {title:<35} {r['avg_rating']:<12.2f} {r['review_count']:<10}")

    def get_recommendations(self):
        self.print_header("RECOMMENDATIONS")
        
        if not self.recommendation_service:
            print("\n  [ERROR] Recommendation system not available!")
            return
        
        username = input("\n  Enter username: ").strip()
        if not username:
            print("\n  [ERROR] Username cannot be empty!")
            return
        
        highest_rated = self.db.get_highest_rated_by_user(username)
        
        if not highest_rated:
            print(f"\n  User '{username}' hasn't reviewed anything yet!")
            return
        
        print(f"\n  Your highest-rated {highest_rated.media_type}:")
        print(f"    Title: {highest_rated.title}")
        print(f"    Rating: {highest_rated.rating:.1f}/5.0")
        
        print(f"\n  Recommendations based on '{highest_rated.title}'...")
    
        recommendations = self.recommendation_service.recommend(
            highest_rated.media_type,
            highest_rated.title,
            top_n=5
        )
        
        if not recommendations:
            print("\n  No recommendations available.")


def run_cli():
    cli = MediaReviewCLI()
    cli.main_menu()


if __name__ == "__main__":
    run_cli()