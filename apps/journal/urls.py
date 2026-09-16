from django.urls import path

from . import views

app_name = "journal"

urlpatterns = [
    path("", views.index, name="index"),
    path("trades/add/", views.add_trade, name="add_trade"),
]
