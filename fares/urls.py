from django.urls import path
from . import views

urlpatterns = [
    path('itineraries/', views.ListItineraries.as_view()),
]
