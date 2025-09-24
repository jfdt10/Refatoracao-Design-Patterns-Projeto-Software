import sys
import qrcode
from datetime import datetime, timedelta
import uuid
from abc import ABC, abstractmethod

BOOKING_CONFIRMED = "booking_confirmed"
NEW_MOVIE = "new_movie"
NEW_SHOWTIME = "new_showtime"
DISCOUNT_COUPON = "discount_coupon"
SEAT_RESERVATION = "seat_reservation"
PAYMENT_SUCCESS = "payment_success"

PERCENTAGE = "percentage"
FIXED_AMOUNT = "fixed_amount"

class NotificationService:
    def __init__(self):
        self.notifications = []
    
    def send_notification(self, user, notification_type, message, data=None):
        notification = {
            'id': str(uuid.uuid4()),
            'user_id': user.id,
            'user_name': user.name,
            'user_email': user.email,
            'type': notification_type,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now(),
            'read': False
        }
        self.notifications.append(notification)
        
        print(f"\nNOTIFICATION SENT TO {user.name} ({user.email})")
        print(f" Type: {notification_type.upper()}")
        print(f" Message: {message}")
        print("-" * 50)
        
        return notification['id']
    
    def get_user_notifications(self, user_id, unread_only=False):
        user_notifications = [n for n in self.notifications if n['user_id'] == user_id]
        if unread_only:
            user_notifications = [n for n in user_notifications if not n['read']]
        return user_notifications
    
    def mark_as_read(self, notification_id):
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                return True
        return False

class Coupon:
    def __init__(self, code, coupon_type, value, description, valid_until=None, 
                 min_purchase=0, max_uses=None, applicable_cinemas=None, 
                 applicable_movies=None, user_type=None):
        self.code = code.upper()
        self.type = coupon_type
        self.value = value
        self.description = description
        self.valid_until = valid_until
        self.min_purchase = min_purchase
        self.max_uses = max_uses
        self.uses_count = 0
        self.applicable_cinemas = applicable_cinemas or []
        self.applicable_movies = applicable_movies or []
        self.user_type = user_type
        self.is_active = True
    
    def is_valid(self):
        if not self.is_active:
            return False
        if self.valid_until and datetime.now() > self.valid_until:
            return False
        if self.max_uses and self.uses_count >= self.max_uses:
            return False
        return True
    
    def can_apply(self, total_amount, cinema_name=None, movie_name=None, user_type=None):
        if not self.is_valid():
            return False
        if total_amount < self.min_purchase:
            return False
        if self.applicable_cinemas and cinema_name not in self.applicable_cinemas:
            return False
        if self.applicable_movies and movie_name not in self.applicable_movies:
            return False
        if self.user_type and user_type != self.user_type:
            return False
        return True
    
    def apply_discount(self, total_amount):
        if self.type == PERCENTAGE:
            discount = total_amount * (self.value / 100)
            return max(0, total_amount - discount), discount
        elif self.type == FIXED_AMOUNT:
            discount = min(self.value, total_amount)
            return max(0, total_amount - discount), discount
        return total_amount, 0
    
    def use(self):
        self.uses_count += 1

class PromotionManager:
    def __init__(self):
        self.coupons = {}
        self.initialize_default_coupons()
    
    def initialize_default_coupons(self):
        self.add_coupon(Coupon("STUDENT50", PERCENTAGE, 50, 
                               "50% off for students", user_type="student"))
        self.add_coupon(Coupon("WELCOME10", FIXED_AMOUNT, 10,
                               "R$10 off for new users", min_purchase=20, max_uses=1))
        self.add_coupon(Coupon("CINEMA20", PERCENTAGE, 20,
                               "20% off on all tickets", 
                               valid_until=datetime.now() + timedelta(days=30)))   
    def add_coupon(self, coupon):
        self.coupons[coupon.code] = coupon
    
    def get_coupon(self, code):
        return self.coupons.get(code.upper())
    
    def list_active_coupons(self):
        return [c for c in self.coupons.values() if c.is_valid()]


