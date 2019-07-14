from django.conf import settings
from django.urls import path, include
from rest_framework import routers

urlpatterns = [
    path('api/fares/', include('fares.urls'))
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls))
                  ] + urlpatterns
