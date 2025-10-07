import uuid
from datetime import datetime, timedelta
import qrcode
from services import notification_service
from utils import SEAT_RESERVATION
from events import event_bus
from states import AvailableState


class USER:
    def __init__(self, name, login, password, email=None):  
        self.name = name
        self.login = login
        self.email = email if email else f"{login}@example.com" 
        self.__password = password
        self.booking_history = []
        self.id = str(uuid.uuid4())
        self.user_type = "regular"
        self.created_at = datetime.now()

    @property
    def password(self):
        return self.__password
    
    @password.setter
    def password(self, new_password):
        if not isinstance(new_password, str) or len(new_password) < 5:
            print("The password must be a string and have at least 5 characters.")
        else:
            self.__password = new_password
    
    def add_booking(self, ticket):
        self.booking_history.append(ticket)

    def remove_booking(self, ticket):
        if ticket in self.booking_history:
            self.booking_history.remove(ticket)

    def view_booking_history(self):
        if not self.booking_history:
            print("No past bookings.")
            return
        
        print("\n Your Booking History:")
        print("=" * 50)
        for i, ticket in enumerate(self.booking_history, 1):
            print(f"\n[{i}] {ticket.name.upper()} TICKET")
            print("-" * 30)
            print(f" Movie: {ticket.showtime.movie.name}")
            print(f" Time: {ticket.showtime.time}")
            print(f" Room: {ticket.showtime.screen_number}")
            print(f" Seat: {ticket.seat.row_and_number}")
            print(f" Price: R$ {ticket.price:.2f}")
            print("-" * 30)

    def view_notifications(self, unread_only=False):
        notifications = notification_service.get_user_notifications(self.id, unread_only)
        if not notifications:
            print("No notifications.")
            return
        
        print(f"\nNotifications {'(Unread only)' if unread_only else ''}:")
        print("=" * 50)
        for i, notification in enumerate(notifications, 1):
            status = "(!)NEW" if not notification['read'] else "(✓) READ"
            timestamp = notification['timestamp'].strftime("%d/%m/%Y %H:%M")
            print(f"\n[{i}] {status} [{notification['type'].upper()}] - {timestamp}")
            print(f"  {notification['message']}")
            if notification['data']:
                print(f"  Details: {notification['data']}")
            print("-" * 40)
        return notifications

class ADMIN(USER):
    def __init__(self, name, login, password, email=None):
        super().__init__(name, login, password, email)
        self.user_type = "admin" 
        self.permissions = ["manage_movies", "manage_cinemas", "manage_coupons", "view_reports", "send_notifications"]

class SEAT:
    def __init__(self, row_and_number):
        if isinstance(row_and_number, str):
            self.row = row_and_number[0]
            self.number = row_and_number[1:]
        else:
            self.row = row_and_number
            self.number = ""
        self.row_and_number = f"{self.row}{self.number}"
        self.reservation_history = []
        self.reservation_expiry = None
        
        self.state = AvailableState()
    
    @property
    def is_reserved(self):
        return self.state.get_status() != "Available"
    
    def temp_reserve(self, user, minutes=10):
        return self.state.reserve(self, user, minutes)
    
    def reserver(self, user, minutes=0):  
        return self.state.reserve(self, user, minutes)

    def release(self, user=None): 
        return self.state.release(self, user)
    
    def confirm(self):
        return self.state.confirm(self)

    def check_expiry(self):
        return self.state.check_expiry(self)
    
    def get_status(self):
        return self.state.get_status()
    
    def get_history(self):
        if not self.reservation_history:
            print(f"No history for seat {self.row_and_number}")
            return
            
        print(f"\nHistory for seat {self.row_and_number}:")
        print("=" * 50)
        for entry in self.reservation_history:
            time_str = entry['time'].strftime("%d/%m/%Y %H:%M")
            action = "RESERVED" if entry['action'] == 'reserved' else "RELEASED"
            expires = f" (Expires: {entry['expires_at'].strftime('%H:%M')})" if entry.get('expires_at') else ""
            
            print(f"\n {time_str}{expires}")
            print(f" {entry['user_name']} (ID: {entry['user_id']})")
            print(f" Action: {action}")
            print("-" * 30)


class SHOWTIME:
    def __init__(self, movie, time, screen_number, seats):
        self.movie = movie
        self.time = time
        self.screen_number = screen_number
        self.seats = seats 

    def list_available_seats(self):
        available_seats = [seat.row_and_number for seat in self.seats if not seat.is_reserved]
        print(f"Available seats for '{self.movie.name}' at {self.time}: {', '.join(available_seats)}")
        return available_seats    

class MOVIE:
    def __init__(self, name, duration_in_minutes, genre):
        self.id = str(uuid.uuid4())
        self.name = name
        self.duration_in_minutes = duration_in_minutes
        self.genre = genre
        self.showtimes = []
        self.reviews = []
        self.total_tickets_sold = 0
        self.total_revenue = 0.0

    @property
    def average_ticket_price(self):
        if self.total_tickets_sold == 0:
            return 0.0
        return self.total_revenue / self.total_tickets_sold
    
    def add_showtime(self, time, screen_number, seats):
        new_showtime = SHOWTIME(self, time, screen_number, seats)
        self.showtimes.append(new_showtime)
    
    def list_showtimes(self):
        if not self.showtimes:
            print(f"No sessions available at {self.name}.") 
            return
        
        print(f"Sessions available at {self.name}:")
        for showtime in self.showtimes:
            available_count = len([s for s in showtime.seats if not s.is_reserved])
            print(f"- Time: {showtime.time} | Room: {showtime.screen_number} | seats available: {available_count}")        
    
    def add_review(self, rating, comment):
        self.reviews.append({"rating": rating, "comment": comment})

    def get_average_rating(self):
        if not self.reviews:
            return "N/A"
        total_rating = sum(review["rating"] for review in self.reviews)
        return total_rating / len(self.reviews)

class CINEMA:
    def __init__(self, name):
        self.name = name
        self.movies = []
    
    def add_movie(self, movie):
        self.movies.append(movie)
    
    def list_movies(self):
        if not self.movies:
            print("No movies available at this time.")
            return
        
        print(f"\nMovies available at {self.name}:\n")  
        for movie in self.movies:
            movie.list_showtimes()
            print("-" * 20)