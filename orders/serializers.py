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
        courier = get_object_or_404(Courier, courier_id=current_courier_id)
        type = courier.courier_type
        courier_wieght = None
        if type == "foot":
            courier_wieght = 10
        elif type == "bike":
            courier_wieght = 15
        elif type == "car":
            courier_wieght = 50
        if courier_wieght is None:
            return False
        for order in orders:
            delivery_hours = order.deliveryhour_set.all()
            working_hours = courier.courierworkinghour_set.all()
            if order.weight < courier_wieght:
                for delivery_hour in delivery_hours:
                    for working_hour in working_hours:
                        time_is_common = working_hour.start_time >= delivery_hour.start_time and working_hour.start_time < delivery_hour.end_time or working_hour.end_time > delivery_hour.start_time and working_hour.end_time <= delivery_hour.end_time
                        if time_is_common:
                            courier_regions = CourierRegion.objects.filter(courier__courier_id=current_courier_id)
                            for region in courier_regions:
                                if region == order.region:
                                    order.courier_id = validated_data.get('courier_id')
                                    order.assigned = True
                                    order.assign_time = datetime.datetime.now().isoformat()
                                    order.save()
                                else:
                                    pass
        return True