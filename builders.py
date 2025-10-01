from factories import get_factory_for_user
from services import promotion_manager


#----- Builder ------
class ComboBuilder:
    def __init__(self, user):
        self.user = user
        self.factory = get_factory_for_user(user)
        self.ticket = None
        self.extras = []
        self.total_price = 0.0

    def add_ticket(self, ticket_type, seat, showtime, price=25.0):
        self.ticket = create_ticket_with_factory(self.user, ticket_type, seat, showtime, price=price)
        self.factory = get_factory_for_user(self.user, ticket_type)
        self.total_price += self.ticket.price
        return self
    
    def add_popcorn(self, size="M", price=5.0):
        popcorn = self.factory.create_product("popcorn", size=size)
        popcorn.purchase_product()
        self.extras.append(popcorn)
        self.total_price += popcorn.price
        return self
    def add_candy(self, candy_type="Mixed", price=6.0):
        candy = self.factory.create_product("candy", type=candy_type)
        candy.purchase_product()
        self.extras.append(candy)
        self.total_price += candy.price
        return self
    def add_nachos(self, topping="cheese", price=10.0):
        nachos = self.factory.create_product("nachos", topping=topping)
        nachos.purchase_product()
        self.extras.append(nachos)
        self.total_price += nachos.price
        return self
    def add_hotdog(self, size="regular", price=12.0):
        hotdog = self.factory.create_product("hotdog", size=size)
        hotdog.purchase_product()
        self.extras.append(hotdog)
        self.total_price += hotdog.price
        return self
    def add_soda(self, size="M", price=4.0):
        soda = self.factory.create_product("soda", size=size)
        soda.purchase_product()
        self.extras.append(soda)
        self.total_price += soda.price
        return self
    def add_juice(self, size="M", price=5.0):
        juice = self.factory.create_product("juice", size=size)
        juice.purchase_product()
        self.extras.append(juice)
        self.total_price += juice.price
        return self

    def add_water(self, size="M", price=4.0):
        water = self.factory.create_product("water", size=size, price=price)
        water.purchase_product()
        self.extras.append(water)
        self.total_price += water.price
        return self
    
    def remove_extra(self, identifier):
        if isinstance(identifier, int):
            idx = identifier
        else:
            idx = next((i for i, extra in enumerate(self.extras) if extra.name == identifier), None)

        if idx is None or not (0 <= idx < len(self.extras)):
            print("Invalid index or name.")
            return False
        
        extra = self.extras.pop(idx)

        try:
            if hasattr(extra, 'cancel_purchase') and callable(extra.cancel_purchase):
                extra.cancel_purchase()
        except Exception as e:
            print(f"Error cancelling purchase for {extra.name}: {e}")
        
        self.total_price = max(0.0, self.total_price - getattr(extra, 'price', 0.0))
        print(f"Removed extra: {extra.name} - R$ {getattr(extra, 'price', 0.0):.2f}")
        return True
    
    def apply_coupon(self, coupon_code):
        if not self.ticket or not coupon_code:
            print("No ticket or coupon provided.")
            return self

        coupon = promotion_manager.get_coupon(coupon_code)
        if not coupon:
            print("Invalid coupon code.")
            return self

        subtotal = self.ticket.price + sum(extra.price for extra in self.extras)

        cinema_name = None
        movie_name = self.ticket.showtime.movie.name if self.ticket and self.ticket.showtime else None
        user_type = "student" if "student" in self.ticket.name.lower() else "regular"

        if not coupon.can_apply(subtotal, cinema_name, movie_name, user_type):
            print(f"Coupon '{coupon.code}' cannot be applied to this purchase.")
            return self
        
        try:
            self.ticket.promotion(coupon)
            for extra in self.extras:
                if hasattr(extra, 'promotion') and callable(extra.promotion):
                    extra.promotion(coupon)
        except Exception as e:
            print(f"Error applying coupon: {e}")
            return self

        self.total_price = self.ticket.price + sum(extra.price for extra in self.extras)
        coupon.use()
        discount = subtotal - self.total_price
        print(f"Coupon '{coupon.code}' applied! Discount: R$ {discount:.2f}")
        return self
    def build(self):
        if not self.ticket:
            raise ValueError("A ticket must be added to the combo.")
        combo = {
            "ticket": self.ticket,
            "extras": self.extras,
            "total_price": self.total_price,
            "user": self.user
        }
        return combo
def create_ticket_with_factory(user, ticket_type, seat, showtime, price=25.0):
    factory = get_factory_for_user(user, ticket_type)
    ticket = factory.create_product("ticket", name=f"{ticket_type.title()} Ticket", price=price, seat=seat, showtime=showtime)
    return ticket