from abc import ABC, abstractmethod
import qrcode

#----- Produtos Abstratos------
class FOOD(ABC):
    def __init__(self, name, price, size_or_type):
        self.name = name
        self.price = price
        self.size_or_type = size_or_type

    @abstractmethod
    def purchase_product(self, user=None):
        pass

    @abstractmethod
    def cancel_purchase(self, user=None):
        pass

    @abstractmethod
    def calculate_food_price(self):
        pass

    @abstractmethod
    def promotion(self, coupon=None):
        pass


class DRINK(ABC):
    def __init__(self, name, price, size):
        self.name = name
        self.price = price
        self.size = size

    @abstractmethod
    def purchase_product(self, user=None):
        pass

    @abstractmethod
    def cancel_purchase(self, user=None):
        pass

    @abstractmethod
    def calculate_drink_price(self):
        pass

    @abstractmethod
    def promotion(self, coupon=None):
        pass


class SERVICE(ABC):
    def __init__(self, name, price):
        self.name = name
        self.price = price

    @abstractmethod
    def purchase_product(self, user=None):
        pass

    @abstractmethod
    def cancel_purchase(self, user=None):
        pass

    @abstractmethod
    def generate_service_confirmation(self):
        pass

    @abstractmethod
    def promotion(self, coupon=None):
        pass


#----- Produtos Concretos -----

class POPCORN(FOOD):
    def __init__(self, name: str, price: float, size: str):
        super().__init__(name, price, size_or_type=size)
        self.size = size

    def calculate_food_price(self):
        size_prices = {"S": 4.5, "M": 6.0, "L": 7.5}
        base_price = size_prices.get(self.size.upper(), 5.0)
        has_discount = "(Student" in self.name or "(VIP" in self.name or "(VIP Discount 50 %" in self.name
        return base_price * 0.5 if has_discount else max(self.price, base_price)

    def purchase_product(self, user=None):
        self.price = self.calculate_food_price()
        return self.price

    def cancel_purchase(self, user=None):
        # No side-effect prints here; state handling elsewhere.
        return True

    def promotion(self, coupon=None):
        if coupon and getattr(coupon, "can_apply", None) and getattr(coupon, "apply_discount", None):
            if coupon.can_apply(self.price):
                new_price, discount = coupon.apply_discount(self.price)
                self.price = new_price
                self.last_discount_amount = discount
                self.last_coupon_code = getattr(coupon, "code", None)
        return self.price


class TICKET(SERVICE):
    def __init__(self, name, price, seat, showtime):
        super().__init__(name, price)
        self.seat = seat
        self.showtime = showtime
        self.extras = []

    def purchase_product(self, user=None):
        # Reserve the seat temporarily; confirmation handled by UI/finalize logic.
        self.seat.temp_reserve(user)
        return True

    def cancel_purchase(self, user=None):
        self.seat.release(user)
        return True

    def generate_service_confirmation(self):
        return self.generate_qr_code()

    def promotion(self, coupon=None):
        cinema_name = None
        movie_name = None
        try:
            movie_name = self.showtime.movie.name if self.showtime and getattr(self.showtime, "movie", None) else None
        except Exception:
            movie_name = None
        user_type = "student" if "student" in self.name.lower() else "regular"

        if coupon and getattr(coupon, "can_apply", None) and getattr(coupon, "apply_discount", None):
            if coupon.can_apply(self.price, cinema_name, movie_name, user_type):
                new_price, discount = coupon.apply_discount(self.price)
                self.price = new_price
                self.last_discount_amount = discount
                self.last_coupon_code = getattr(coupon, "code", None)
        return self.price

    def generate_qr_code(self):
        data = f"""
        Ticket for seat {self.seat.row_and_number}
        Movie: {self.showtime.movie.name}
        Time: {self.showtime.time}
        Room: {self.showtime.screen_number}
        """
        qr = qrcode.QRCode(box_size=2)
        qr.add_data(data)
        # Keep QR printing as user-facing confirmation
        print("\n📲 Mobile Ticket With QR Code:")
        print("-" * 40)
        print(data.strip())
        print("-" * 40)
        qr.print_ascii(invert=True)
        print("-" * 40)


class CANDY(FOOD):
    def __init__(self, name: str, price: float, candy_type: str):
        super().__init__(name, price, size_or_type=candy_type)
        self.candy_type = candy_type

    def calculate_food_price(self):
        base_price = 6.0
        has_discount = "(Student" in self.name or "(VIP" in self.name
        return base_price * 0.5 if has_discount else max(self.price, base_price)

    def purchase_product(self, user=None):
        self.price = self.calculate_food_price()
        return self.price

    def cancel_purchase(self, user=None):
        return True

    def promotion(self, coupon=None):
        if coupon and getattr(coupon, "can_apply", None) and getattr(coupon, "apply_discount", None):
            if coupon.can_apply(self.price):
                new_price, discount = coupon.apply_discount(self.price)
                self.price = new_price
                self.last_discount_amount = discount
                self.last_coupon_code = getattr(coupon, "code", None)
        return self.price


