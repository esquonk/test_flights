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

        two_way = TwoWayFilter.get_value(request)
        duration_expr = onward_trip.duration + return_trip.duration \
            if two_way else onward_trip.duration

        if ordering:
            for field in ordering:
                if field == 'price':
                    queryset = queryset.order_by(Itinerary.price())
                elif field == '-price':
                    queryset = queryset.order_by(Itinerary.price().desc())
                elif field == 'duration':
                    queryset = queryset.order_by(duration_expr)
                elif field == '-duration':
                    queryset = queryset.order_by(duration_expr.desc())

        return queryset
