from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from sqlalchemy.orm import aliased, contains_eager

from fares.expr import return_trip, onward_trip
from fares.models import Itinerary, Trip, Flight
from fares.filters import TwoWayFilter, ItineraryOrderingFilter
from fares.serializers import ItinerarySerializer

from .models import db


class Pagination(LimitOffsetPagination):
    pass


class ListItineraries(ListAPIView):
    serializer_class = ItinerarySerializer
    pagination_class = Pagination
    filter_backends = (ItineraryOrderingFilter, TwoWayFilter,)
    ordering_fields = ('price', 'duration',)

    def get_queryset(self):
        onward_opts = contains_eager(Itinerary.onward_trip, alias=onward_trip) \
            .selectinload(Trip.flights)
        return_opts = contains_eager(Itinerary.return_trip, alias=return_trip) \
            .selectinload(Trip.flights)

        query = db.query(Itinerary) \
            .outerjoin(onward_trip, Itinerary.onward_trip) \
            .outerjoin(return_trip, Itinerary.return_trip) \
            .options(onward_opts.joinedload(Flight.source),
                     onward_opts.joinedload(Flight.destination),
                     onward_opts.joinedload(Flight.carrier),
                     return_opts.joinedload(Flight.source),
                     return_opts.joinedload(Flight.destination),
                     return_opts.joinedload(Flight.carrier),
                     )

        return query
