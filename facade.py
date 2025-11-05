from services import notification_service, promotion_manager
import random
from datetime import datetime
from builders import ComboBuilder
from models import USER, CINEMA, MOVIE, SEAT
from observer import event_bus, multi_channel_service
from utils import PAYMENT_SUCCESS, BOOKING_CONFIRMED, BOOKING_CANCELLED, PAYMENT_REFUNDED
from typing import List
from commands import PurchaseComboCommand, CancelProductCommand, CommandInvoker
from exceptions import (
    SeatAlreadyReservedException,
    ReservationExpiredException,
    SeatNotAvailableException,
    PaymentProcessingException,
    InvalidPaymentMethodException,
    PaymentLimitExceededException,
    InvalidCouponException,
    CouponExpiredException,
    CouponUsageLimitException,
    MinimumPurchaseException,
    NotificationDeliveryException,
)

PAYMENT_LIMITS = {
    "credit": 10000.00,
    "debit": 5000.00,
    "pix": 50000.00
}
PAYMENT_ERROR_RATE = 0.05

#-------------- Subsistemas do Facade-----------------

class Notification_Subsystem:
    def __init__(self, notification_service_instance):
        self._notifier = notification_service_instance

    def send(self, user, notification_type, message, data=None, channels=None):
        return self._notifier.send_notification(user, notification_type, message, data, channels)

    def get_notifications(self, user_id, unread_only=False):
        return self._notifier.get_user_notifications(user_id, unread_only)

    def mark_as_read(self, notification_id):
        return self._notifier.mark_as_read(notification_id)


class Promotion_Subsystem:
    def __init__(self):
        self._promotion_manager = promotion_manager

    def coupons_initialization(self):
        self._promotion_manager.initialize_default_coupons()

    def add_coupon(self, coupon):
        self._promotion_manager.add_coupon(coupon)

    def get_coupon(self, code):
        coupon = self._promotion_manager.get_coupon(code)
        if not coupon:
            raise InvalidCouponException(code, reason="Coupon not found")
        return coupon

    def list_active(self):
        return self._promotion_manager.list_active_coupons()

    def validate_and_apply(self, coupon_code: str, builder: ComboBuilder, user):
        coupon = self.get_coupon(coupon_code)
        coupon.is_valid(raise_exception=True)
        coupon.can_apply(
            total_amount=getattr(builder, "_total_price", 0.0),
            ticket_type=getattr(builder, "_ticket_type", None),
            raise_exception=True
        )
        builder.apply_coupon(coupon_code)
        return True, f"Coupon '{coupon_code}' successfully applied!"


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

        if not isinstance(method, str):
            raise TypeError("Payment method must be a string")
        if not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")

        method = method.lower()

        method_mapping = {
            "credit": "credit",
            "credito": "credit",
            "crédito": "credit",
            "debit": "debit",
            "debito": "debit",
            "débito": "debit",
            "pix": "pix"
        }

        if method not in method_mapping:
            raise InvalidPaymentMethodException(
                method, valid_methods=["Credit", "Debit", "PIX"]
            )
        
        method_key = method_mapping[method]
        limit = PAYMENT_LIMITS[method_key]

        if amount > limit:
            raise PaymentLimitExceededException(
                payment_method=method_key.upper(),
                amount=amount,
                limit=limit
            )
        
        if random.random() < PAYMENT_ERROR_RATE:
            raise PaymentProcessingException(
                "Error connecting to payment server",
                details="Please try again in a few seconds"
            )
        
        return self._process_by_method(method_key, amount, user)

    def _process_by_method(self, method_key: str, amount: float, user):
        if method_key == "credit":
            return self._process_credit(amount, user)
        elif method_key == "debit":
            return self._process_debit(amount, user)
        elif method_key == "pix":
            return self._process_pix(amount, user)

    def _process_credit(self, amount: float, user):
        transaction_id = f"CC-{datetime.now().timestamp()}"
        print(f"[Payment] Credit Card: R${amount:.2f} - {user.name}")
        return True, transaction_id

    def _process_debit(self, amount: float, user):
        transaction_id = f"DB-{datetime.now().timestamp()}"
        print(f"[Payment] Debit Card: R${amount:.2f} - {user.name}")
        return True, transaction_id

    def _process_pix(self, amount: float, user):
        transaction_id = f"PIX-{datetime.now().timestamp()}"
        print(f"[Payment] PIX: R${amount:.2f} - {user.name}")
        return True, transaction_id


