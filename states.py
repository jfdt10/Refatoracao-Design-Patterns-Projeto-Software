from abc import ABC, abstractmethod
from datetime import datetime, timedelta


class SeatState(ABC):
    
    @abstractmethod
    def reserve(self, seat, user, minutes=0):
        pass
    
    @abstractmethod
    def release(self, seat, user=None):
        pass
    
    @abstractmethod
    def confirm(self, seat):
        pass
    
    @abstractmethod
    def check_expiry(self, seat):
        pass
    
    @abstractmethod
    def get_status(self):
        pass


class AvailableState(SeatState):
    
    def reserve(self, seat, user, minutes=0):
        from events import event_bus
        
        reservation = {
            'user_id': user.id,
            'user_name': user.name,
            'time': datetime.now(),
            'action': 'reserved',
            'expires_at': (datetime.now() + timedelta(minutes=minutes)) if minutes > 0 else None
        }
        seat.reservation_history.append(reservation)
        seat.reservation_expiry = reservation['expires_at']
        
        print(f"✅ Seat {seat.row_and_number} reserved for {user.name}!")
        
        if minutes > 0:
            seat.state = TemporaryReservedState()
        else:
            seat.state = ConfirmedState()
        
        expiry_str = seat.reservation_expiry.strftime("%H:%M:%S") if seat.reservation_expiry else "Permanent"
        event_bus.publish("seat_reserved", {
            "user": user,
            "seat": seat.row_and_number,
            "expires_at": expiry_str
        })
        return True
    
    def release(self, seat, user=None):
        print("Seat is already available.")
        return False
    
    def confirm(self, seat):
        print("Cannot confirm an available seat.")
        return False
    
    def check_expiry(self, seat):
        return False  
    
    def get_status(self):
        return "Available"


class TemporaryReservedState(SeatState):
    
    def reserve(self, seat, user, minutes=0):
        print("Seat is already reserved.")
        return False
    
    def release(self, seat, user=None):
        from events import event_bus
        
        user_id = user.id if user and hasattr(user, 'id') else 'system'
        user_name = user.name if user and hasattr(user, 'name') else 'System'
        
        seat.reservation_history.append({
            'user_id': user_id,
            'user_name': user_name,
            'time': datetime.now(),
            'action': 'released'
        })
        seat.reservation_expiry = None

        print(f"Seat {seat.row_and_number} reservation cancelled by {user_name}.")

        # Transição de estado
        seat.state = AvailableState()
        
        # Publicar evento
        event_bus.publish("seat_released", {
            "user": user,
            "seat": seat.row_and_number
        })
        return True
    
    def confirm(self, seat):
        print(f"Seat {seat.row_and_number} confirmed!")
        seat.reservation_expiry = None
        seat.state = ConfirmedState()
        return True
    
    def check_expiry(self, seat):
        if seat.reservation_expiry and datetime.now() >= seat.reservation_expiry:
            print(f"⏰ Reservation for seat {seat.row_and_number} expired. Releasing...")
            self.release(seat)
            return True
        return False
    
    def get_status(self):
        return "Temporarily Reserved"


class ConfirmedState(SeatState):
    
    def reserve(self, seat, user, minutes=0):
        print(" Seat is already confirmed.")
        return False
    
    def release(self, seat, user=None):
        from events import event_bus
        
        user_id = user.id if user and hasattr(user, 'id') else 'system'
        user_name = user.name if user and hasattr(user, 'name') else 'System'
        
        seat.reservation_history.append({
            'user_id': user_id,
            'user_name': user_name,
            'time': datetime.now(),
            'action': 'released'
        })
        
        print(f"Confirmed seat {seat.row_and_number} released by {user_name}.")
        
        seat.state = AvailableState()
        
        event_bus.publish("seat_released", {
            "user": user,
            "seat": seat.row_and_number
        })
        return True
    
    def confirm(self, seat):
        print("Seat is already confirmed.")
        return False
    
    def check_expiry(self, seat):
        return False  
    
    def get_status(self):
        return "Confirmed"