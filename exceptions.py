import re
# ---------EXCEÇÕES DE VALIDAÇÃO (herdam de ValueError)-------

class InvalidEmailException(ValueError):
    def __init__(self, email, message=None):
        self.email = email
        self.message = message or f"Invalid email: '{email}'. Must contain '@' and valid domain."
        super().__init__(self.message)


class InvalidPhoneException(ValueError):
    def __init__(self, phone, message=None):
        self.phone = phone
        self.message = message or f"Invalid phone: '{phone}'. Must have 10-11 digits."
        super().__init__(self.message)


class InvalidCPFException(ValueError):
    def __init__(self, cpf, message=None):
        self.cpf = cpf
        self.message = message or f"Invalid CPF: '{cpf}'. Check the format (XXX.XXX.XXX-XX)."
        super().__init__(self.message)


class InvalidPasswordException(ValueError):
    def __init__(self, message="Invalid password. Must have at least 8 characters."):
        self.message = message
        super().__init__(self.message)

# ---------EXCEÇÕES DE RESERVA (herdam de RuntimeError)-------------
class BookingException(RuntimeError):
    pass


class SeatAlreadyReservedException(BookingException):
    def __init__(self, seat_number, current_state=None):
        self.seat_number = seat_number
        self.current_state = current_state
        message = f"Seat {seat_number} is already reserved"
        if current_state:
            message += f" (State: {current_state})"
        super().__init__(message)


class ReservationExpiredException(BookingException):
    def __init__(self, seat_number, expiry_time=None):
        self.seat_number = seat_number
        self.expiry_time = expiry_time
        message = f"Reservation for seat {seat_number} has expired"
        if expiry_time:
            message += f" at {expiry_time.strftime('%H:%M:%S')}"
        super().__init__(message)


class SeatNotAvailableException(BookingException):
    def __init__(self, seat_number, operation="reserve"):
        self.seat_number = seat_number
        self.operation = operation
        super().__init__(
            f"Seat {seat_number} is not available for operation: {operation}"
        )


#----------- EXCEÇÕES DE PAGAMENTO (herdam de RuntimeError)---------

class PaymentException(RuntimeError):
    pass


class PaymentLimitExceededException(PaymentException):
    def __init__(self, payment_method, amount, limit):
        self.payment_method = payment_method
        self.amount = amount
        self.limit = limit
        
        message = (
            f"Payment limit exceeded for '{payment_method}':\n"
            f"  • Requested amount: R$ {amount:.2f}\n"
            f"  • Allowed limit: R$ {limit:.2f}\n"
            f"  • Difference: R$ {amount - limit:.2f}"
        )
        super().__init__(message)


class PaymentProcessingException(PaymentException):
    def __init__(self, message="Error processing payment", details=None):
        self.details = details
        full_message = message
        if details:
            full_message += f". Details: {details}"
        super().__init__(full_message)


class InvalidPaymentMethodException(PaymentException):
    def __init__(self, payment_method, valid_methods=None):
        self.payment_method = payment_method
        self.valid_methods = valid_methods
        message = f"Invalid payment method: '{payment_method}'"
        if valid_methods:
            message += f". Valid methods: {', '.join(valid_methods)}"
        super().__init__(message)



#------------ EXCEÇÕES DE CUPOM (herdam de RuntimeError)-------------

class CouponException(RuntimeError):
    pass


class InvalidCouponException(CouponException):
    def __init__(self, coupon_code, reason=None):
        self.coupon_code = coupon_code
        self.reason = reason
        message = f"Coupon '{coupon_code}' is invalid or inactive"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class CouponExpiredException(CouponException):
    def __init__(self, coupon_code, expiry_date=None):
        self.coupon_code = coupon_code
        self.expiry_date = expiry_date
        message = f"Coupon '{coupon_code}' has expired"
        if expiry_date:
            message += f" on {expiry_date.strftime('%d/%m/%Y')}"
        super().__init__(message)


class CouponUsageLimitException(CouponException):
    def __init__(self, coupon_code, max_uses=None):
        self.coupon_code = coupon_code
        self.max_uses = max_uses
        message = f"Coupon '{coupon_code}' has reached its usage limit"
        if max_uses:
            message += f" ({max_uses} times)"
        super().__init__(message)


class MinimumPurchaseException(CouponException):
    def __init__(self, coupon_code, min_purchase, current_total):
        self.coupon_code = coupon_code
        self.min_purchase = min_purchase
        self.current_total = current_total
        super().__init__(
            f"Coupon '{coupon_code}' requires a minimum purchase of R$ {min_purchase:.2f}. "
            f"Current value: R$ {current_total:.2f}"
        )



# ---------EXCEÇÕES DE NOTIFICAÇÃO (herdam de RuntimeError)----------

class NotificationException(RuntimeError):
    pass


class NotificationDeliveryException(NotificationException):
    def __init__(self, channel, message, original_error=None):
        self.channel = channel
        self.original_error = original_error
        full_message = f"Failed to send notification via {channel}: {message}"
        if original_error:
            full_message += f" (Error: {original_error})"
        super().__init__(full_message)


