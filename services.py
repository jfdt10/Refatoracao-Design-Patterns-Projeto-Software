import uuid
from datetime import datetime, timedelta
from utils import MetaSingleton, PERCENTAGE, FIXED_AMOUNT
from events import event_bus, NotificationObserver, analytics_observer

class NotificationService(metaclass=MetaSingleton):
    def __init__(self):
        self.notifications = []
        notification_observer = NotificationObserver(self)
        event_bus.attach(notification_observer)
        event_bus.attach(analytics_observer)
        print("Observers registrados com sucesso!")
    
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
#------ Singleton via Metaclass -----
class PromotionManager(metaclass=MetaSingleton):
    def __init__(self):
        if not hasattr(self, 'coupons'):
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
# --- Instâncias Globais dos Serviços ---
notification_service = NotificationService()
promotion_manager = PromotionManager()