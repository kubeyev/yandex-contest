from django.urls import path
from .views import OrderList, AssignList, CompleteList

app_name = "order"

# app_name will help us do a reverse look-up latter.
urlpatterns = [
    path('', OrderList.as_view()),
    path('/assign', AssignList.as_view()),
    path('/complete', CompleteList.as_view()),
]