class InvalidNotificationChannelException(NotificationException):
    def __init__(self, channel, available_channels=None):
        self.channel = channel
        self.available_channels = available_channels
        message = f"Invalid notification channel: '{channel}'"
        if available_channels:
            message += f". Available channels: {', '.join(available_channels)}"
        super().__init__(message)


# ----------EXCEÇÕES DE AUTENTICAÇÃO (herdam de RuntimeError)----------

class AuthenticationException(RuntimeError):
    pass


class InvalidCredentialsException(AuthenticationException):
    def __init__(self, login=None):
        self.login = login
        message = "Invalid credentials"
        if login:
            message += f" for user '{login}'"
        super().__init__(message)


class UserNotFoundException(AuthenticationException):
    def __init__(self, identifier):
        self.identifier = identifier
        super().__init__(f"User '{identifier}' not found")


class UnauthorizedAccessException(AuthenticationException):
    def __init__(self, user_login, resource=None):
        self.user_login = user_login
        self.resource = resource
        message = f"Unauthorized access for user '{user_login}'"
        if resource:
            message += f" to resource '{resource}'"
        super().__init__(message)



# ---------- EXCEÇÕES DE SERVIÇOS EXTERNOS (herdam de ConnectionError) ----------
"""
class ServiceUnavailableException(ConnectionError):
    def __init__(self, service_name, details=None):
        self.service_name = service_name
        self.details = details
        message = f"Service '{service_name}' unavailable"
        if details:
            message += f": {details}"
        super().__init__(message)
""" # Não usei essa exceção no projeto, mas deixei aqui comentada caso precise futuramente.



# ------------ FUNÇÕES DE VALIDAÇÃO --------------------

def validate_cpf(cpf: str):    
    cpf_clean = re.sub(r'\D', '', cpf)
    
    if len(cpf_clean) != 11:
        raise InvalidCPFException(cpf, "CPF must have 11 digits")

    if cpf_clean == cpf_clean[0] * 11:
        raise InvalidCPFException(cpf, "CPF must not be a repeated sequence")

    def calculate_digit(cpf_partial, weights):
        total = sum(int(digit) * weight for digit, weight in zip(cpf_partial, weights))
        remainder = total % 11
        return 0 if remainder < 2 else 11 - remainder
    
    first_digit = calculate_digit(cpf_clean[:9], range(10, 1, -1))
    if int(cpf_clean[9]) != first_digit:
        raise InvalidCPFException(cpf, "First verification digit is invalid")
    
    second_digit = calculate_digit(cpf_clean[:10], range(11, 1, -1))
    if int(cpf_clean[10]) != second_digit:
        raise InvalidCPFException(cpf, "Second verification digit is invalid")

    return True


def validate_email(email: str):    
    if not email or not isinstance(email, str):
        raise InvalidEmailException(email, "Email must not be empty")
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise InvalidEmailException(email)
    
    return True


def validate_phone(phone: str):    
    if not phone or not isinstance(phone, str):
        raise InvalidPhoneException(phone, "Phone must not be empty")
    
    phone_clean = re.sub(r'\D', '', phone)
    
    if not re.match(r'^\d{10,11}$', phone_clean):
        raise InvalidPhoneException(phone)
    
    return True



EXCEPTION_REGISTRY = {
    'invalid_email': InvalidEmailException,
    'invalid_phone': InvalidPhoneException,
    'invalid_cpf': InvalidCPFException,
    'invalid_password': InvalidPasswordException,
    
    'seat_already_reserved': SeatAlreadyReservedException,
    'reservation_expired': ReservationExpiredException,
    'seat_not_available': SeatNotAvailableException,
    
    'payment_limit_exceeded': PaymentLimitExceededException,
    'payment_processing': PaymentProcessingException,
    'invalid_payment_method': InvalidPaymentMethodException,
    
    'invalid_coupon': InvalidCouponException,
    'coupon_expired': CouponExpiredException,
    'coupon_usage_limit': CouponUsageLimitException,
    'minimum_purchase': MinimumPurchaseException,
    
    'notification_delivery': NotificationDeliveryException,
    'invalid_notification_channel': InvalidNotificationChannelException,
    
    'invalid_credentials': InvalidCredentialsException,
    'user_not_found': UserNotFoundException,
    'unauthorized_access': UnauthorizedAccessException,
    
    'service_unavailable': ServiceUnavailableException,
}


__all__ = [
    'InvalidEmailException',
    'InvalidPhoneException',
    'InvalidCPFException',
    'InvalidPasswordException',
    'BookingException',
    'SeatAlreadyReservedException',
    'ReservationExpiredException',
    'SeatNotAvailableException',
    'PaymentException',
    'PaymentLimitExceededException',
    'PaymentProcessingException',
    'InvalidPaymentMethodException',
    'CouponException',
    'InvalidCouponException',
    'CouponExpiredException',
    'CouponUsageLimitException',
    'MinimumPurchaseException',
    'NotificationException',
    'NotificationDeliveryException',
    'InvalidNotificationChannelException',
    'AuthenticationException',
    'InvalidCredentialsException',
    'UserNotFoundException',
    'UnauthorizedAccessException',
    'ServiceUnavailableException',
    
    'validate_cpf',
    'validate_email',
    'validate_phone',
    
    'EXCEPTION_REGISTRY',
]