class PRODUCT(ABC):

    @abstractmethod
    def __init__(self, name, price):
        self.name = name  
        self.price = price

    @abstractmethod
    def purchase_product(self):
        pass

    @abstractmethod
    def cancel_purchase(self):
        pass

    @abstractmethod
    def promotion(self, coupon=None):
        pass

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
        self.permissions = ["manage_movies", "manage_cinemas", "manage_coupons", "view_reports"]
    
    def add_movie_to_cinema(self, cinema, movie):
        if "manage_movies" not in self.permissions:
            print("Access denied: Insufficient permissions.")
            return False
        
        cinema.add_movie(movie)
        self.notify_new_movie(movie, cinema)
        print(f"Movie '{movie.name}' added to {cinema.name} successfully!")
        return True
    
    def notify_new_movie(self, movie, cinema):
        for user in usuarios_registrados.values():
            if user.user_type != "admin":
                message = f" New movie available: '{movie.name}' at {cinema.name}!"
                data = {"movie_name": movie.name, "cinema_name": cinema.name, "genre": movie.genre}
                notification_service.send_notification(user, NEW_MOVIE, message, data)

    def add_showtime_to_movie(self, movie, time, screen_number, seats):
        if "manage_movies" not in self.permissions:
            print("Access denied: Insufficient permissions.")
            return False
        
        movie.add_showtime(time, screen_number, seats)
        self.notify_new_showtime(movie, time)
        print(f"Showtime {time} added to '{movie.name}' successfully!")
        return True
    
    def notify_new_showtime(self, movie, time):
        for user in usuarios_registrados.values():
            if user.user_type != "admin":
                message = f"New showtime available: '{movie.name}' at {time}!"
                data = {"movie_name": movie.name, "time": time}
                notification_service.send_notification(user, NEW_SHOWTIME, message, data)
    
    def create_coupon(self, code, coupon_type, value, description, **kwargs):
        if "manage_coupons" not in self.permissions:
            print("Access denied: Insufficient permissions.")
            return False
        
        coupon = Coupon(code, coupon_type, value, description, **kwargs)
        promotion_manager.add_coupon(coupon)
        
        self.notify_new_coupon(coupon)
        print(f"Coupon '{code}' created successfully!")
        return True
    
    def notify_new_coupon(self, coupon):
        for user in usuarios_registrados.values():
            if user.user_type != "admin":
                message = f" New discount coupon available: {coupon.code} - {coupon.description}"
                data = {"coupon_code": coupon.code, "description": coupon.description}
                notification_service.send_notification(user, DISCOUNT_COUPON, message, data)

    def view_reports(self):
        if "view_reports" not in self.permissions:
            print("Access denied: Insufficient permissions.")
            return False
        
        print("\nMovie Reports:")
        print("=" * 50)
        total_bookings = sum(len(user.booking_history) for user in usuarios_registrados.values())
        print(f" System-Wide Total Bookings: {total_bookings}")
        print(f" System-Wide Active Coupons: {len(promotion_manager.list_active_coupons())}")
        print("-" * 50)

        for cinema in cinemas.values():
            for movie in cinema.movies:
                print(f"\nMovie: {movie.name} ({cinema.name})")
                print("-" * 30)
                print(f" Total tickets sold: {movie.total_tickets_sold}")
                print(f" Total revenue: R$ {movie.total_revenue:.2f}")
                print(f" Average ticket price: R$ {movie.average_ticket_price:.2f}")
                print("-" * 30)
        return True
    
