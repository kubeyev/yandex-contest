from django.urls import path
from .views import CourierList, CourierDetail

app_name = "courier"

urlpatterns = [
    path('', CourierList.as_view()),
    path('/<int:pk>', CourierDetail.as_view()),
]