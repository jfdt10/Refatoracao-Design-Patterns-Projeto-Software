import uuid
from datetime import datetime, timedelta
from utils import MetaSingleton, PERCENTAGE, FIXED_AMOUNT
from adapter import EmailNotificationAdapter, SMSNotificationAdapter, PushNotificationAdapter
from exceptions import (
    InvalidCouponException,
    CouponExpiredException,
    CouponUsageLimitException,
    MinimumPurchaseException,
    NotificationDeliveryException,
    InvalidNotificationChannelException
)

class MultiChannelNotificationService(metaclass=MetaSingleton):
    def __init__(self):
        self.channels = {
            "email": EmailNotificationAdapter(),
            "sms": SMSNotificationAdapter(),
            "push": PushNotificationAdapter(),
            "app": None
        }
        self.notifications = []

    def register_channel(self, channel_name, channel_instance):
        self.channels[channel_name] = channel_instance

    def send_notification(self, user, notification_type, message, data=None, channels=None):
        if not channels:
            channels = ["app"]

        notification = {
            'id': str(uuid.uuid4()),
            'user_id': user.id,
            'user_name': user.name,
            'user_email': user.email,
            'type': notification_type,
            'message': message,
            'data': data or {},
            'timestamp': datetime.now(),
            'read': False,
            'channels_sent': []
        }

        failed_channels = []
        for channel_name in channels:
            if channel_name not in self.channels:
                raise InvalidNotificationChannelException(
                    channel_name, 
                    list(self.channels.keys())
                )
            
            if self.channels[channel_name]:
                try:
                    channel = self.channels[channel_name]
                    result = channel.send(user, notification_type, message, data)
                    notification['channels_sent'].append({
                        'channel': channel_name,
                        'status': result.get('status', 'unknown'),
                        'timestamp': datetime.now()
                    })
                except (AttributeError, KeyError, TypeError) as e:
                    failed_channels.append(channel_name)
                    notification['channels_sent'].append({
                        'channel': channel_name,
                        'status': 'failed',
                        'error': str(e),
                        'timestamp': datetime.now()
                    })

        if failed_channels and len(failed_channels) == len(channels):
            raise NotificationDeliveryException(
                ", ".join(failed_channels),
                "Falha em todos os canais de notificação"
            )

        self.notifications.append(notification)
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

    def get_channel_statistics(self):
        stats = {}
        for channel_name, channel in self.channels.items():
            if channel and hasattr(channel, 'sent_messages'):
                stats[channel_name] = len(channel.sent_messages)
            else:
                stats[channel_name] = 0
        return stats

# Classe Wrapper do Serviço de Notificação Multi-Canal
class NotificationService(metaclass=MetaSingleton):
    def __init__(self):
        self.notifications = []

    def send(self, user, notification_type, message, data=None):
        return {
            'status': 'stored',
            'timestamp': datetime.now()
        }

    def send_notification(self, user, notification_type, message, data=None, channels=None):
        return multi_channel_service.send_notification(user, notification_type, message, data, channels or ["app"])

    def get_user_notifications(self, user_id, unread_only=False):
        return multi_channel_service.get_user_notifications(user_id, unread_only)

    def mark_as_read(self, notification_id):
        return multi_channel_service.mark_as_read(notification_id)

class Coupon:
    def __init__(self, code, coupon_type, value, description, valid_until=None,
             min_purchase=0, max_uses=None, applicable_cinemas=None,
             applicable_movies=None, user_type=None, applicable_ticket_types=None):
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
        self.applicable_ticket_types = applicable_ticket_types or []

    def is_valid(self, raise_exception=False):
        if not self.is_active:
            if raise_exception:
                raise InvalidCouponException(self.code, "Cupom está inativo")
            return False
        
        if self.valid_until and datetime.now() > self.valid_until:
            if raise_exception:
                raise CouponExpiredException(self.code, self.valid_until)
            return False
        
        if self.max_uses and self.uses_count >= self.max_uses:
            if raise_exception:
                raise CouponUsageLimitException(self.code, self.max_uses)
            return False
        
        return True

    def can_apply(self, total_amount, ticket_type=None, cinema_name=None, movie_name=None, user_type=None, raise_exception=False):
       
        if not self.is_valid(raise_exception=raise_exception):
            return False
        
        if total_amount < self.min_purchase:
            if raise_exception:
                raise MinimumPurchaseException(self.code, self.min_purchase, total_amount)
            return False
        
        if hasattr(self, 'applicable_ticket_types') and self.applicable_ticket_types and ticket_type not in self.applicable_ticket_types:
            if raise_exception:
                raise InvalidCouponException(
                    self.code, 
                    f"Cupom não aplicável ao tipo de ingresso '{ticket_type}'"
                )
            return False
        
        if self.applicable_cinemas and cinema_name not in self.applicable_cinemas:
            if raise_exception:
                raise InvalidCouponException(
                    self.code,
                    f"Cupom não aplicável ao cinema '{cinema_name}'"
                )
            return False
        
        if self.applicable_movies and movie_name not in self.applicable_movies:
            if raise_exception:
                raise InvalidCouponException(
                    self.code,
                    f"Cupom não aplicável ao filme '{movie_name}'"
                )
            return False
        
        if self.user_type and user_type != self.user_type:
            if raise_exception:
                raise InvalidCouponException(
                    self.code,
                    f"Cupom exclusivo para usuários do tipo '{self.user_type}'"
                )
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

class PromotionManager(metaclass=MetaSingleton):
    def __init__(self):
        if not hasattr(self, 'coupons'):
            self.coupons = {}
            self.initialize_default_coupons()

    def initialize_default_coupons(self):
        self.add_coupon(Coupon("STUDENT50", PERCENTAGE, 50,
                       "50% off for student tickets",
                       applicable_ticket_types=["student"]))
        self.add_coupon(Coupon("WELCOME10", FIXED_AMOUNT, 10,
                               "R$10 off for new users", min_purchase=20, max_uses=1))
        self.add_coupon(Coupon("CINEMA20", PERCENTAGE, 20,
                               "20% off on all tickets",
                               valid_until=datetime.now() + timedelta(days=30)))
        self.add_coupon(Coupon("MOVIE15", FIXED_AMOUNT, 15,
                               "R$15 off on selected movies",
                               applicable_movies=["Toy Story", "Interstellar"], min_purchase=30))

    def add_coupon(self, coupon):
        self.coupons[coupon.code] = coupon

    def get_coupon(self, code):
        return self.coupons.get(code.upper())

    def list_active_coupons(self):
        return [c for c in self.coupons.values() if c.is_valid()]

# --- Instâncias Globais dos Serviços ---
multi_channel_service = MultiChannelNotificationService()
notification_service = NotificationService()
multi_channel_service.register_channel("app", notification_service)
promotion_manager = PromotionManager()
