import threading

# --- Constantes de Notificação ---
BOOKING_CONFIRMED = "booking_confirmed"
NEW_MOVIE = "new_movie"
NEW_SHOWTIME = "new_showtime"
DISCOUNT_COUPON = "discount_coupon"
SEAT_RESERVATION = "seat_reservation"
PAYMENT_SUCCESS = "payment_success"
CUSTOM_MESSAGE = "custom_message"

# --- Constantes de Cupom ---
PERCENTAGE = "percentage"
FIXED_AMOUNT = "fixed_amount"

# --- Tipos de Ingresso ---
TICKET_STANDARD = "Standard"
TICKET_STUDENT = "Student"
TICKET_VIP = "VIP"

# --- Tipos de Usuário ---
USER_REGULAR = "regular"
USER_ADMIN = "admin"
USER_STUDENT = "student"
USER_VIP = "vip"

#------ Singleton via Metaclass -----
class MetaSingleton(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


