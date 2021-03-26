from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from .models import Order, DeliveryHour
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