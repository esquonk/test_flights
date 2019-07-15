from rest_framework.filters import BaseFilterBackend, OrderingFilter

from fares.expr import onward_trip, return_trip
from fares.models import Itinerary


class TwoWayFilter(BaseFilterBackend):

    @staticmethod
    def get_value(request):
        two_way = request.query_params.get('two_way')

        if two_way is None:
            return None
        else:
            return two_way.lower() in ['1', 'true']

    def filter_queryset(self, request, queryset, view):
        two_way = TwoWayFilter.get_value(request)
        if two_way is None:
            pass
        elif two_way:
            queryset = queryset.filter(Itinerary.return_trip_id != None)
        else:
            queryset = queryset.filter(Itinerary.return_trip_id == None)

        return queryset


class ItineraryOrderingFilter(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            for field in ordering:
                expr = getattr(queryset.statement.c, field.lstrip('-'))
                if field.startswith('-'):
                    expr = expr.desc()
                queryset = queryset.order_by(expr)

        return queryset


class AirportFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        source = request.query_params.get('source')
        destination = request.query_params.get('destination')


        if source:
            queryset = queryset.filter(onward_trip.source_iata == source)

        if destination:
            queryset = queryset.filter(onward_trip.destination_iata == destination)

        return queryset
