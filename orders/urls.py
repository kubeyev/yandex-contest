from django.urls import path
from .views import OrderList

app_name = "order"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('', OrderList.as_view()),
    path('assign', OrderList.as_view())
]