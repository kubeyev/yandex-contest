from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from .models import Courier, CourierRegion, CourierWorkingHour
from orders.models import Order
from couriers.refactorator import creation_of_working_hours, creation_of_regions
import datetime


class CourierSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField()
    courier_type = serializers.CharField()
    regions = serializers.ListField(
        child=serializers.IntegerField()
    )
    working_hours = serializers.ListField(
        child=serializers.CharField()
    )

    def create(self, validated_data):
        courier, _ = Courier.objects.get_or_create(
            courier_id=validated_data['courier_id'],
            courier_type=validated_data['courier_type'],
        )
        courier.save()

        creation_of_regions(validated_data['regions'], courier)
        creation_of_working_hours(validated_data['working_hours'], courier)

        return True

    def update(self, instance, validated_data):
        instance.courier_id = validated_data.get('courier_id', instance.courier_id)
        instance.courier_type = validated_data.get('courier_type', instance.courier_type)
        if 'regions' in validated_data.keys():
            instance.regions.clear()
            instance.save()
            for region in validated_data['regions']:
                courier_region, _ = CourierRegion.objects.get_or_create(
                    region=region,
                )
                instance.regions.add(courier_region)
        if 'working_hours' in validated_data.keys():
            instance.courierworkinghour_set.all().delete()
            for working_hour in validated_data['working_hours']:
                start_time_list = working_hour.split('-')[0].split(':')
                start_time = datetime.time(int(start_time_list[0]), int(start_time_list[1]))

                end_time_list = working_hour.split('-')[1].split(':')
                end_time = datetime.time(int(end_time_list[0]), int(end_time_list[1]))

                instance.courierworkinghour_set.get_or_create(start_time=start_time, end_time=end_time)
        instance.save()

        courier = Courier.objects.get(courier_id=instance.courier_id)
        courier_orders = Order.objects.all().filter(courier_id=instance.courier_id,assigned=True)
        courier_max_wieght = 0
        orders_sum_weight = 0

        if type == "foot":
            courier_max_wieght = 10
        elif type == "bike":
            courier_max_wieght = 15
        elif type == "car":
            courier_max_wieght = 50
        for order in courier.order_set.order_by('-weight'):
            orders_sum_weight += order.weight

        for order in courier.order_set.order_by('-weight'):
            region_is_common = order.region in [region.region for region in courier.regions.all()]
            if not order.complete_time and not region_is_common:
                courier.order_set.remove(order)
                courier.save()
                continue
            for working_hour in courier.courierworkinghour_set.all():
                for delivery_hour in order.deliveryhour_set.all():
                    time_is_common = working_hour.start_time >= delivery_hour.start_time and working_hour.start_time < delivery_hour.end_time or working_hour.end_time > delivery_hour.start_time and working_hour.end_time <= delivery_hour.end_time
                    if not time_is_common:
                        courier.order_set.remove(order)
                        order.update(assign_time=None, assigned=False)
                        order.save()
                        courier.save()
                        continue

            orders_sum_weight += order.weight

        while orders_sum_weight > orders_sum_weight:
            order_max = courier.order_set.order_by('-weight')[0]
            orders_sum_weight -= order_max.weight
            courier.order_set.remove(order_max)
            order.update(assign_time=None, assigned=False)
            order.save()
            courier.save()

        courier.save()
        return courier