class POPCORN(PRODUCT):
    def __init__(self, name, price, size):
        super().__init__(name, price)
        self.size = size
    
    def purchase_product(self):
        if self.size == "L":
            self.price = 7.5
            self.name = "Pipoca Grande"
        elif self.size == "M":
            self.price = 6.0
            self.name = "Pipoca Média"
        else:
            self.price = 4.5
            self.name = "Pipoca Pequena"
        return self.price
    
    def cancel_purchase(self):
        print(f"Popcorn of size {self.size} purchase cancelled.")    

    def promotion(self, coupon=None):
        if coupon and coupon.can_apply(self.price):
            new_price, discount = coupon.apply_discount(self.price)
            self.price = new_price
            print(f"Coupon '{coupon.code}' applied to popcorn! Discount: R${discount:.2f}")
        return self.price
        
class TICKET(PRODUCT):
    def __init__(self, name, price, seat, showtime):
        super().__init__(name, price)
        self.seat = seat
        self.showtime = showtime
    
    def purchase_product(self):
        print(f"Ticket for seat {self.seat.row_and_number} purchased successfully.")
    
    def cancel_purchase(self):
        print(f"Ticket for seat {self.seat.row_and_number} cancelled.")
        self.seat.release()  
       
    def promotion(self, coupon=None):
        if coupon:
            
            cinema_name = None 
            movie_name = self.showtime.movie.name
            user_type = "student" if "student" in self.name.lower() else "regular"
            
            if coupon.can_apply(self.price, cinema_name, movie_name, user_type):
                new_price, discount = coupon.apply_discount(self.price)
                self.price = new_price
                print(f"Coupon '{coupon.code}' applied! Discount: R${discount:.2f}")
                coupon.use()
            else:
                print(f"Coupon '{coupon.code}' cannot be applied to this purchase.")
        
        return self.price

    def generate_qr_code(self):
        data = f"""
        Ticket for seat {self.seat.row_and_number}
        Movie: {self.showtime.movie.name}
        Time: {self.showtime.time}
        Room: {self.showtime.screen_number}
        """
        qr = qrcode.QRCode(box_size=2)
        qr.add_data(data)
        print("\n📲 Mobile Ticket With QR Code:")
        print("-"*40)
        print(data.strip())
        print("-"*40)
        qr.print_ascii(invert=True)
        print("-"*40)

class SEAT:
    def __init__(self, row_and_number):
        self.row_and_number = row_and_number
        self.is_reserved = False
        self.reservation_history = []
        self.reservation_expiry = None
    
    def reserver(self, user, minutes=0):  
        if not self.is_reserved:
            self.is_reserved = True
            reservation = {
                'user_id': user.id,
                'user_name': user.name,
                'time': datetime.now(),
                'action': 'reserved',
                'expires_at': (datetime.now() + timedelta(minutes=minutes)) if minutes > 0 else None
            }
            self.reservation_history.append(reservation)
            self.reservation_expiry = reservation['expires_at']
            print(f"Seat {self.row_and_number} reserved for {user.name}!")

            message = f"🪑 Seat {self.row_and_number} reserved successfully!"
            expiry_str = self.reservation_expiry.strftime("%H:%M:%S") if self.reservation_expiry else "Permanent"
            data = {"seat": self.row_and_number, "expires_at": expiry_str}
            notification_service.send_notification(user, SEAT_RESERVATION, message, data)
            return True
        return False

    def release(self, user=None): 
        if self.is_reserved:
            self.is_reserved = False
            user_id = user.id if user and hasattr(user, 'id') else 'system'
            user_name = user.name if user and hasattr(user, 'name') else 'System'
            
            self.reservation_history.append({
                'user_id': user_id,
                'user_name': user_name,
                'time': datetime.now(),
                'action': 'released'
            })
            print(f"Seat {self.row_and_number} reservation cancelled by {user_name}.")
            self.reservation_expiry = None
            return True
        return False
    
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

    def temp_reserve(self, user, minutes=15): 
        if not self.is_reserved:
            if self.reserver(user, minutes):
                print(f"Seat {self.row_and_number} reserved for {minutes} minutes.")
                return True
        else:
            print(f"Seat {self.row_and_number} is already reserved.")
            return False

    def check_expiry(self):
        if self.is_reserved and self.reservation_expiry:
            remaining_time = self.reservation_expiry - datetime.now()
            if remaining_time < timedelta(seconds=0):
                self.release()
                print(f" Seat Reservation {self.row_and_number} expired")
                return True 
            elif remaining_time < timedelta(minutes=5):
                print(f" Heads up! Reservation for seat {self.row_and_number} expires in {int(remaining_time.seconds/60)} minutes.")
        return False

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

