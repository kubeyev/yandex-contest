from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from .models import Order, DeliveryHour
from couriers.models import Courier, CourierWorkingHour, CourierRegion

import datetime


class OrderSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    weight = serializers.FloatField()
    region = serializers.IntegerField()
    delivery_hours = serializers.ListField(
        child=serializers.CharField()
    )

    def create(self, validated_data):
        order, _ = Order.objects.get_or_create(
            order_id=validated_data['order_id'],
            weight=validated_data['weight'],
            region=validated_data['region'],
        )
        order.save()
        for delivery_hour in validated_data['delivery_hours']:
            start_time_list = delivery_hour.split('-')[0].split(':')
            start_time = datetime.time(int(start_time_list[0]), int(start_time_list[1]))

            end_time_list = delivery_hour.split('-')[1].split(':')
            end_time = datetime.time(int(end_time_list[0]), int(end_time_list[1]))

            order.deliveryhour_set.get_or_create(start_time=start_time, end_time=end_time)
            order.save()
        return True

    def update(self, instance, validated_data):
        instance.order_id = validated_data.get('courier_id', instance.courier_id)
        instance.weight = validated_data.get('weight', instance.weight)
        instance.region = validated_data.get('region', instance.region)
        if validated_data.get('delivery_hour'):
            instance.deliveryhour_set.all().delete()
            for delivery_hour in validated_data['delivery_hours']:
                start_time_list = delivery_hour.split('-')[0].split(':')
                start_time = datetime.time(int(start_time_list[0]), int(start_time_list[1]))

                end_time_list = delivery_hour.split('-')[1].split(':')
                end_time = datetime.time(int(end_time_list[0]), int(end_time_list[1]))

                instance.deliveryhour_set.get_or_create(start_time=start_time, end_time=end_time)
        instance.save()
        return instance


class AssignSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField()

    def create(self, validated_data):
        orders = Order.objects.all().filter(assigned=False).order_by("weight")
        current_courier_id = validated_data.get('courier_id')
        courier = Courier.objects.get(
            courier_id=current_courier_id
        )
        type = courier.courier_type
        courier_max_wieght = 0
        orders_sum_weight = 0
        if type == "foot":
            courier_max_wieght = 10
        elif type == "bike":
            courier_max_wieght = 15
        elif type == "car":
            courier_max_wieght = 50
        if courier_max_wieght == 0:
            return False

        output_orders_id = []

        for order in orders:
            delivery_hours = order.deliveryhour_set.all()
            working_hours = courier.courierworkinghour_set.all()
            region_check = order.region in [region.region for region in courier.regions.all()]
            if region_check:
                for delivery_hour in delivery_hours:
                    for working_hour in working_hours:
                        time_check = working_hour.start_time >= delivery_hour.start_time and working_hour.start_time < delivery_hour.end_time or working_hour.end_time > delivery_hour.start_time and working_hour.end_time < delivery_hour.end_time
                        if time_check:
                            courier.order_set.add(order)
                            order.assigned = True
                            order.assign_time = datetime.datetime.now().isoformat()
                            order.save()
                            output_orders_id.append({"id": order.order_id})

            if orders_sum_weight > courier_max_wieght:
                courier.order_set.remove({"id": order.order_id})
                orders_sum_weight -= order.weight
                order.assign_time = None
                order.assigned = False
                output_orders_id.remove(order.order_id)

                break
        courier.save()
        return output_orders_id


class CompleteSerializer(serializers.Serializer):
    courier_id = serializers.IntegerField()
    order_id = serializers.IntegerField()
    complete_time = serializers.DateTimeField()

    def create(self, validated_data):
        courier = Courier.objects.get(courier_id=validated_data.get("courier_id"))
        order = Order.objects.get(order_id=validated_data.get("order_id"))
        order.complete_time = validated_data.get("complete_time")
        order.save()
        return True