class NACHOS(FOOD):
    def __init__(self, name: str, price: float, topping: str = "cheese"):
        super().__init__(name, price, size_or_type=topping)
        self.topping = topping

    def calculate_food_price(self):
        base_price = 10.0
        topping_extras = {"cheese": 0, "jalapeño": 2.0, "guacamole": 3.0}
        extra_cost = topping_extras.get(self.topping.lower(), 0)
        total_price = base_price + extra_cost

        has_discount = "(Student" in self.name or "(VIP" in self.name
        return total_price * 0.5 if has_discount else max(self.price, total_price)

    def purchase_product(self, user=None):
        self.price = self.calculate_food_price()
        return self.price

    def cancel_purchase(self, user=None):
        return True

    def promotion(self, coupon=None):
        if coupon and getattr(coupon, "can_apply", None) and getattr(coupon, "apply_discount", None):
            if coupon.can_apply(self.price):
                new_price, discount = coupon.apply_discount(self.price)
                self.price = new_price
                self.last_discount_amount = discount
                self.last_coupon_code = getattr(coupon, "code", None)
        return self.price


class HOTDOG(FOOD):
    def __init__(self, name: str, price: float, size: str = "regular"):
        super().__init__(name, price, size_or_type=size)
        self.size = size

    def calculate_food_price(self):
        size_prices = {"small": 10.0, "regular": 12.0, "jumbo": 15.0}
        base_price = size_prices.get(self.size.lower(), 12.0)

        has_discount = "(Student" in self.name or "(VIP" in self.name
        return base_price * 0.5 if has_discount else max(self.price, base_price)

    def purchase_product(self, user=None):
        self.price = self.calculate_food_price()
        return self.price

    def cancel_purchase(self, user=None):
        return True

    def promotion(self, coupon=None):
        if coupon and getattr(coupon, "can_apply", None) and getattr(coupon, "apply_discount", None):
            if coupon.can_apply(self.price):
                new_price, discount = coupon.apply_discount(self.price)
                self.price = new_price
                self.last_discount_amount = discount
                self.last_coupon_code = getattr(coupon, "code", None)
        return self.price


class SODA(DRINK):
    def __init__(self, name: str, price: float, size: str):
        super().__init__(name, price, size)

    def calculate_drink_price(self):
        size_prices = {"S": 3.0, "M": 4.0, "L": 5.0}
        base_price = size_prices.get(self.size.upper(), 4.0)
        has_discount = "(Student" in self.name or "(VIP" in self.name or "(VIP Discount 50 %" in self.name
        return base_price * 0.5 if has_discount else max(self.price, base_price)

    def purchase_product(self, user=None):
        self.price = self.calculate_drink_price()
        return self.price

    def cancel_purchase(self, user=None):
        return True

    def promotion(self, coupon=None):
        if coupon and getattr(coupon, "can_apply", None) and getattr(coupon, "apply_discount", None):
            if coupon.can_apply(self.price):
                new_price, discount = coupon.apply_discount(self.price)
                self.price = new_price
                self.last_discount_amount = discount
                self.last_coupon_code = getattr(coupon, "code", None)
        return self.price


class JUICE(DRINK):
    def __init__(self, name: str, price: float, size: str):
        super().__init__(name, price, size)

    def calculate_drink_price(self):
        size_prices = {"S": 5.0, "M": 6.5, "L": 8.0}
        base_price = size_prices.get(self.size.upper(), 6.0)
        has_discount = "(Student" in self.name or "(VIP" in self.name or "(VIP Discount 50 %" in self.name
        return base_price * 0.5 if has_discount else max(self.price, base_price)

    def purchase_product(self, user=None):
        self.price = self.calculate_drink_price()
        return self.price

    def cancel_purchase(self, user=None):
        return True

    def promotion(self, coupon=None):
        if coupon and getattr(coupon, "can_apply", None) and getattr(coupon, "apply_discount", None):
            if coupon.can_apply(self.price):
                new_price, discount = coupon.apply_discount(self.price)
                self.price = new_price
                self.last_discount_amount = discount
                self.last_coupon_code = getattr(coupon, "code", None)
        return self.price


class WATER(DRINK):
    def __init__(self, name: str, price: float, size: str):
        super().__init__(name, price, size)

    def calculate_drink_price(self):
        size_prices = {"S": 3.0, "M": 4.0, "L": 5.0}
        base_price = size_prices.get(self.size.upper(), 4.0)
        has_discount = "(Student" in self.name or "(VIP" in self.name or "(VIP Discount 50 %" in self.name
        return base_price * 0.5 if has_discount else max(self.price, base_price)

    def purchase_product(self, user=None):
        self.price = self.calculate_drink_price()
        return self.price

    def cancel_purchase(self, user=None):
        return True

    def promotion(self, coupon=None):
        if coupon and getattr(coupon, "can_apply", None) and getattr(coupon, "apply_discount", None):
            if coupon.can_apply(self.price):
                new_price, discount = coupon.apply_discount(self.price)
                self.price = new_price
                self.last_discount_amount = discount
                self.last_coupon_code = getattr(coupon, "code", None)
        return self.price