class BookingSubsystem:

    def reserve_seat(self, seat: SEAT, user, minutes: int = 10):
        result = seat.temp_reserve(user, minutes)
        if not result:
            raise SeatAlreadyReservedException(
                seat.row_and_number,
                current_state=seat.get_status()
            )
        return result

    def confirm_seat(self, seat: SEAT):
        result = seat.confirm()
        if not result:
            raise SeatNotAvailableException(
                seat.row_and_number,
                operation="confirm"
            )
        return result

    def release_seat(self, seat: SEAT, user=None):
        return seat.release(user)

    def check_seat_expiry(self, seat: SEAT):
        expired = seat.check_reservation_expiry()
        if expired:
            raise ReservationExpiredException(
                seat.row_and_number,
                expiry_time=seat.reservation_expiry
            )
        return not expired

# ---------------- Facade Sistema ---------------------
class CinemaSystemFacade:
    def __init__(self,
                 notification_subsystem: Notification_Subsystem = None,
                 promotion_subsystem: Promotion_Subsystem = None,
                 combo_subsystem: ComboManagementSubsystem = None,
                 payment_subsystem: PaymentSubsystem = None,
                 booking_subsystem: BookingSubsystem = None,
                 invoker: CommandInvoker = None):

        self.notifications = notification_subsystem or Notification_Subsystem(multi_channel_service)
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

        seat_reserved = False
        
        try:
            seat_reserved = self.bookings.reserve_seat(seat, user, minutes=10)
        except (SeatAlreadyReservedException, SeatNotAvailableException) as e:
            result["message"] = str(e)
            return result

        try:
            builder = self.combos.create_builder(user)
            self.combos.add_ticket_to_combo(builder, ticket_type, seat, showtime)

            if extras:
                self.combos.add_extras_to_combo(builder, extras)

            original_price = getattr(builder, "_total_price", 0.0)
            result["original_price"] = original_price

            if coupon_code:
                try:
                    success, message = self.promotions.validate_and_apply(coupon_code, builder, user)
                    
                    new_total = getattr(builder, "_total_price", original_price)
                    discount = max(0.0, original_price - new_total)
                    result["discount"] = discount

                    if success and discount > 0:
                        try:
                            self.notifications.send(
                                user, "coupon_applied",
                                f"Coupon '{coupon_code}' applied! Discount: R$ {discount:.2f}",
                                {"coupon": coupon_code, "discount": discount}
                            )
                        except NotificationDeliveryException:
                            pass
                    elif success and discount == 0:
                        try:
                            self.notifications.send(
                                user, "coupon_applied_no_effect",
                                f"Coupon '{coupon_code}' applied but no discount.",
                                {"coupon": coupon_code}
                            )
                        except NotificationDeliveryException:
                            pass

                except (InvalidCouponException, CouponExpiredException, 
                        CouponUsageLimitException, MinimumPurchaseException) as e:
                    result["message"] = str(e)
                    return result

            combo = self.combos.build_combo(builder)
            result["combo"] = combo
            result["final_price"] = getattr(combo, "total_price", 0.0)

            try:
                self.bookings.check_seat_expiry(seat)
            except ReservationExpiredException as e:
                result["message"] = str(e)
                self.bookings.release_seat(seat, user)
                return result

            try:
                payment_success, transaction_id = self.payments.process_payment(
                    payment_method,
                    combo.total_price,
                    user
                )
                
                if not payment_success:
                    result["message"] = f"Payment failed: {transaction_id}"
                    self.bookings.release_seat(seat, user)
                    try:
                        self.notifications.send(user, "payment_failed", result["message"])
                    except NotificationDeliveryException:
                        pass
                    return result

                result["transaction_id"] = transaction_id

            except (PaymentLimitExceededException, PaymentProcessingException, 
                    InvalidPaymentMethodException) as e:
                result["message"] = str(e)
                self.bookings.release_seat(seat, user)
                return result

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
                result["message"] = "Failed to execute purchase command"
                return result

            result["seat_confirmed"] = True
            result["success"] = True
            result["message"] = "Purchase completed successfully!"

        finally:
            if seat_reserved and not result.get("seat_confirmed", False):
                self.bookings.release_seat(seat, user)
        
        return result

    def _finalize_purchase(self, combo, movie, showtime, seat):
        try:
            if not self.bookings.confirm_seat(seat):
                return False
        except SeatNotAvailableException:
            return False

        combo.ticket.extras = combo.extras

        event_bus.publish(PAYMENT_SUCCESS, {
            "user": combo.user,
            "amount": combo.total_price,
            "movie": getattr(movie, "name", None),
            "time": getattr(showtime, "time", None),
            "seat": getattr(seat, "row_and_number", None)
        })

        event_bus.publish(BOOKING_CONFIRMED, {
            "user": combo.user,
            "movie": getattr(movie, "name", None),
            "time": getattr(showtime, "time", None),
            "seat": getattr(seat, "row_and_number", None)
        })

        try:
            self.notifications.send(
                combo.user, "purchase_success",
                f"Purchase confirmed! {getattr(movie, 'name', '')} - Seat {getattr(seat, 'row_and_number', '')}",
                {
                    "ticket_id": getattr(combo.ticket, 'id', None),
                    "final_price": combo.total_price
                }
            )
        except NotificationDeliveryException:
            pass
        
        return True

    def cancel_booking(self, user: USER, ticket_id: str, movie: MOVIE, seat: SEAT):
        result = {
            "success": False,
            "refund_amount": 0.0,
            "message": ""
        }

        ticket = next((t for t in user.booking_history if getattr(t, 'id', None) == ticket_id), None)
        if not ticket:
            result["message"] = f"Ticket ID {ticket_id} not found"
            return result

        cmd = CancelProductCommand(ticket, user)
        self.invoker.execute_command(cmd)

        if not getattr(cmd, "executed", False):
            result["message"] = "Failed to execute cancel command"
            return result

        refund = float(getattr(ticket, "price", 0.0) or 0.0)
        for extra in getattr(ticket, "extras", []) or []:
            refund += float(getattr(extra, "price", 0.0) or 0.0)

        result["refund_amount"] = refund

        if seat is not None:
            self.bookings.release_seat(seat, user)

        user.cancel_booking(ticket)

        if movie:
            movie.total_tickets_sold = max(0, getattr(movie, "total_tickets_sold", 0) - 1)
            movie.total_revenue = max(0.0, getattr(movie, "total_revenue", 0.0) - refund)

        seat_id = getattr(seat, "row_and_number", "N/A") if seat else "N/A"
        movie_name = getattr(movie, "name", None) if movie else "N/A"
        
        event_bus.publish(BOOKING_CANCELLED, {
            "user": user,
            "movie": movie_name,
            "seat": seat_id,
            "refund": refund
        })

        event_bus.publish(PAYMENT_REFUNDED, {
            "user": user,
            "amount": refund,
            "seat": seat_id
        })

        try:
            self.notifications.send(
                user, "booking_cancelled",
                f"Booking canceled. Refund: R${refund:.2f}",
                {"refund": refund, "seat": seat_id}
            )
        except NotificationDeliveryException:
            pass

        result["success"] = True
        result["message"] = f"Booking canceled. Refund: R${refund:.2f}"

        return result

    def list_active_coupons(self):
        return self.promotions.list_active()

    def get_user_notifications(self, user_id: str, unread_only: bool = False):
        return self.notifications.get_notifications(user_id, unread_only)

# Criar instância do sistema com facade
cinema_system = CinemaSystemFacade(invoker=CommandInvoker())