# --- Serviços de Notificação e Promoção ---
notification_service = NotificationService()
promotion_manager = PromotionManager()

usuarios_registrados = {}
usuario_logado = None
cinemas = {}

def inicializar_dados():
    global cinemas, usuarios_registrados
    cinesystem = CINEMA("Cinesystem")
    filme1_cinesystem = MOVIE("Divergent", 139, "Action")
    filme2_cinesystem = MOVIE("Notting Hill", 124, "Romance")
    filme1_cinesystem.add_showtime("19:00", 1, [SEAT(f"A{i}") for i in range(1, 11)])
    filme2_cinesystem.add_showtime("16:00", 2, [SEAT(f"B{i}") for i in range(1, 11)])
    cinesystem.add_movie(filme1_cinesystem)
    cinesystem.add_movie(filme2_cinesystem)

    kinoplex = CINEMA("Kinoplex")
    filme1_kinoplex = MOVIE("The conjuring", 112, "Horror")
    filme2_kinoplex = MOVIE("Interestelar", 169, "Sci-Fi")
    filme1_kinoplex.add_showtime("20:00", 3, [SEAT(f"C{i}") for i in range(1, 11)])
    filme2_kinoplex.add_showtime("17:00", 4, [SEAT(f"D{i}") for i in range(1, 11)])
    kinoplex.add_movie(filme1_kinoplex)
    kinoplex.add_movie(filme2_kinoplex)
    
    centerplex = CINEMA("Centerplex")
    filme1_centerplex = MOVIE("Toy Story", 81, "Animation")
    filme1_centerplex.add_showtime("21:00", 5, [SEAT(f"E{i}") for i in range(1, 11)])
    centerplex.add_movie(filme1_centerplex)

    cinemas["Cinesystem"] = cinesystem
    cinemas["Kinoplex"] = kinoplex
    cinemas["Centerplex"] = centerplex
    
    usuarios_registrados["marcela"] = USER("Marcela", "marcela", "12345", "marcela@email.com")
    usuarios_registrados["admin"] = ADMIN("Admin", "admin", "admin123", "admin@cinema.com")
    usuarios_registrados["system"] = USER("System", "system", "system", "system@cinema.com")

def menu_principal():
    global usuario_logado
    print("\nWelcome to the Movie Ticketing System!")
    while True:
        print("\n--- Main Menu ---")
        if usuario_logado:
            print(f"Welcome, {usuario_logado.name}!")
            print("[1] Watch Movies")
            print("[2] My Reservations")
            print("[3] Notifications")
            print("[4] Review a Movie")
            print("[5] View Available Coupons")
            print("[6] Cancel a Purchase")
            if isinstance(usuario_logado, ADMIN):
                print("[7] Admin Panel")
            print("[0] Logout")
        else:
            print("[1] Login")
            print("[2] Exit")
        
        escolha = input("Select an option: ")

        if not usuario_logado:
            if escolha == "1":
                login()
            elif escolha == "2":
                print("Thank you for using the system!")
                sys.exit()
            else:
                print("Invalid option. Please try again.")
        else:
            if escolha == "1":
                ver_cinemas()
            elif escolha == "2":
                usuario_logado.view_booking_history()
            elif escolha == "3":
                menu_notifications()
            elif escolha == "4":
                avaliar_filme()
            elif escolha == "5":
                view_coupons()
            elif escolha == "6":
                cancelar_compra()
            elif escolha == "7" and isinstance(usuario_logado, ADMIN):
                admin_panel()
            elif escolha == "0":
                usuario_logado = None
                print("You have logged out of your account.")
            else:
                print("Invalid option. Please try again.")

