from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from observer import event_bus
from utils import SEAT_RESERVED, SEAT_RELEASED, SEAT_CONFIRMED
from exceptions import (
    SeatAlreadyReservedException,
    ReservationExpiredException,
    SeatNotAvailableException
) 

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
        return False
    
    def confirm(self, seat):
        raise SeatNotAvailableException(seat.row_and_number, "confirm")
    
    def check_expiry(self, seat):
        return False  
    
    def get_status(self):
        return "Available"


class TemporaryReservedState(SeatState):
    
    def reserve(self, seat, user, minutes=0):
        raise SeatAlreadyReservedException(
            seat.row_and_number,
            "Temporarily Reserved"
        )
    
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

        seat.state = AvailableState()
        
        event_bus.publish(SEAT_RELEASED, {
            "user": user,
            "seat": seat.row_and_number
        })
        return True
    
    def confirm(self, seat):
        seat.reservation_expiry = None
        seat.state = ConfirmedState()
        event_bus.publish(SEAT_CONFIRMED, {
            "seat": seat.row_and_number
        })
        return True
    
    def check_expiry(self, seat):
        if seat.reservation_expiry and datetime.now() >= seat.reservation_expiry:
            expiry_time = seat.reservation_expiry
            self.release(seat)
            raise ReservationExpiredException(seat.row_and_number, expiry_time)
        return False
    
    def get_status(self):
        return "Temporarily Reserved"


class ConfirmedState(SeatState):
    
    def reserve(self, seat, user, minutes=0):
        raise SeatAlreadyReservedException(
            seat.row_and_number,
            "Confirmed"
        )
    
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
        return False
    
    def check_expiry(self, seat):
        return False  
    
    def get_status(self):
        return "Confirmed"