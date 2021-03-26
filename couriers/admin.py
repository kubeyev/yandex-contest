from django.contrib import admin
from .models import Courier, CourierRegion, CourierWorkingHour

admin.site.register(Courier)
admin.site.register(CourierRegion)
admin.site.register(CourierWorkingHour)