from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from .models import Courier, CourierRegion, CourierWorkingHour
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
        print("validated data: " + str(validated_data))
        courier, _ = Courier.objects.get_or_create(
            courier_id=validated_data['courier_id'],
            courier_type=validated_data['courier_type'],
        )
        courier.save()
        for region in validated_data['regions']:
            courier_region, _ = CourierRegion.objects.get_or_create(
                region=region,
            )
            courier.regions.add(courier_region)
        for working_hour in validated_data['working_hours']:
            start_time_list = working_hour.split('-')[0].split(':')
            start_time = datetime.time(int(start_time_list[0]), int(start_time_list[1]))

            end_time_list = working_hour.split('-')[1].split(':')
            end_time = datetime.time(int(end_time_list[0]), int(end_time_list[1]))

            courier.courierworkinghour_set.get_or_create(start_time=start_time, end_time=end_time)
            courier.save()
        return True

    def update(self, instance, validated_data):
        instance.courier_id = validated_data.get('courier_id', instance.courier_id)
        instance.courier_type = validated_data.get('courier_type', instance.courier_type)
        if validated_data.get('regions'):
            instance.regions.clear()
            instance.save()
            for region in validated_data['regions']:
                courier_region, _ = CourierRegion.objects.get_or_create(
                    region=region,
                )
                instance.regions.add(courier_region)
        if validated_data.get('working_hours'):
            instance.courierworkinghour_set.all().delete()
            for working_hour in validated_data['working_hours']:
                start_time_list = working_hour.split('-')[0].split(':')
                start_time = datetime.time(int(start_time_list[0]), int(start_time_list[1]))

                end_time_list = working_hour.split('-')[1].split(':')
                end_time = datetime.time(int(end_time_list[0]), int(end_time_list[1]))

                instance.courierworkinghour_set.get_or_create(start_time=start_time, end_time=end_time)
        instance.save()
        return instance