import threading
from tabulate import tabulate
from src.database.manager import DatabaseManager
from src.services.review_service import ReviewService
from src.services.user_service import UserService
from src.services.recommendation_service import RecommendationService
from src.patterns.factory import MediaFactory
from src.cache.redis_cache import cache


class MediaReviewCLI:

    def __init__(self):
        self.db = DatabaseManager()
        self.db.create_tables()
        self.review_service = ReviewService(self.db)
        self.user_service = UserService(self.db)
        
        print("\nLoading recommendation models...")
        try:
            self.recommendation_service = RecommendationService()
            print("Recommendation system ready\n")
            
        except Exception as e:
            print(f"Recommendation system not available: {e}")
            self.recommendation_service = None
    
    def print_header(self, text):
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)
    
    def media_type_selector(self):
        print("\nSelect media type:")
        types = MediaFactory.get_all_types()
        for i, media_type in enumerate(types, 1):
            print(f"{i}. {media_type.capitalize()}")
        
        choice = input("Enter choice (1-3): ").strip()
        media_map = {'1': 'movie', '2': 'song', '3': 'webshow'}
        return media_map.get(choice)
    
    def main_menu(self):
        try:
            while True:
                self.print_header("MEDIA REVIEW SYSTEM")
                print("1. Show All Reviewers")
                print("2. Add New Reviewer")
                print("3. Review & Recommendations Menu")
                print("4. Show Statistics")
                print("5. Exit")
                
                choice = input("\nEnter your choice (1-5): ").strip()
                
                if choice == '1':
                    self.show_all_reviewers()
                elif choice == '2':
                    self.add_new_reviewer()
                elif choice == '3':
                    self.review_menu()
                elif choice == '4':
                    self.show_statistics()
                elif choice == '5':
                    print("\nGoodbye!\n")
                    break
                else:
                    print("[ERROR] Invalid choice!")
                
                if choice != '5':
                    input("\nPress Enter to continue...")
        finally:
            self.db.close_session()
    
    def show_all_reviewers(self):
        self.print_header("ALL REVIEWERS")
        users = self.db.get_all_users()
        if not users:
            print("No reviewers found in the database!")
        else:
            table_data = [
                [u.user_id, u.username, u.created_at.strftime('%Y-%m-%d %H:%M')]
                for u in users
            ]
            print(tabulate(table_data,
                          headers=['ID', 'Username', 'Joined Date'],
                          tablefmt='grid'))
            print(f"\nTotal Reviewers: {len(users)}")
    
    def add_new_reviewer(self):
        self.print_header("ADD NEW REVIEWER")
        username = input("Enter username: ").strip()

        if not username:
            print("[ERROR] Username cannot be empty!")
            return
        
        success, message = self.user_service.register_user(username)
        
        if success:
            print(f"[OK] {message}")
        else:
            print(f"[WARNING] {message}")
    
    def review_menu(self):
        while True:
            self.print_header("REVIEW & RECOMMENDATIONS")
            print("1. View All Media")
            print("2. Add New Review")
            print("3. Search by Title")
            print("4. Get Top Rated")
            print("5. Get Recommendations")
            print("6. Subscribe to Media Notifications")
            print("7. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                self.view_all_media()
            elif choice == '2':
                self.add_new_review()
            elif choice == '3':
                self.search_by_title()
            elif choice == '4':
                self.get_top_rated()
            elif choice == '5':
                self.get_recommendations()
            elif choice == '6':
                self.subscribe_to_media()
            elif choice == '7':
                break
            else:
                print("[ERROR] Invalid choice!")
            
            if choice != '7':
                input("\nPress Enter to continue...")
    
    def view_all_media(self):
        self.print_header("ALL MEDIA")
        
        grouped = self.db.get_all_reviews_grouped()
        
        has_data = False
        
        for media_type, reviews in grouped.items():
            if reviews:
                has_data = True
                print(f"\n{media_type.upper()}S ({len(reviews)} items)")
                print("-" * 70)
                
                table_data = [
                    [idx + 1, r.title, 
                     f"{r.rating:.1f}" if r.rating else "N/A",
                     "Yes" if r.is_reviewed else "No",
                     r.username]
                    for idx, r in enumerate(reviews)
                ]
                print(tabulate(table_data,
                              headers=['#', 'Title', 'Rating','By'],
                              tablefmt='simple'))
        
        if not has_data:
            print("No media found in the database!")
    
    def add_new_review(self):
        self.print_header("ADD NEW REVIEW")
        
        username = input("Enter your username: ").strip()
        if not username:
            print("[ERROR] Username cannot be empty!")
            return
        
        user = self.db.get_user(username)
        if not user:
            print(f"[WARNING] User '{username}' not found!")
            create = input("Create this user? (y/n): ").strip().lower()
            if create == 'y':
                self.user_service.register_user(username)
            else:
                return
        
        media_type = self.media_type_selector()
        if not media_type:
            print("[ERROR] Invalid media type!")
            return
        
        try:
            title = input(f"\nEnter {media_type} title: ").strip()
            if not title:
                print("[ERROR] Title cannot be empty!")
                return
            
            media = MediaFactory.create_media(media_type, title)
            print(f"\nCreating review for: {title}")
            
            rating = float(input("Enter rating (1.0 - 5.0): ").strip())
            if rating < 1.0 or rating > 5.0:
                print("[ERROR] Rating must be between 1.0 and 5.0!")
                return
            
            review_text = input("Enter review text (press Enter to skip): ").strip()
            
            print("\nSubmitting review...")
            
            def submit_review():
                success, message = self.review_service.add_review_threaded(
                    username, title, media_type, rating, review_text
                )
                if success:
                    print(f"[OK] {message}")
                else:
                    print(f"[ERROR] {message}")
            
            thread = threading.Thread(target=submit_review)
            thread.start()
            thread.join()
            
        except ValueError as e:
            print(f"[ERROR] {e}")
    
    def search_by_title(self):
        self.print_header("SEARCH BY TITLE")
        
        media_type = self.media_type_selector()
        if not media_type:
            print("[ERROR] Invalid media type!")
            return
        
        title = input(f"\nEnter {media_type} title to search: ").strip()
        if not title:
            print("[ERROR] Search term cannot be empty!")
            return
        
        results = self.db.search_by_title(title, media_type)
        
        if not results:
            print(f"\nNo {media_type}s found matching '{title}'")
        else:
            print(f"\nFound {len(results)} result(s):\n")
            table_data = [
                [r.title, r.username, 
                 f"{r.rating:.1f}" if r.rating else "Not Rated",
                 (r.review_text[:40] + "...") if len(r.review_text) > 40 else r.review_text or "No review"]
                for r in results
            ]
            print(tabulate(table_data,
                          headers=['Title', 'Reviewer', 'Rating', 'Review'],
                          tablefmt='grid'))
    
    def get_top_rated(self):
        self.print_header("GET TOP RATED")
        
        media_type = self.media_type_selector()
        if not media_type:
            print("[ERROR] Invalid media type!")
            return
        
        results = self.review_service.get_top_rated_cached(media_type, limit=5)
        
        if not results:
            print(f"\nNo rated {media_type}s found!")
        else:
            print(f"\nTop {len(results)} {media_type.capitalize()}(s):\n")
            table_data = [
                [i+1, r['title'], f"{r['avg_rating']:.2f}", f"{r['review_count']} review(s)"]
                for i, r in enumerate(results)
            ]
            print(tabulate(table_data,
                          headers=['Rank', 'Title', 'Avg Rating', 'Total Reviews'],
                          tablefmt='grid'))
    
    def get_recommendations(self):
        self.print_header("GET RECOMMENDATIONS")
        
        if not self.recommendation_service:
            print("[ERROR] Recommendation system is not available!")
            print("Please ensure .pkl model files are in the 'pickles/' folder.")
            return
        
        username = input("Enter username: ").strip()
        if not username:
            print("[ERROR] Username cannot be empty!")
            return
        
        highest_rated = self.db.get_highest_rated_by_user(username)
        
        if not highest_rated:
            print(f"[WARNING] User '{username}' hasn't reviewed anything yet!")
            return
        
        print(f"\nYour highest-rated {highest_rated.media_type}:")
        print(f"  Title: {highest_rated.title}")
        print(f"  Rating: {highest_rated.rating:.1f}")
        
        print(f"\nRecommendations based on '{highest_rated.title}'...")
    
        recommendations = self.recommendation_service.recommend(
            highest_rated.media_type,
            highest_rated.title,
            top_n=5
        )
        
        if not recommendations:
            print("\nNo recommendations available. Try reviewing more items!")
    
    # uses_service function calls for subscriptions
    def subscribe_to_media(self):
        self.print_header("SUBSCRIBE TO NOTIFICATIONS")
        
        username = input("Enter your username: ").strip()
        if not username:
            print("[ERROR] Username cannot be empty!")
            return
        
        media_title = input("Enter media title to subscribe to: ").strip()
        if not media_title:
            print("[ERROR] Media title cannot be empty!")
            return
        
        success, message = self.user_service.subscribe_to_media(username, media_title)
        
        if success:
            print(f"[OK] {message}")
        else:
            print(f"[WARNING] {message}")

    def show_statistics(self):
        self.print_header("DATABASE STATISTICS")
        
        stats = self.db.get_stats()
        
        print(f"Total Users:           {stats['users']}")
        print(f"\nMEDIA CATALOG:")
        print(f"  Total Media Items:     {stats['total_media']}")
        print(f"  Reviewed Items:        {stats['reviewed_media']}")
        print(f"  Not Yet Reviewed:      {stats['total_media'] - stats['reviewed_media']}")
        
        print(f"\nBY MEDIA TYPE:")
        print(f"  Movies:             {stats['movies']['total']} total, "
              f"{stats['movies']['reviewed']} reviewed")
        print(f"  Songs:              {stats['songs']['total']} total, "
              f"{stats['songs']['reviewed']} reviewed")
        print(f"  WebShows:           {stats['webshows']['total']} total, "
              f"{stats['webshows']['reviewed']} reviewed")


def run_cli():
    cli = MediaReviewCLI()
    cli.main_menu()


if __name__ == "__main__":
    run_cli()