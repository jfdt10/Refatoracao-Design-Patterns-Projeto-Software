from abc import ABC, abstractmethod
import threading


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
        
        if event == "seat_reserved":
            seat = payload.get("seat", "")
            expires = payload.get("expires_at", "")
            message = f"🪑 Assento {seat} reservado com sucesso!"
            data = {"seat": seat, "expires_at": expires}
            self.notification_service.send_notification(user, "seat_reservation", message, data)
        
        elif event == "seat_released":
            seat = payload.get("seat", "")
            message = f"Reserva do assento {seat} cancelada."
            self.notification_service.send_notification(user, "seat_released", message, {"seat": seat})
        
        elif event == "payment_success":
            amount = payload.get("amount", 0)
            message = f"Pagamento confirmado: R$ {amount:.2f}"
            self.notification_service.send_notification(user, "payment_success", message, payload)
        
        elif event == "booking_confirmed":
            movie = payload.get("movie", "")
            time = payload.get("time", "")
            seat = payload.get("seat", "")
            message = f"Reserva confirmada: '{movie}' às {time} (Assento {seat})"
            self.notification_service.send_notification(user, "booking_confirmed", message, payload)
        
        elif event == "new_movie":
            movie_name = payload.get("movie_name", "")
            cinema_name = payload.get("cinema_name", "")
            message = f"Novo filme disponível: '{movie_name}' no {cinema_name}!"
            self.notification_service.send_notification(user, "new_movie", message, payload)
        
        elif event == "new_showtime":
            movie_name = payload.get("movie_name", "")
            time = payload.get("time", "")
            message = f"Nova sessão disponível: '{movie_name}' às {time}!"
            self.notification_service.send_notification(user, "new_showtime", message, payload)
        
        elif event == "discount_coupon":
            coupon_code = payload.get("coupon_code", "")
            description = payload.get("description", "")
            message = f"Novo cupom disponível: {coupon_code} - {description}"
            self.notification_service.send_notification(user, "discount_coupon", message, payload)

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
        
        if event == "seat_reserved":
            self.metrics["seats_reserved"] += 1
            print(f"[Analytics] Total assentos reservados: {self.metrics['seats_reserved']}")
        
        elif event == "seat_released":
            self.metrics["seats_released"] += 1
            print(f"[Analytics] Total assentos liberados: {self.metrics['seats_released']}")
        
        elif event == "payment_success":
            self.metrics["payments_completed"] += 1
            amount = payload.get("amount", 0)
            self.metrics["total_revenue"] += amount
            print(f"[Analytics] Pagamentos: {self.metrics['payments_completed']} | Receita total: R$ {self.metrics['total_revenue']:.2f}")
        
        elif event == "booking_confirmed":
            self.metrics["bookings_confirmed"] += 1
            print(f"[Analytics] Total reservas confirmadas: {self.metrics['bookings_confirmed']}")
        
        elif event == "new_movie":
            self.metrics["movies_added"] += 1
            print(f"[Analytics] Total filmes adicionados: {self.metrics['movies_added']}")
        
        elif event == "new_showtime":
            self.metrics["showtimes_added"] += 1
            print(f"[Analytics] Total sessões criadas: {self.metrics['showtimes_added']}")
        
        elif event == "discount_coupon":
            self.metrics["coupons_created"] += 1
            print(f"[Analytics] Total cupons criados: {self.metrics['coupons_created']}")
    
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

event_bus = EventBus()
analytics_observer = AnalyticsObserver()

