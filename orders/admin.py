from django.contrib import admin
from .models import Order, DeliveryHour

admin.site.register(Order)
admin.site.register(DeliveryHour)