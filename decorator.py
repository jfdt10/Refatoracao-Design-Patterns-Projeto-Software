from abc import ABC, abstractmethod
from products import FOOD, DRINK

# Decorator Base
class ProductDecorator(ABC):
    def __init__(self, product):
        self._product = product
        
    @property
    def price(self):
        return self._product.price
        
    @property
    def name(self):
        return self._product.name
    
    def purchase_product(self, user=None):
        return self._product.purchase_product(user)
    
    def cancel_purchase(self, user=None):
        return self._product.cancel_purchase(user)
        
    def calculate_food_price(self):
        if hasattr(self._product, 'calculate_food_price'):
            return self._product.calculate_food_price()
        return self.price
        
    def calculate_drink_price(self):
        if hasattr(self._product, 'calculate_drink_price'):
            return self._product.calculate_drink_price()
        return self.price
        
    def promotion(self, coupon=None):
        if hasattr(self._product, 'promotion'):
            return self._product.promotion(coupon)
        return False

# Decoradores concretos
class SpecialPackagingDecorator(ProductDecorator):
    def __init__(self, product):
        super().__init__(product)
        self._packaging_price = 5.0
        self.size_or_type = getattr(product, 'size_or_type', None)
        self.size = getattr(product, 'size', None)
    
    @property
    def price(self):
        return self._product.price + self._packaging_price
    
    @property
    def name(self):
        return f"{self._product.name} (Special Packaging)"
        
    def purchase_product(self, user=None):
        print(f"Adding special packaging for {self._product.name}")
        return self._product.purchase_product(user)

class ExtraItemDecorator(ProductDecorator):
    def __init__(self, product, extra_item, extra_price):
        super().__init__(product)
        self._extra_item = extra_item
        self._extra_price = extra_price
        self.size_or_type = getattr(product, 'size_or_type', None)
        self.size = getattr(product, 'size', None)
    
    @property
    def price(self):
        return self._product.price + self._extra_price
    
    @property
    def name(self):
        return f"{self._product.name} + {self._extra_item}"
        
    def purchase_product(self, user=None):
        print(f"Adicionando {self._extra_item} ao {self._product.name}")
        return self._product.purchase_product(user)

class GiftWrapDecorator(ProductDecorator):
    def __init__(self, product, message=""):
        super().__init__(product)
        self._gift_wrap_price = 3.0
        self._message = message
        self.size_or_type = getattr(product, 'size_or_type', None)
        self.size = getattr(product, 'size', None)
    
    @property
    def price(self):
        return self._product.price + self._gift_wrap_price
    
    @property
    def name(self):
        if self._message:
            return f"{self._product.name} (Gift Wrap: '{self._message}')"
        return f"{self._product.name} (Gift Wrap)"
        
    def purchase_product(self, user=None):
        print(f"Wrapping {self._product.name} to gift")
        return self._product.purchase_product(user)

# Função auxiliar para facilitar o uso dos decoradores
def decorate_product(product, decorations):
    decorated_product = product
    for decorator_class, args, kwargs in decorations:
        args = args or []
        kwargs = kwargs or {}
        decorated_product = decorator_class(decorated_product, *args, **kwargs)
    return decorated_product