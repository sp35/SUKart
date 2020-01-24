from django.contrib import admin
from kart.models import User, DeliveryAgent, ShoppingUser, Company, Product, Order


admin.site.register([ User, DeliveryAgent, ShoppingUser, Company, Product, Order ])