from abc import ABC, abstractmethod
import threading
from utils import SEAT_RESERVED, SEAT_RELEASED, PAYMENT_SUCCESS, BOOKING_CONFIRMED, NEW_MOVIE, NEW_SHOWTIME, DISCOUNT_COUPON, CUSTOM_NOTIFICATION
from services import multi_channel_service

class Observer(ABC):
    
    @abstractmethod
    def update(self, subject, event, payload=None):
        pass


class Subject(ABC):
    
    @abstractmethod
    def attach(self, observer): 
        pass
    
    @abstractmethod
    def detach(self, observer):
        pass
    
    @abstractmethod
    def notify(self, event, payload=None):
        pass


class EventBus(Subject):
    
    def __init__(self):
        self._lock = threading.Lock()
        self._listeners = {} 
        self._wildcard = []  
    
    def attach(self, observer, events=None):
       
        with self._lock:
            if events is None:
                if observer not in self._wildcard:
                    self._wildcard.append(observer)
                return
            
            for event in events:
                if event not in self._listeners:
                    self._listeners[event] = []
                if observer not in self._listeners[event]:
                    self._listeners[event].append(observer)
    
    def detach(self, observer, events=None):
        with self._lock:
            if events is None:
                if observer in self._wildcard:
                    self._wildcard.remove(observer)
                for listeners in self._listeners.values():
                    if observer in listeners:
                        listeners.remove(observer)
                return
            
            for event in events:
                if event in self._listeners and observer in self._listeners[event]:
                    self._listeners[event].remove(observer)
    
    def notify(self, event, payload=None):
        with self._lock:
            specific = list(self._listeners.get(event, []))
            wildcard = list(self._wildcard)
        
        subscribers = specific + wildcard
        for obs in subscribers:
            try:
                obs.update(self, event, payload)
            except Exception as e:
                print(f"[EventBus] Erro no observer para '{event}': {e}")
    
    def publish(self, event, payload=None):
        self.notify(event, payload)


class NotificationObserver(Observer):
    
    def __init__(self, notification_service):
        self.notification_service = notification_service
    
    def update(self, subject, event, payload=None):
        if not isinstance(payload, dict):
            return
        
        user = payload.get("user")
        
        if user is None:
            targets = payload.get("targets", [])
            for target_user in targets:
                self._send_notification(event, target_user, payload)
            return
        
        self._send_notification(event, user, payload)
    
    def _send_notification(self, event, user, payload):
        channels = payload.get("channels", ["app"])
        
        if event == SEAT_RESERVED:
            seat = payload.get("seat", "")
            expires = payload.get("expires_at", "")
            message = f"🪑 Assento {seat} reservado com sucesso!"
            data = {"seat": seat, "expires_at": expires}
            self.notification_service.send_notification(user, "seat_reservation", message, data)
        
        elif event == SEAT_RELEASED:
            seat = payload.get("seat", "")
            message = f"Reserva do assento {seat} cancelada."
            self.notification_service.send_notification(user, "seat_released", message, {"seat": seat})
        
        elif event == PAYMENT_SUCCESS:
            amount = payload.get("amount", 0)
            movie = payload.get("movie", "")
            time = payload.get("time", "")
            seat = payload.get("seat", "")
            message = f"Pagamento confirmado: R$ {amount:.2f}"
            data = {"amount": amount, "movie": movie, "time": time, "seat": seat}
            self.notification_service.send_notification(user, "payment_success", message, data)
        
        elif event == BOOKING_CONFIRMED:
            movie = payload.get("movie", "")
            time = payload.get("time", "")
            seat = payload.get("seat", "")
            message = f"Reserva confirmada: '{movie}' às {time} (Assento {seat})"
            data = {"movie": movie, "time": time, "seat": seat}
            self.notification_service.send_notification(user, "booking_confirmed", message, data)
        
        elif event == NEW_MOVIE:
            movie_name = payload.get("movie_name", "")
            cinema_name = payload.get("cinema_name", "")
            genre = payload.get("genre", "")
            message = f"Novo filme disponível: '{movie_name}' no {cinema_name}!"
            data = {"movie_name": movie_name, "cinema_name": cinema_name, "genre": genre}
            self.notification_service.send_notification(user, "new_movie", message, data, channels=channels)
        
        elif event == NEW_SHOWTIME:
            movie_name = payload.get("movie_name", "")
            time = payload.get("time", "")
            message = f"Nova sessão disponível: '{movie_name}' às {time}!"
            data = {"movie_name": movie_name, "time": time}
            self.notification_service.send_notification(user, "new_showtime", message, data, channels=channels)
        
        elif event == DISCOUNT_COUPON:
            coupon_code = payload.get("coupon_code", "")
            description = payload.get("description", "")
            message = f"Novo cupom disponível: {coupon_code} - {description}"
            data = {"coupon_code": coupon_code, "description": description}
            self.notification_service.send_notification(user, "discount_coupon", message, data)
        
        elif event == CUSTOM_NOTIFICATION:
            message = payload.get("message", "")
            data = {"message": message}
            self.notification_service.send_notification(user, "custom_notification", message, data, channels=channels)
class AnalyticsObserver(Observer):
    
    def __init__(self):
        self.metrics = {
            "seats_reserved": 0,
            "seats_released": 0,
            "payments_completed": 0,
            "bookings_confirmed": 0,
            "total_revenue": 0.0,
            "movies_added": 0,
            "showtimes_added": 0,
            "coupons_created": 0
        }
    
    def update(self, subject, event, payload=None):
        if not isinstance(payload, dict):
            return
        
        if event == SEAT_RESERVED:
            self.metrics["seats_reserved"] += 1

        elif event == SEAT_RELEASED:
            self.metrics["seats_released"] += 1
        
        elif event == PAYMENT_SUCCESS:
            self.metrics["payments_completed"] += 1
            amount = payload.get("amount", 0)
            self.metrics["total_revenue"] += amount
        
        elif event == BOOKING_CONFIRMED:
            self.metrics["bookings_confirmed"] += 1
        
        elif event == NEW_MOVIE:
            self.metrics["movies_added"] += 1
        
        elif event == NEW_SHOWTIME:
            self.metrics["showtimes_added"] += 1
        
        elif event == DISCOUNT_COUPON:
            self.metrics["coupons_created"] += 1
    
    def get_report(self):
        return f"""
=== RELATÓRIO DE ANALYTICS ===
Assentos Reservados: {self.metrics['seats_reserved']}
Assentos Liberados: {self.metrics['seats_released']}
Pagamentos Completados: {self.metrics['payments_completed']}
Reservas Confirmadas: {self.metrics['bookings_confirmed']}
Receita Total: R$ {self.metrics['total_revenue']:.2f}
Filmes Adicionados: {self.metrics['movies_added']}
Sessões Criadas: {self.metrics['showtimes_added']}
Cupons Criados: {self.metrics['coupons_created']}
==============================
"""

# Instanciação do EventBus e Observers Globais
event_bus = EventBus()
analytics_observer = AnalyticsObserver()

# Instanciação e Registro dos Observers
notification_observer = NotificationObserver(multi_channel_service)
event_bus.attach(notification_observer)
event_bus.attach(analytics_observer)