def menu_notifications():
    while True:
        print("\n--- Notifications ---")
        print("[1] View All Notifications")
        print("[2] View Unread Notifications")
        print("[3] Mark Notification as Read")
        print("[0] Back to main menu")

        escolha = input("Select an option: ")

        if escolha == "1":
            usuario_logado.view_notifications()
        elif escolha == "2":
            usuario_logado.view_notifications(unread_only=True)
        elif escolha == "3":
            notifications = usuario_logado.view_notifications(unread_only=True)
            if notifications:
                try:
                    notif_choice = int(input("Enter the notification number to mark as read: "))
                    if 1 <= notif_choice <= len(notifications):
                        notification_id = notifications[notif_choice - 1]['id']
                        if notification_service.mark_as_read(notification_id):
                            print("Notification marked as read.")
                        else:
                            print("Could not find notification.")
                    else:
                        print("Invalid number.")
                except ValueError:
                    print("Invalid input.")
        elif escolha == "0":
            return
        else:
            print("Invalid option. Please try again.")

def view_coupons():
    active_coupons = promotion_manager.list_active_coupons()
    if not active_coupons:
        print("No active coupons.")
    else:
        print("\nActive Coupons:")
        for coupon in active_coupons:
            print(f"\n Code: {coupon.code}")
            print(f" Description: {coupon.description}")
            if coupon.type == PERCENTAGE:
                print(f" Type: Percentage | Discount: {coupon.value}%")
            elif coupon.type == FIXED_AMOUNT:
                print(f" Type: Fixed Amount | Discount: R$ {coupon.value:.2f}")
            if coupon.min_purchase > 0:
                print(f" Minimum purchase: R$ {coupon.min_purchase:.2f}")
            if coupon.max_uses:
                print(f" Max uses: {coupon.max_uses} (Used {coupon.uses_count} times)")
            if coupon.valid_until:
                print(f" Valid until: {coupon.valid_until.strftime('%Y-%m-%d %H:%M:%S')}")
            if coupon.applicable_cinemas:
                print(f" Applicable cinemas: {', '.join(coupon.applicable_cinemas)}")
            if coupon.applicable_movies:
                print(f" Applicable movies: {', '.join(coupon.applicable_movies)}")
            if coupon.user_type:
                print(f" User type: {coupon.user_type}")
            print("-" * 50)

def admin_panel():
    while True:
        print("\n ADMIN PANEL")
        print("[1] Add New Movie")
        print("[2] Add New Showtime")
        print("[3] Create New Coupon")
        print("[4] View System Reports")
        print("[5] Send Custom Notification")
        print("[0] Back to Main Menu")
        
        escolha = input("Select an option: ")
        
        if escolha == "1":
            add_movie_admin()
        elif escolha == "2":
            add_showtime_admin()
        elif escolha == "3":
            create_coupon_admin()
        elif escolha == "4":
            usuario_logado.view_reports()
        elif escolha == "5":
            send_custom_notification()
        elif escolha == "0":
            break
        else:
            print("Invalid option.")
            
def add_movie_admin():
    print("\n ADD NEW MOVIE")
    name = input("Movie name: ")
    duration = int(input("Duration (minutes): "))
    genre = input("Genre: ")
    
    print("\nSelect cinema:")
    for i, cinema_name in enumerate(cinemas.keys(), 1):
        print(f"[{i}] {cinema_name}")
    
    try:
        cinema_choice = int(input("Cinema number: ")) - 1
        cinema_name = list(cinemas.keys())[cinema_choice]
        cinema = cinemas[cinema_name]
        
        new_movie = MOVIE(name, duration, genre)
        usuario_logado.add_movie_to_cinema(cinema, new_movie)
        
    except (ValueError, IndexError):
        print("Invalid option.")

