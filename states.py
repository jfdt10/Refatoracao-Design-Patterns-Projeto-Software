from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from observer import event_bus
from utils import SEAT_RESERVED, SEAT_RELEASED, SEAT_CONFIRMED 

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
        
        reservation = {
            'user_id': user.id,
            'user_name': user.name,
            'time': datetime.now(),
            'action': 'reserved',
            'expires_at': (datetime.now() + timedelta(minutes=minutes)) if minutes > 0 else None
        }
        seat.reservation_history.append(reservation)
        seat.reservation_expiry = reservation['expires_at']
        
        # transição de estado baseada em minutes
        if minutes > 0:
            seat.state = TemporaryReservedState()
        else:
            seat.state = ConfirmedState()
        
        expiry_str = seat.reservation_expiry.strftime("%H:%M:%S") if seat.reservation_expiry else "Permanent"
        event_bus.publish(SEAT_RESERVED, {
            "user": user,
            "seat": seat.row_and_number,
            "expires_at": expiry_str
        })
        return True
    
    def release(self, seat, user=None):
        # já disponível -> nada a fazer
        return False
    
    def confirm(self, seat):
        # não é possível confirmar um assento disponível sem reserva
        return False
    
    def check_expiry(self, seat):
        return False  
    
    def get_status(self):
        return "Available"


class TemporaryReservedState(SeatState):
    
    def reserve(self, seat, user, minutes=0):
        # já reservado temporariamente
        return False
    
    def release(self, seat, user=None):
        
        user_id = user.id if user and hasattr(user, 'id') else 'system'
        user_name = user.name if user and hasattr(user, 'name') else 'System'
        
        seat.reservation_history.append({
            'user_id': user_id,
            'user_name': user_name,
            'time': datetime.now(),
            'action': 'released'
        })
        seat.reservation_expiry = None

        # Transição de estado
        seat.state = AvailableState()
        
        # Publicar evento para UI/handlers
        event_bus.publish(SEAT_RELEASED, {
            "user": user,
            "seat": seat.row_and_number
        })
        return True
    
    def confirm(self, seat):
        # confirmar reserva temporária
        seat.reservation_expiry = None
        seat.state = ConfirmedState()
        event_bus.publish(SEAT_CONFIRMED, {
            "seat": seat.row_and_number
        })
        return True
    
    def check_expiry(self, seat):
        if seat.reservation_expiry and datetime.now() >= seat.reservation_expiry:
            # quando expirar, liberar e publicar evento via release()
            self.release(seat)
            return True
        return False
    
    def get_status(self):
        return "Temporarily Reserved"


class ConfirmedState(SeatState):
    
    def reserve(self, seat, user, minutes=0):
        # assento já confirmado
        return False
    
    def release(self, seat, user=None):
        
        user_id = user.id if user and hasattr(user, 'id') else 'system'
        user_name = user.name if user and hasattr(user, 'name') else 'System'
        
        seat.reservation_history.append({
            'user_id': user_id,
            'user_name': user_name,
            'time': datetime.now(),
            'action': 'released'
        })
        
        seat.state = AvailableState()

        event_bus.publish(SEAT_RELEASED, {
            "user": user,
            "seat": seat.row_and_number
        })
        return True
    
    def confirm(self, seat):
        # já confirmado
        return False
    
    def check_expiry(self, seat):
        return False  
    
    def get_status(self):
        return "Confirmed"