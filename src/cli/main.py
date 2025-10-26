import threading
from src.database.manager import DatabaseManager
from src.services.review_service import ReviewService
from src.services.user_service import UserService
from src.services.recommendation_service import RecommendationService


class MediaReviewCLI:
    
    #HELPER
    def __init__(self):
        self.db = DatabaseManager()
        self.db.create_tables()
        self.review_service = ReviewService(self.db)
        self.user_service = UserService(self.db)
        
        print("[OK] Loading recommendation models...")
        self.recommendation_service = RecommendationService()
        print("\n✓ Recommendation system ready\n")
        
    def print_header(self, text):
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)

    def media_type_selector(self):
        print("\nSelect media type:")
        print("  1. Movie")
        print("  2. Song")
        print("  3. Webshow")
        
        choice = input("\nEnter choice (1-3): ").strip()
        return {'1': 'movie', '2': 'song', '3': 'webshow'}.get(choice)
    
    def _register_existing_users(self):
        from src.patterns.observer import notification_subject
        users = self.db.get_all_users()
        for user in users:
            notification_subject.register_observer(user.username)
        if users:
            print(f"✅ Registered {len(users)} users for notifications")
           
    #MENU 
    def main_menu(self):
        while True:
            self.print_header("MEDIA REVIEW SYSTEM")
            print("\n  1. Show All Reviewers")
            print("  2. Add New Reviewer")
            print("  3. Add Review")
            print("  4. View All Media")
            print("  5. Search Media")
            print("  6. Top Rated")
            print("  7. Get Recommendations")
            print("  8. Add to Favorites")
            print("  9. Remove from Favorites")
            print("  10. Exit")

            choice = input("\n  Enter your choice (1-10): ").strip()
            
            if choice == '1':
                self.show_all_reviewers()
            elif choice == '2':
                self.add_new_reviewer()
            elif choice == '3':
                self.add_new_review()
            elif choice == '4':
                self.view_all_media()
            elif choice == '5':
                self.search_by_title()
            elif choice == '6':
                self.get_top_rated()
            elif choice == '7':
                self.get_recommendations()
            elif choice == '8':
                self.add_to_favorites()
            elif choice == '9':
                self.remove_from_favorites()
            elif choice == '10':
                print("\n  Thank you for using Media Review System!")
                self.db.close_session()
                break
            else:
                print("\n  [ERROR] Invalid choice!")
            
            if choice != '10':
                input("\n  Press Enter to continue...")

    #REVIEW
    def show_all_reviewers(self):
        self.print_header("ALL REVIEWERS")
        users = self.db.get_all_users()
        
        if not users:
            print("\n  No reviewers found.")
            return
        
        print(f"\n  {'Username':<20} {'Reviews':<15} {'Favorites':<15}")
        print("  " + "-"*50)
        for u in users:
            review_count = self.db.get_user_review_count(u.username)
            fav_count = len(self.user_service.get_favorites(u.username))
            print(f"  {u.username:<20} {review_count:<15} {fav_count:<15}")
            
    def add_new_reviewer(self):
        self.print_header("ADD NEW REVIEWER")
        username = input("\n  Enter username: ").strip()

        if not username:
            print("\n  [ERROR] Username cannot be empty!")
            return
        
        success, message = self.user_service.register_user(username)
        print(f"\n  {'✓' if success else '[WARNING]'} {message}")

    def add_new_review(self):
        self.print_header("ADD NEW REVIEW")
        
        username = input("\n  Enter your username: ").strip()
        if not username:
            print("\n  [ERROR] Username cannot be empty!")
            return
        
        if not self.db.get_user(username):
            create = input(f"  User '{username}' not found. Create? (y/n): ").strip().lower()
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
        
        rating_input = input("  Enter rating (1.0 - 5.0): ").strip()
        try:
            rating = float(rating_input)
            if rating < 1.0 or rating > 5.0:
                print("\n  [ERROR] Rating must be between 1.0 and 5.0!")
                return
        except ValueError:
            print("\n  [ERROR] Rating must be a number!")
            return
        
        review_text = input("  Enter review text (optional): ").strip()
        
        def submit():
            success, message = self.review_service.add_review_threaded(
                username, title, media_type, rating, review_text
            )
            print(f"\n  {'✓' if success else '[ERROR]'} {message}")
        
        thread = threading.Thread(target=submit)
        thread.start()
        thread.join()


    #MEDIA
    def view_all_media(self):
        self.print_header("ALL MEDIA ITEMS")
        grouped = self.db.get_all_media_grouped()
        
        has_data = False
        for media_type, media_list in grouped.items():
            if media_list:
                has_data = True
                print(f"\n  {media_type.upper()}S ({len(media_list)})")
                print("  " + "-"*60)
                for media in media_list[:10]:
                    stats = self.db.get_media_stats(media)
                    avg = f"{stats['avg_rating']:.1f}/5" if stats['rated_reviews'] > 0 else "N/A"
                    print(f"  {media.title[:45]:<45} | {stats['total_reviews']} reviews | {avg}")
                if len(media_list) > 10:
                    print(f"  ... and {len(media_list) - 10} more")
        
        if not has_data:
            print("\n  No media found.")

    def search_by_title(self):
        self.print_header("SEARCH MEDIA")
        
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
            print(f"\n  Found {len(results)} {media_type}(s):")
            print("  " + "-"*60)
            for media in results:
                stats = self.db.get_media_stats(media)
                avg = f"{stats['avg_rating']:.1f}/5" if stats['rated_reviews'] > 0 else "N/A"
                print(f"  {media.title[:45]:<45} | {stats['total_reviews']} reviews | {avg}")

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
            print("  " + "-"*60)
            for i, r in enumerate(results, 1):
                print(f"  {i}. {r['title'][:40]:<40} | {r['avg_rating']:.1f}/5 ({r['review_count']} reviews)")

    def get_recommendations(self):
        self.print_header("RECOMMENDATIONS")
        
        username = input("\n  Enter username: ").strip()
        if not username or not self.db.get_user(username):
            print("\n  [ERROR] User not found!")
            return
        
        media_type = self.media_type_selector()
        if not media_type:
            print("\n  [ERROR] Invalid media type!")
            return
        
        highest_rated = self.db.get_highest_rated_by_user(username, media_type)
        
        if not highest_rated:
            print(f"\n  [INFO] You haven't rated any {media_type}s yet!")
            return
        
        print(f"\n  Your highest-rated {media_type}: {highest_rated.title} ({highest_rated.rating}/5)")
        print(f"  Finding recommendations...\n")
        
        recommendations = self.recommendation_service.recommend(
            highest_rated.media_type, highest_rated.title, top_n=5
        )
        
        if recommendations:
            print("  Recommendations:")
            print("  " + "-"*50)
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec['title']} (Match: {rec['score']}%)")
        else:
            print(f"  [INFO] No recommendations available.")


    #FAVOURITE
    def add_to_favorites(self):
        self.print_header("ADD TO FAVORITES")
        
        username = input("\n  Enter your username: ").strip()
        if not username or not self.db.get_user(username):
            print("\n  [ERROR] User not found!")
            return
        
        media_type = self.media_type_selector()
        if not media_type:
            print("\n  [ERROR] Invalid media type!")
            return
        
        title = input(f"\n  Enter {media_type} title: ").strip()
        if not title:
            print("\n  [ERROR] Title cannot be empty!")
            return
        
        success, message = self.user_service.add_to_favorites(username, title, media_type)
        print(f"\n  {'✓' if success else '[WARNING]'} {message}")
        if success:
            print(f"  You'll be notified when someone reviews '{title}'")

    def remove_from_favorites(self):
        self.print_header("REMOVE FROM FAVORITES")
        
        username = input("\n  Enter your username: ").strip()
        if not username or not self.db.get_user(username):
            print("\n  [ERROR] User not found!")
            return
        
        favorites = self.user_service.get_favorites(username)
        
        if not favorites:
            print("\n  You have no favorites!")
            return
        
        print(f"\n  Your Favorites:")
        for i, media in enumerate(favorites, 1):
            print(f"  {i}. [{media.media_type}] {media.title}")
        
        choice = input(f"\n  Select favorite to remove (1-{len(favorites)}): ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(favorites):
                media = favorites[idx]
                success, message = self.user_service.remove_from_favorites(
                    username, media.title, media.media_type
                )
                print(f"\n  {'✓' if success else '[ERROR]'} {message}")
            else:
                print("\n  [ERROR] Invalid choice!")
        except ValueError:
            print("\n  [ERROR] Please enter a valid number!")


def run_cli():
    cli = MediaReviewCLI()
    cli.main_menu()


if __name__ == "__main__":
    run_cli()