from .serializers import CourierSerializer
from .models import Courier
from orders.models import Order
from couriers.refactorator import coeficient

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class CourierList(APIView):
    def post(self, request):
        couriers_id = []
        invalid_ids = []
        no_undescribed_field = False
        courier_basic_dic = {
            "courier_id": 1,
            "courier_type": "",
            "regions": [],
            "working_hours": []
        }
        for courier in request.data.get('data'):
            if set(courier.keys()) != set(courier_basic_dic.keys()) \
            or not courier['courier_type'] in ['bike', 'foot'] \
            or courier['courier_id'] in [courier.courier_id for courier in Courier.objects.all()]:
                no_undescribed_field = True
                invalid_ids.append({"id": courier['couriers_id']})


        couriers = request.data.get('data')
        serializer = CourierSerializer(data=couriers, many = True)

        if not serializer.is_valid():
            for num in range(len(couriers)):
                if serializer.errors[num] and not {"id": couriers[num]['courier_id']} in invalid_ids:
                    invalid_ids.append({"id": couriers[num]['courier_id']})
        if serializer.is_valid() and not no_undescribed_field:
            serializer.save()
            for courier in couriers:
                couriers_id.append({"id": courier['courier_id']})
            return Response({"couriers": couriers_id}, status=status.HTTP_201_CREATED)

        return Response({"validation_error": {"couriers": invalid_ids}},status=status.HTTP_400_BAD_REQUEST)


class CourierDetail(APIView):
    def get_object(self, pk):
        try:
            return Courier.objects.get(courier_id=pk)
        except Courier.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        courier = self.get_object(pk)
        regions = [region.region for region in courier.regions.all()]
        working_hours = [
            str(working_hour.start_time.strftime("%H:%M")) + "-" + str(working_hour.end_time.strftime("%H:%M"))
            for working_hour in courier.courierworkinghour_set.all()]
        average_time_for_region = []
        sum_earning = []
        sum_time = 0
        courier_coeficient = coeficient(courier.courier_type)

        for region in regions:
            orders = Order.objects.all().filter(region=region, courier_id=pk)
            if orders:
                for order in orders:
                    time_difference_for_one_order_done_by_courier = order.complete_time - order.assign_time
                    sum_time += time_difference_for_one_order_done_by_courier

                    sum_earning.append(500*courier_coeficient)

                average_time_for_region.append(sum_time.seconds / len(orders))

            else:
                responce_dic = {
                    "courier_id": courier.courier_id,
                    "courier_type": courier.courier_type,
                    "regions": regions,
                    "working_hours": working_hours
                }
                return Response(responce_dic, status=status.HTTP_200_OK)

        time = min(average_time_for_region)
        rating = (60 * 60 - min(time, 60 * 60)) / (60 * 60) * 5
        earnings = sum(sum_earning)

        responce_dic = {
            "courier_id": courier.courier_id,
            "courier_type": courier.courier_type,
            "regions": regions,
            "working_hours": working_hours,
            "rating": rating,
            "earnings": courier.earnings
        }
        courier.rating = rating
        courier.earnings = earnings
        courier.save()
        return Response(responce_dic, status=status.HTTP_200_OK)


    def patch(self, request, pk):
        courier = self.get_object(pk)
        serializer = CourierSerializer(courier, data=request.data, partial=True)
        courier_basic_dic = {
            "courier_id": 1,
            "courier_type": "",
            "regions": [],
            "working_hours": []
        }
        if not request.data.get('working_hours') and not request.data.get("regions") and not request.data.get("courier_id") and not request.data.get("courier_type"):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('courier_type'):
            if not request.data.get('courier_type') in ["foot", "bike", "car"]:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            regions = [region.region for region in courier.regions.all()]
            working_hours = [
                str(working_hour.start_time.strftime("%H:%M")) + "-" + str(working_hour.end_time.strftime("%H:%M"))
                for working_hour in courier.courierworkinghour_set.all()]
            courier_dic = {
                "courier_id": courier.courier_id,
                "courier_type": courier.courier_type,
                "regions": regions,
                "working_hours": working_hours
            }

            return Response(courier_dic)
        return Response(status=status.HTTP_400_BAD_REQUEST)