from .models import Order
from .serializers import OrderSerializer, AssignSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import datetime


class OrderList(APIView):
    def post(self, request):
        orders = request.data.get('data')
        serializer = OrderSerializer(data=orders, many=True)
        orders_id = []
        if serializer.is_valid():
            serializer.save()
            for courier in orders:
                orders_id.append({"id": courier['order_id']})
            return Response({"orders": orders_id}, status=status.HTTP_201_CREATED)
        for i in range(len(orders)):
            if serializer.errors[i]:
                orders_id.append({"id": orders[i]['order_id']})
        return Response({"validation_error": {"couriers": orders_id}}, status=status.HTTP_400_BAD_REQUEST, )


class AssignList(APIView):
    def post(self, request):
        serializer = AssignSerializer(data=request.data)
        current_courier_id = request.data.get("courier_id")
        if serializer.is_valid():
            serializer.save()
            orders = list(Order.objects.all().filter(assigned=True, courier_id=current_courier_id))
            order_id_list = []
            for order in orders:
                order_id_list.append(order.id)

            responce_dic = {
                "orders": order_id_list,
                "assign_time": datetime.datetime.now().isoformat()
            }

            return Response(responce_dic, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CompleteList(APIView):
    pass