from django.db import models
from couriers.models import Courier


class Order(models.Model):
    order_id = models.IntegerField(primary_key=True)
    weight = models.FloatField(max_length=5)
    region = models.IntegerField()
    courier_id = models.ForeignKey(Courier, on_delete=models.CASCADE, null = True, blank = True)
    assign_time = models.DateTimeField(null = True, blank = True)
    complete_time = models.DateTimeField(null = True, blank = True)
    assigned = models.BooleanField(default=False, null = True, blank = True)

    def __str__(self):
        return str(self.order_id)


class DeliveryHour(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return str(self.start_time) + " - " + str(self.end_time)