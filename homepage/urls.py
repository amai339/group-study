from django.urls import path,include
from . import views




urlpatterns = [
    path('introduction/',views.introduction),
    path('login/', views.log_in),
    path('logout/',views.log_out),
    path('register/',views.register),
    path('',views.homepage),
]