def add_showtime_admin():
    print("\n ADD NEW SHOWTIME")
    try:
        print("\nSelect cinema:")
        for i, cinema_name in enumerate(cinemas.keys(), 1):
            print(f"[{i}] {cinema_name}")
        cinema_choice = int(input("Cinema number: ")) - 1
        cinema_name = list(cinemas.keys())[cinema_choice]
        cinema = cinemas[cinema_name]

        if not cinema.movies:
            print(f"No movies in {cinema.name} to add a showtime to.")
            return

        print("\nSelect movie:")
        for i, movie in enumerate(cinema.movies, 1):
            print(f"[{i}] {movie.name}")
        movie_choice = int(input("Movie number: ")) - 1
        selected_movie = cinema.movies[movie_choice]
        
        showtime_time = input("Showtime time (HH:MM): ")
        screen_number = int(input("Screen number: "))
        num_seats = int(input("Number of seats for this showtime: "))
        
        seats = [SEAT(f"S{i}") for i in range(1, num_seats + 1)] # Generic seat names
        
        usuario_logado.add_showtime_to_movie(selected_movie, showtime_time, screen_number, seats)

    except (ValueError, IndexError):
        print("Invalid option.")

def create_coupon_admin():
    print("\nCREATE NEW COUPON")
    try:
        code = input("Coupon code: ")
        description = input("Coupon description: ")
        coupon_type = input("Coupon type (percentage/fixed_amount): ").lower()
        if coupon_type not in [PERCENTAGE, FIXED_AMOUNT]:
            print("Invalid type.")
            return
        
        value = float(input("Discount value (e.g., 10 for 10% or 10.0 for R$10): "))
        
        kwargs = {}
        min_purchase = float(input("Minimum purchase amount (0 for none): "))
        if min_purchase > 0:
            kwargs['min_purchase'] = min_purchase
            
        max_uses = int(input("Maximum uses (0 for unlimited): "))
        if max_uses > 0:
            kwargs['max_uses'] = max_uses
            
        valid_until_str = input("Valid until (YYYY-MM-DD HH:MM) or leave blank: ")
        if valid_until_str:
            kwargs['valid_until'] = datetime.strptime(valid_until_str, '%Y-%m-%d %H:%M')
            
        applicable_movies_str = input("Applicable movies (comma-separated names, or leave blank): ")
        if applicable_movies_str:
            kwargs['applicable_movies'] = [name.strip() for name in applicable_movies_str.split(',')]
            
        user_type = input("Applicable user type (student/regular) or leave blank: ")
        if user_type:
            kwargs['user_type'] = user_type

        usuario_logado.create_coupon(code, coupon_type, value, description, **kwargs)
    except ValueError:
        print("Invalid input. Please check the format of your entries.")

def send_custom_notification():
    print("\nSEND CUSTOM NOTIFICATION")
    message = input("Enter the notification message to send to all users: ")
    if not message:
        print("Message cannot be empty.")
        return

    for user in usuarios_registrados.values():
        if user.user_type != "admin":
            notification_service.send_notification(user, "custom_message", message)
    print("Custom notifications sent to all users.")

def login():
    global usuario_logado
    resposta = input("\nAre you already registered? \n[1] Yes\n[2] No\n ")
    
    if resposta == "1":
        processar_login()
    elif resposta == "2":
        registrar()
    else:
        print("Invalid option.")

def processar_login():
    global usuario_logado
    login_user = input("Login: ")
    password_user = input("Password: ")
    
    if login_user in usuarios_registrados and usuarios_registrados[login_user].password == password_user:
        usuario_logado = usuarios_registrados[login_user]
        print(f"Login successful! Welcome, {usuario_logado.name}.")
    else:
        print("Incorrect login or password.")

def registrar():
    name = input("Name: ")
    login_user = input("Login: ")
    print("The password must be a string and have at least 5 characters.")
    password_user = input("Password: ")
    
    if login_user in usuarios_registrados:
        print("This login already exists. Please try another one.")
    elif len(password_user) < 5:
         print("The password must be a string and have at least 5 characters.")
    else:
        usuarios_registrados[login_user] = USER(name, login_user, password_user)
        print("User successfully registered!")

