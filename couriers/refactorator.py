from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from .models import Courier, CourierRegion, CourierWorkingHour
import datetime

def creation_of_working_hours(hours, courier):
    for working_hour in hours:
        start_time_list = working_hour.split('-')[0].split(':')
        start_time = datetime.time(int(start_time_list[0]), int(start_time_list[1]))

        end_time_list = working_hour.split('-')[1].split(':')
        end_time = datetime.time(int(end_time_list[0]), int(end_time_list[1]))

        courier.courierworkinghour_set.get_or_create(start_time=start_time, end_time=end_time)
        courier.save()

def creation_of_regions(regions, courier):
    for region in regions:
        courier_region, _ = CourierRegion.objects.get_or_create(
            region=region,
        )
        courier.regions.add(courier_region)

def coeficient(type):
    if type == "foot":
        coeficient = 2
    elif type == "bike":
        coeficient = 5
    elif type == "car":
        coeficient = 9
    else:
        return False
    return coeficient