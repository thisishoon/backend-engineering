from django.urls import path
from . import views


urlpatterns = [
    path('', views.ManagerView.as_view()),
    path('<slug:pk>', views.ManagerView.as_view())
]