def ver_cinemas():
    print("\n--- Choose a Cinema ---")
    cinema_keys = list(cinemas.keys())
    for i, cinema_nome in enumerate(cinema_keys, 1):
        print(f"[{i}] {cinema_nome}")
    print("[0] Back to main menu")
    
    while True:
        escolha = input("Enter the theater number: \n")
        if escolha == '0':
            return
        try:
            cinema_nome = cinema_keys[int(escolha) - 1]
            ver_filmes(cinemas[cinema_nome])
            break
        except (ValueError, IndexError):
            print("Invalid option.")
            
def ver_filmes(cinema_obj):
    cinema_obj.list_movies()
        
    escolha_filme = input("Enter the name of the movie you want to buy tickets for (or 'exit' to go back): ")
    if escolha_filme.lower() == 'exit':
        return
    
    filme_selecionado = next((m for m in cinema_obj.movies if m.name.lower() == escolha_filme.lower()), None)
    if not filme_selecionado:
        print("Movie not found. Please try again.")
        return
        
    comprar_ingresso(filme_selecionado)

def payment(valor):
    print(f"\n--- Payment Process of R${valor:.2f} ---")
    while True:
        forma_de_pagamento = input("Choose a payment method: \n[1] Credit Card\n[2] Debit Card\n[3] Pix\n[4] Cancel\n") 

        if forma_de_pagamento == "1":
            numero = input("Number of credit card(16 digits):").strip()
            if len(numero) == 16 and numero.isdigit():
                print(f"Payment made with Credit Card of R${valor:.2f}.")
                return True
            else:
                print("Invalid credit card number. Please try again.")
        elif forma_de_pagamento == "2":
            numero = input("Number of debit card(16 digits): ").strip()
            if len(numero) == 16 and numero.isdigit():
                print(f"Payment made with Debit Card of R${valor:.2f}.")
                return True
            else:
                print("Invalid debit card number. Please try again.")
        elif forma_de_pagamento == "3":
            print("Pix Key: cinemaenterprises.com")
            print(f"Value: R${valor:.2f}")
            print(f"Payment made with Pix of R${valor:.2f} Successfully completed.")
            return True
        elif forma_de_pagamento == "4":
            print("Payment canceled.")
            return False
        else:
            print("Invalid option. Please try again.")

