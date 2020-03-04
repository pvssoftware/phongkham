from django.conf import settings




class Cart:

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
    
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
    
    def choose(self,license,money,order_desc):
        self.cart = {}
        self.cart["license"] = license
        self.cart["money"] = money
        self.cart["order_desc"] = order_desc
        self.save()

    def add_email(self,email):
        self.cart["email"] = email
        self.save()
    
    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified  = True

    def clear(self):
        self.cart = {}
        self.save()

    