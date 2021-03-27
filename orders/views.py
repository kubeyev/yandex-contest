from couriers.models import Courier
from .models import Order
from .serializers import OrderSerializer, AssignSerializer, CompleteSerializer

from django.shortcuts import get_object_or_404

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
            order_id_list = serializer.save()
            if order_id_list == True:
                responce_dic = {
                    "orders": order_id_list,
                    "assign_time": datetime.datetime.now().isoformat()
                }
            else:
                responce_dic = {
                    "orders": order_id_list
                }

            return Response(responce_dic, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CompleteList(APIView):
    def post(self, request):
        serializer = CompleteSerializer(data=request.data)
        try:
            courier = Courier.objects.get(
                courier_id=request.data['courier_id']
            )
            order = Order.objects.get(
                order_id=request.data['order_id']
            )
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST )

        if order in courier.order_set.all() and order.assign_time:
            if serializer.is_valid():
                if serializer.save():
                    return Response({"order_id": order.order_id}, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST )
        return Response(status=status.HTTP_400_BAD_REQUEST )