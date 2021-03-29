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
        common_order_dic = {
            "order_id": 1,
            "weight": 2,
            "region": 3,
            "delivery_hours": 1
        }
        orders = request.data.get('data')
        serializer = OrderSerializer(data=orders, many=True)
        orders_id = []
        invalid_ids = []
        no_undescribed_field = False
        for order in orders:
            if set(order.keys()) != set(common_order_dic.keys()) \
            or order["order_id"] in [ord.order_id for ord in Order.objects.all()] \
            or not order["delivery_hours"] \
            or type(order.get("weight")) in [int, float] or type(order.get("delivery_hous"))!=list \
            or type(order.get("region"))!=int:
                no_undescribed_field = True
                invalid_ids.append({"id": order['order_id']})

        if not serializer.is_valid():
            for num in range(len(orders)):
                if serializer.errors[num] and not {"id": orders[num]['order_id']} in invalid_ids:
                    invalid_ids.append({"id": orders[num]['order_id']})

        if serializer.is_valid() and not no_undescribed_field:
            serializer.save()
            for order in orders:
                orders_id.append({"id": order['order_id']})
            return Response({"orders": orders_id}, status=status.HTTP_201_CREATED)

        return Response({"validation_error": {"orders": invalid_ids}}, status=status.HTTP_400_BAD_REQUEST, )


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
        courier = Courier.objects.get(
            courier_id=request.data['courier_id']
        )
        order = Order.objects.get(
            order_id=request.data['order_id']
        )

        if order in courier.order_set.all() and order.assign_time:
            if serializer.is_valid():
                if serializer.save():
                    return Response({"order_id": order.order_id}, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST )
        return Response(status=status.HTTP_400_BAD_REQUEST )