from .models import Courier
from .serializers import CourierSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class CourierList(APIView):
    def post(self, request):
        try:
            couriers = request.data.get('data')
            serializer = CourierSerializer(data=couriers, many=True)
            couriers_id = []
            if serializer.is_valid():
                serializer.save()
                for courier in couriers:
                    couriers_id.append({"id": courier['courier_id']})
                return Response({"couriers": couriers_id}, status=status.HTTP_201_CREATED)
            for i in range(len(couriers)):
                if serializer.errors[i]:
                    couriers_id.append({"id": couriers[i]['courier_id']})
            return Response({"validation_error": {"couriers": couriers_id}}, status=status.HTTP_400_BAD_REQUEST, )
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CourierDetail(APIView):
    def get_object(self, pk):
        try:
            return Courier.objects.get(courier_id=pk)
        except Courier.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        # try:
        courier = self.get_object(pk)
        serializer = CourierSerializer(courier)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # except:
        #     return Response(status=status.HTTP_404_NOT_FOUND)


    def patch(self, request, pk):
        courier = self.get_object(pk)
        serializer = CourierSerializer(courier, data=request.data, partial=True)
        if not request.data.get('working_hours') and not request.data.get("regions") and not request.data.get("courier_id") and not request.data.get("courier_type"):
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