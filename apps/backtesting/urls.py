from django.urls import path

from . import views

app_name = "backtesting"

urlpatterns = [
    path("", views.index, name="index"),
]
