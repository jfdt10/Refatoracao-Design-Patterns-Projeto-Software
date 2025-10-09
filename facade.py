from services import notification_service, promotion_manager
from datetime import datetime
from builders import ComboBuilder
from models import USER, CINEMA, MOVIE, SEAT
from observer import event_bus
from utils import PAYMENT_SUCCESS, BOOKING_CONFIRMED, BOOKING_CANCELLED, PAYMENT_REFUNDED
from typing import List
+from commands import PurchaseComboCommand, CancelProductCommand, CommandInvoker
#-------------- Subsistemas do Facade-----------------

class Notification_Subsystem:
    def __init__(self):
        self._notifier = notification_service 
    
    def send(self, user, notification_type, message, data=None):
        return self._notifier.send_notification(user, notification_type, message, data)

    def get_notifications(self, user_id, unread_only=False):
        return self._notifier.get_user_notifications(user_id, unread_only)

    def mark_as_read(self, notification_id):
        return self._notifier.mark_notification_as_read(notification_id)


class Promotion_Subsystem:
    def __init__(self):
        self._promotion_manager = promotion_manager

    def coupons_initialization(self):
        self._promotion_manager.initialize_coupons()

    def add_coupon(self, coupon):
        self._promotion_manager.add_coupon(coupon)

    def get_coupon(self, code):
        return self._promotion_manager.get_coupon(code)

    def list_active(self):
        return self._promotion_manager.list_active_coupons()
    
    def validate_and_apply(self, coupon_code: str, builder: ComboBuilder, user):
        coupons = self.get_coupon(coupon_code)
        if not coupons:
            return False, f"Coupon {coupon_code} not found."
        try:
            builder.apply_coupon(coupon_code)
            return True, f"Coupon {coupon_code} applied successfully."
        except Exception as e:
            return False, f"Error applying coupon: {str(e)}"


class ComboManagementSubsystem:

    def create_builder(self, user):
        return ComboBuilder(user)

    def add_ticket_to_combo(self, builder: ComboBuilder, ticket_type, seat: SEAT, showtime, price: float = 25.0):
        builder.add_ticket(ticket_type, seat, showtime, price)
        return builder
    
    def add_extras_to_combo(self, builder: ComboBuilder, extras: List[dict]): 
        for extra in extras:
            extra_type = extra.get("type", "").lower()
            
            if extra_type == "popcorn":
                builder.add_popcorn(size=extra.get("size", "M"))
            elif extra_type == "soda":
                builder.add_soda(size=extra.get("size", "M"))
            elif extra_type == "juice":
                builder.add_juice(size=extra.get("size", "M"))
            elif extra_type == "water":
                builder.add_water(size=extra.get("size", "M"))
            elif extra_type == "candy":
                builder.add_candy(candy_type=extra.get("candy_type", "Mixed"))
            elif extra_type == "nachos":
                builder.add_nachos(topping=extra.get("topping", "cheese"))
            elif extra_type == "hotdog":
                builder.add_hotdog(size=extra.get("size", "regular"))
        
        return builder
         
    def build_combo(self, builder: ComboBuilder): 
        return builder.build()
    

class PaymentSubsystem:
    def process_payment(self, method: str, amount: float, user):
        method = method.lower()
        
        if method in ["credit", "credito", "crédito"]:
            return self._process_credit(amount, user)
        elif method in ["debit", "debito", "débito"]:
            return self._process_debit(amount, user)
        elif method == "pix":
            return self._process_pix(amount, user)
        else:
            return False, f"Método '{method}' não suportado"
    
    def _process_credit(self, amount: float, user):
        transaction_id = f"CC-{datetime.now().timestamp()}"
        print(f"[Payment] Cartão de Crédito: R${amount:.2f} - {user.name}")
        return True, transaction_id
    
    def _process_debit(self, amount: float, user):
        transaction_id = f"DB-{datetime.now().timestamp()}"
        print(f"[Payment] Cartão de Débito: R${amount:.2f} - {user.name}")
        return True, transaction_id

    def _process_pix(self, amount: float, user):
        transaction_id = f"PIX-{datetime.now().timestamp()}"
        print(f"[Payment] PIX: R${amount:.2f} - {user.name}")
        return True, transaction_id


class BookingSubsystem:
    
    def reserve_seat(self, seat: SEAT, user, minutes: int = 10):
        return seat.temp_reserve(user, minutes)

    def confirm_seat(self, seat: SEAT):
        return seat.confirm()
    
    def release_seat(self, seat: SEAT, user=None):  
        return seat.release(user)

    def check_seat_expiry(self, seat: SEAT):
        return seat.check_expiry()
    

# ---------------- Facade Sistema ---------------------

