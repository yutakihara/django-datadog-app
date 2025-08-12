from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('metrics/', views.metrics, name='metrics'),
    path('api/test/', views.api_test, name='api_test'),
    path('health/', views.health_check, name='health_check'),
]
