from django.urls import path
from . import views


urlpatterns = [
    path('', views.ManagerView.as_view()),
]