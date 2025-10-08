from abc import ABC, abstractmethod
from dataclasses import dataclass
from factories import get_factory_for_user
from services import promotion_manager

# --- Produto Final ---
@dataclass
class Combo:
    ticket: object
    extras: list
    total_price: float
    user: object

# --- Interface Builder ---
class Builder(ABC):
    @abstractmethod
    def reset(self):
        pass
    
    @abstractmethod
    def build(self):
        pass

# --- Builder Concreto ---
class ComboBuilder(Builder):
    def __init__(self, user):
        self.user = user
        self.reset()
    
    def reset(self):
        self.factory = get_factory_for_user(self.user)
        self._ticket = None
        self._extras = []
        self._total_price = 0.0
        return self

    def add_ticket(self, ticket_type, seat, showtime, price=25.0):
        self._ticket = create_ticket_with_factory(self.user, ticket_type, seat, showtime, price=price)
        self.factory = get_factory_for_user(self.user, ticket_type)
        self._total_price += self._ticket.price
        return self
    
    def add_popcorn(self, size="M"):
        popcorn = self.factory.create_product("popcorn", size=size)
        self._extras.append(popcorn)
        self._total_price += popcorn.price
        return self
    
    def add_candy(self, candy_type="Mixed"):
        candy = self.factory.create_product("candy", type=candy_type)
        self._extras.append(candy)
        self._total_price += candy.price
        return self
    
    def add_nachos(self, topping="cheese"):
        nachos = self.factory.create_product("nachos", topping=topping)
        self._extras.append(nachos)
        self._total_price += nachos.price
        return self
    
    def add_hotdog(self, size="regular"):
        hotdog = self.factory.create_product("hotdog", size=size)
        self._extras.append(hotdog)
        self._total_price += hotdog.price
        return self
    
    def add_soda(self, size="M"):
        soda = self.factory.create_product("soda", size=size)
        self._extras.append(soda)
        self._total_price += soda.price
        return self
    
    def add_juice(self, size="M"):
        juice = self.factory.create_product("juice", size=size)
        self._extras.append(juice)
        self._total_price += juice.price
        return self

    def add_water(self, size="M", price=4.0):
        water = self.factory.create_product("water", size=size, price=price)
        self._extras.append(water)
        self._total_price += water.price
        return self
    
    def remove_extra(self, identifier):
        if isinstance(identifier, int):
            idx = identifier
        else:
            idx = next((i for i, extra in enumerate(self._extras) if extra.name == identifier), None)

        if idx is None or not (0 <= idx < len(self._extras)):
            print("Invalid index or name.")
            return False
        
        extra = self._extras.pop(idx)
        self._total_price = max(0.0, self._total_price - getattr(extra, 'price', 0.0))
        print(f"Removed extra: {extra.name} - R$ {getattr(extra, 'price', 0.0):.2f}")
        return True
    
    def apply_coupon(self, coupon_code):
        if not self._ticket or not coupon_code:
            print("No ticket or coupon provided.")
            return self

        coupon = promotion_manager.get_coupon(coupon_code)
        if not coupon:
            print("Invalid coupon code.")
            return self

        subtotal = self._ticket.price + sum(extra.price for extra in self._extras)
        movie_name = self._ticket.showtime.movie.name if self._ticket and self._ticket.showtime else None
        ticket_type = self._ticket.name.split()[0].lower() if self._ticket else "standard"
        user_type = self.user.user_type

        if not coupon.can_apply(subtotal, ticket_type=ticket_type, cinema_name=None, movie_name=movie_name, user_type=user_type):
            print(f"Coupon '{coupon.code}' cannot be applied to this purchase.")
            return self
        
        try:
            self._ticket.promotion(coupon)
            for extra in self._extras:
                if hasattr(extra, 'promotion') and callable(extra.promotion):
                    extra.promotion(coupon)
        except Exception as e:
            print(f"Error applying coupon: {e}")
            return self

        self._total_price = self._ticket.price + sum(extra.price for extra in self._extras)
        coupon.use()
        discount = subtotal - self._total_price
        print(f"Coupon '{coupon.code}' applied! Discount: R$ {discount:.2f}")
        return self
    
    def build(self) -> Combo:
        if not self._ticket:
            raise ValueError("A ticket must be added to the combo.")
        
        combo = Combo(
            ticket=self._ticket,
            extras=list(self._extras),
            total_price=self._total_price,
            user=self.user
        )
        self.reset() 
        return combo
    
class ComboDirector:

    def __init__(self):
        self._builder = None
    @property
    def builder(self):
        return self._builder
    
    @builder.setter
    def builder(self, builder: ComboBuilder):
        self._builder = builder
    
    def build_basic_combo(self, ticket_type, seat, showtime):
        self._builder.reset()
        self._builder.add_ticket(ticket_type, seat, showtime)
        self._builder.add_popcorn(size="M")
        self._builder.add_soda(size="M")
        return self._builder.build()
    
    def build_premium_combo(self, ticket_type, seat, showtime):
        self._builder.reset()
        self._builder.add_ticket(ticket_type, seat, showtime)
        self._builder.add_popcorn(size="L")
        self._builder.add_soda(size="L")
        self._builder.add_candy(candy_type="Chocolate")
        return self._builder.build()
    
    def build_family_combo(self, ticket_type, seat, showtime):
        self._builder.reset()
        self._builder.add_ticket(ticket_type, seat, showtime)
        self._builder.add_popcorn(size="L")
        self._builder.add_popcorn(size="L")
        self._builder.add_soda(size="M")
        self._builder.add_soda(size="M")
        self._builder.add_soda(size="M")
        self._builder.add_soda(size="M")
        return self._builder.build()
    
    def build_student_combo(self, ticket_type, seat, showtime):
        self._builder.reset()
        self._builder.add_ticket(ticket_type, seat, showtime)
        self._builder.add_popcorn(size="S")
        self._builder.add_water(size="M")
        return self._builder.build()


def create_ticket_with_factory(user, ticket_type, seat, showtime, price=25.0):
    factory = get_factory_for_user(user, ticket_type)
    ticket = factory.create_product("ticket", name=f"{ticket_type.title()} Ticket", price=price, seat=seat, showtime=showtime)
    return ticket