def comprar_ingresso(movie):
    print(f"\n--- Buy Ticket for '{movie.name}' ---")
    movie.list_showtimes()
    
    escolha_horario = input("Enter the session time (ex: 19:00): ")
    showtime_selecionado = next((s for s in movie.showtimes if s.time == escolha_horario), None)
    
    if not showtime_selecionado:
        print("Invalid time. Please try again.")
        return
        
    print(f"\nSelected time: {showtime_selecionado.time} | Room: {showtime_selecionado.screen_number}")
    showtime_selecionado.list_available_seats()
    
    assento_selecionado = None
    while True:
        escolha_assento = input("Enter the number of the seat you want (ex: A5): ").upper()
        assento_selecionado = next((s for s in showtime_selecionado.seats if s.row_and_number.upper() == escolha_assento), None)
        
        if not assento_selecionado:
            print("Invalid seat. Please try again.")
            continue
            
        if assento_selecionado.is_reserved:
            print("Seat already reserved. History:")
            assento_selecionado.get_history()
            continue
            
        if assento_selecionado.temp_reserve(usuario_logado, minutes=10):
            break
        else:
            print("Could not reserve seat. Please try another one.")
    
    tipo_ingresso = input("Enter the ticket type (Standard, Student): ").capitalize()
    preco = 25.0
    
    ticket = TICKET(tipo_ingresso, preco, assento_selecionado, showtime_selecionado)
    
    coupon_code = input("Do you have a coupon code? (Enter code or leave blank): ")
    if coupon_code:
        coupon = promotion_manager.get_coupon(coupon_code)
        if coupon:
            ticket.promotion(coupon)
        else:
            print("Invalid coupon code.")

    print(f"\nPurchase Summary:")
    print(f" Movie: {movie.name}")
    print(f" Session: {showtime_selecionado.time} - Room {showtime_selecionado.screen_number}")
    print(f" Seat: {assento_selecionado.row_and_number}")
    print(f" Ticket Price: R$ {ticket.price:.2f}")

    total_price = ticket.price
    popcorn_item = None

    escolha_combo = input("\nWould you like to add a popcorn combo? \n[1] Yes\n[2] No\n ")
    if escolha_combo == "1":
        while True:
            combo_size = input("Popcorn size (S, M, L): ").upper()
            if combo_size in ["S", "M", "L"]:
                break
            else:
                print("Invalid size. Please try again.")
        popcorn_item = POPCORN("Popcorn", 0.0, combo_size)
        popcorn_item.purchase_product()
        print(f"Combo of {popcorn_item.name} ({popcorn_item.size}) added. Price: R$ {popcorn_item.price:.2f}")
        total_price += popcorn_item.price
        print(f"New Total price: R$ {total_price:.2f}")

    pagar = input(f"Total price: R$ {total_price:.2f}. Do you wish to proceed with the payment? \n[1] Yes\n[2] No\n ")
    if pagar == "1":
        if not assento_selecionado.check_expiry():
            if payment(total_price):
                assento_selecionado.reservation_expiry = None 
                ticket.purchase_product()
                usuario_logado.add_booking(ticket)
                movie.total_tickets_sold += 1
                movie.total_revenue += total_price
                ticket.generate_qr_code()
            else:
                print("Payment failed. Releasing seat.")
                assento_selecionado.release(usuario_logado)
        else:
            print("Your temporary reservation has expired. Please start over.")   
    else:
        print("Purchase canceled.")
        assento_selecionado.release(usuario_logado)

def avaliar_filme():
    print("\n--- Choose a Cinema to Rate a Movie ---")
    cinema_keys = list(cinemas.keys())
    for i, cinema_nome in enumerate(cinema_keys, 1):
        print(f"[{i}]. {cinema_nome}")
    print("[0]. Back to main menu")

    while True:
        escolha = input("Enter the theater number: ")
        if escolha == '0':
            return
        try:
            cinema_nome = cinema_keys[int(escolha) - 1]
            cinema_obj = cinemas[cinema_nome]
            
            print(f"\n--- Movies available on {cinema_obj.name} ---")
            for i, movie in enumerate(cinema_obj.movies, 1):
                print(f"[{i}]. {movie.name}")
            
            escolha_filme = input("Enter the number of the movie you want to rate: ")
            movie_to_review = cinema_obj.movies[int(escolha_filme) - 1]

            rating = int(input("Your rating (1 a 5): "))
            if rating < 1 or rating > 5:
                raise ValueError
            comment = input("Your comment: ")
            
            movie_to_review.add_review(rating, comment)
            print("Review successfully submitted!")
            return

        except (ValueError, IndexError):
            print("Invalid option. Please try again.")

def cancelar_compra():
    if not usuario_logado.booking_history:
        print("You have no bookings to cancel.")
        return
    
    usuario_logado.view_booking_history()
    
    escolha = input("Enter the number of the booking you want to cancel (or '0' to go back): ")
    if escolha == '0':
        return
    
    try:
        index = int(escolha) - 1
        if 0 <= index < len(usuario_logado.booking_history):
            ticket_to_cancel = usuario_logado.booking_history[index]
            ticket_to_cancel.cancel_purchase()
            usuario_logado.remove_booking(ticket_to_cancel)
            print("Booking cancelled successfully!")
        else:
            print("Invalid number.")
    except (ValueError, IndexError):
        print("Invalid option. Please try again.")

# --- Programa Principal---
if __name__ == "__main__":
    inicializar_dados()
    menu_principal()