class CinemaSystemFacade:
    def __init__(self,
                 notification_subsystem: Notification_Subsystem = None,
                 promotion_subsystem: Promotion_Subsystem = None,
                 combo_subsystem: ComboManagementSubsystem = None,
                 payment_subsystem: PaymentSubsystem = None,
                 booking_subsystem: BookingSubsystem = None,
                 invoker: CommandInvoker = None):  

        self.notifications = notification_subsystem or Notification_Subsystem()
        self.promotions = promotion_subsystem or Promotion_Subsystem()
        self.combos = combo_subsystem or ComboManagementSubsystem()
        self.payments = payment_subsystem or PaymentSubsystem()
        self.bookings = booking_subsystem or BookingSubsystem()
        self.invoker = invoker or CommandInvoker()

    def complete_ticket_purchase(self, user: USER, cinema: CINEMA, movie: MOVIE, showtime, seat: SEAT,
                                 ticket_type: str, payment_method: str, extras: List[dict] = None,
                                 coupon_code: str = None):
        result = {
            "success": False,
            "combo": None,
            "original_price": 0.0,
            "final_price": 0.0,
            "discount": 0.0,
            "transaction_id": None,
            "message": "",
            "seat_confirmed": False
        }

        if not self.bookings.reserve_seat(seat, user, minutes=10):
            result["message"] = f"Não foi possível reservar o assento {seat.row_and_number}"
            return result
        
        try:
            builder = self.combos.create_builder(user)
            self.combos.add_ticket_to_combo(builder, ticket_type, seat, showtime)
            
            if extras:
                self.combos.add_extras_to_combo(builder, extras)
            
            result["original_price"] = builder._total_price
            
            if coupon_code:
                success, message = self.promotions.validate_and_apply(coupon_code, builder, user)
                if success:
                    result["discount"] = result["original_price"] - builder._total_price
                    self.notifications.send(
                        user, "coupon_applied",
                        f"Cupom aplicado! Desconto: R${result['discount']:.2f}",
                        {"coupon": coupon_code, "discount": result["discount"]}
                    )
                else:
                    self.notifications.send(user, "coupon_failed", message)
            
            combo = self.combos.build_combo(builder)
            result["combo"] = combo
            result["final_price"] = combo.total_price
            
            if self.bookings.check_seat_expiry(seat):
                result["message"] = "Reserva expirou. Tente novamente."
                self.bookings.release_seat(seat, user)
                return result
            
            payment_success, transaction_id = self.payments.process_payment(
                payment_method,
                combo.total_price,
                user
            )
            
            if not payment_success:
                result["message"] = f"Falha no pagamento: {transaction_id}"
                self.bookings.release_seat(seat, user)
                self.notifications.send(user, "payment_failed", result["message"])
                return result
            
            result["transaction_id"] = transaction_id
            
            cmd = PurchaseComboCommand(
                combo=combo,
                movie=movie,
                showtime=showtime,
                seat=seat,
                user=user,
                finalize_fn=self._finalize_purchase
            )
            
            self.invoker.execute_command(cmd)
            
            if not getattr(cmd, "executed", False):
                result["message"] = "Falha ao executar comando de compra"
                self.bookings.release_seat(seat, user)
                return result
            
            result["seat_confirmed"] = True
            result["success"] = True
            result["message"] = "Compra realizada com sucesso!"
            
        except Exception as e:
            result["message"] = f"Erro durante a compra: {e}"
            self.bookings.release_seat(seat, user)
        
        return result

    def _finalize_purchase(self, combo, movie, showtime, seat):
        """Método auxiliar para finalizar compra (usado pelo Command)"""
        if self.bookings.confirm_seat(seat):
            combo.ticket.extras = combo.extras
            
            event_bus.publish(PAYMENT_SUCCESS, {
                "user": combo.user,
                "amount": combo.total_price,
                "movie": movie.name,
                "time": showtime.time,
                "seat": seat.row_and_number
            })
            
            event_bus.publish(BOOKING_CONFIRMED, {
                "user": combo.user,
                "movie": movie.name,
                "time": showtime.time,
                "seat": seat.row_and_number
            })
            
            self.notifications.send(
                combo.user, "purchase_success",
                f"Compra confirmada! {movie.name} - Assento {seat.row_and_number}",
                {
                    "ticket_id": getattr(combo.ticket, 'id', None),
                    "final_price": combo.total_price
                }
            )
            return True
        return False

    def cancel_booking(self, user: USER, ticket_id: str, movie: MOVIE, seat: SEAT):
        result = {
            "success": False,
            "refunded_amount": 0.0,
            "message": ""
        }
        
        ticket = next((t for t in user.booking_history if getattr(t, 'id', None) == ticket_id), None)
        if not ticket:
            result["message"] = f"Ticket ID {ticket_id} não encontrado nas reservas do usuário."
            return result
        
        try:
            cmd = CancelProductCommand(ticket, user)
            self.invoker.execute_command(cmd)
            
            if not getattr(cmd, "executed", False):
                result["message"] = "Falha ao executar comando de cancelamento"
                return result
            
            refund = float(getattr(ticket, "price", 0.0) or 0.0)
            for extra in getattr(ticket, "extras", []) or []:
                refund += float(getattr(extra, "price", 0.0) or 0.0)
            
            result["refund_amount"] = refund
            
            self.bookings.release_seat(seat, user)
            
            user.cancel_booking(ticket)
            
            if movie:
                movie.total_tickets_sold = max(0, movie.total_tickets_sold - 1)
                movie.total_revenue = max(0.0, movie.total_revenue - refund)
            
            event_bus.publish(BOOKING_CANCELLED, {
                "user": user,
                "movie": movie.name if movie else None,
                "seat": seat.row_and_number,
                "refund": refund
            })
            
            event_bus.publish(PAYMENT_REFUNDED, {
                "user": user,
                "amount": refund,
                "seat": seat.row_and_number
            })
            
            self.notifications.send(
                user, "booking_cancelled",
                f"Reserva cancelada. Reembolso: R${refund:.2f}",
                {"refund": refund, "seat": seat.row_and_number}
            )
            
            result["success"] = True
            result["message"] = f"Reserva cancelada. Reembolso: R${refund:.2f}"
            
        except Exception as e:
            result["message"] = f"Erro ao cancelar: {e}"
        
        return result
    
    def list_active_coupons(self):
        return self.promotions.list_active()
    
    def get_user_notifications(self, user_id: str, unread_only: bool = False):
        return self.notifications.get_notifications(user_id, unread_only)

cinema_system = CinemaSystemFacade(invoker=CommandInvoker())