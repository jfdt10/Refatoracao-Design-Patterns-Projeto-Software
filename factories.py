from abc import ABC, abstractmethod
from products import TICKET, POPCORN, CANDY, NACHOS, HOTDOG, SODA, JUICE, WATER





#------Abstract Factory--------------
class AbstractFactory(ABC):
    @abstractmethod
    def create_product(self, product_type:str, **kwargs):
        pass 

    def process_purchase(self, product:str, **kwargs):
        product = self.create_product(product, **kwargs)
        print(f"Processing purchase for {product.name}...")
        return product
    
#--- Factory Concreta---------
class StandardFactory(AbstractFactory):
    def create_product(self, product_type:str, **kwargs):
        if product_type == "ticket":
            return self.create_ticket(**kwargs) # factory method
        elif product_type == "popcorn":
            return self.create_popcorn(**kwargs) # factory method
        elif product_type == "candy":
            return self.create_candy(**kwargs)
        elif product_type == "nachos":
            return self.create_nachos(**kwargs)
        elif product_type == "hotdog":
            return self.create_hotdog(**kwargs)
        elif product_type == "soda":
            return self.create_soda(**kwargs)
        elif product_type == "juice":
            return self.create_juice(**kwargs)
        elif product_type == "water":
            return self.create_water(**kwargs)
        else:
            raise ValueError(f"Unknown product type: {product_type}")
     
    def create_ticket(self, **kwargs):
        return TICKET(
            kwargs.get("name", "Standard Ticket"),
            kwargs.get("price", 25.0),
            kwargs.get("seat"),
            kwargs.get("showtime")
        )
    
    def create_popcorn(self, **kwargs):
        return POPCORN(
            kwargs.get("name", "Popcorn"),
            kwargs.get("price", 5.0),
            kwargs.get("size", "M")
        )
    
    def create_candy(self, **kwargs):
        return CANDY(
            kwargs.get("name", "Candy"),
            kwargs.get("price", 6.0),
            kwargs.get("type", "Mixed")
        )
    
    def create_nachos(self, **kwargs):
        return NACHOS(
            kwargs.get("name", "Nachos"),
            kwargs.get("price", 10.0),
            kwargs.get("topping", "cheese")
        )
    
    def create_hotdog(self, **kwargs):
        return HOTDOG(
            kwargs.get("name", "Hot Dog"),
            kwargs.get("price", 12.0),
            kwargs.get("size", "regular")
        )
    
    def create_soda(self, **kwargs):
        return SODA(
            kwargs.get("name", "Soda"),
            kwargs.get("price", 4.0),
            kwargs.get("size", "M")
        )
    
    def create_juice(self, **kwargs):
        return JUICE(
            kwargs.get("name", "Juice"),
            kwargs.get("price", 5.0),
            kwargs.get("size", "M")
        )
    
    def create_water(self, **kwargs):
        return WATER(
            kwargs.get("name", "Water"),
            kwargs.get("price", 3.0),
            kwargs.get("size", "M")
        )
#--- Factory Concreta----------
class StudentFactory(AbstractFactory):
    def create_product(self, product_type:str, **kwargs):
        if product_type == "ticket":
            kwargs["price"] = kwargs.get("price", 25.0) * 0.5
            kwargs["name"] = kwargs.get("name", "Ticket") + " (Student)"
        elif product_type == "popcorn":
            kwargs["price"] = kwargs.get("price", 5.0) * 0.5
            kwargs["name"] = kwargs.get("name", "Popcorn") + " (Student)"
        elif product_type in ["candy", "nachos", "hotdog"]:
            kwargs["price"] = kwargs.get("price", 8.0) * 0.5
            kwargs["name"] = kwargs.get("name", product_type.title()) + " (Student)"
        elif product_type in ["soda", "juice", "water"]:
            kwargs["price"] = kwargs.get("price", 4.0) * 0.5
            kwargs["name"] = kwargs.get("name", product_type.title()) + " (Student)"
        standard_factory = StandardFactory()
        return standard_factory.create_product(product_type, **kwargs)

#-- Factory Concreta----------
class VIPFactory(AbstractFactory):
    def create_product(self, product_type: str, **kwargs):
        if product_type == "ticket":
            kwargs["price"] = kwargs.get("price", 25.0) * 1.5
            kwargs["name"] = kwargs.get("name", "Ticket") + " (VIP)"
        elif product_type == "popcorn":
            kwargs["price"] = kwargs.get("price", 5.0) * 0.5
            kwargs["name"] = kwargs.get("name", "Popcorn") + " (VIP Discount 50 %)"
        elif product_type in ["candy", "nachos", "hotdog"]:
            kwargs["price"] = kwargs.get("price", 8.0) * 0.5
            kwargs["name"] = kwargs.get("name", product_type.title()) + " (VIP Discount 50 %)"
        elif product_type in ["soda", "juice", "water"]:
            kwargs["price"] = kwargs.get("price", 4.0) * 0.5
            kwargs["name"] = kwargs.get("name", product_type.title()) + " (VIP Discount 50 %)"
        standard_factory = StandardFactory()
        return standard_factory.create_product(product_type, **kwargs)

#----Factory Method-------
def get_factory_for_user(user, ticket_type: str = None) -> AbstractFactory:
    if ticket_type:
        ticket_lower = ticket_type.lower()
        if ticket_lower == 'student':
            return StudentFactory()
        elif ticket_lower == 'vip':
            return VIPFactory()
    
    return StandardFactory()
