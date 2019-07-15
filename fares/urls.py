from django.urls import path
from . import views

urlpatterns = [
    path('itineraries/', views.ListItineraries.as_view()),
    path('diff/', views.ListItineraryDiff.as_view()),
]
