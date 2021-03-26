from .models import Order
from .serializers import OrderSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


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
    pass


class CompleteList(APIView):
    pass