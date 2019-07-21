from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from sqlalchemy import select, func, extract
from sqlalchemy.orm import aliased, contains_eager, joinedload
from sqlalchemy.sql.functions import coalesce

from fares.expr import return_trip, onward_trip
from fares.filters import TwoWayFilter, ItineraryOrderingFilter, AirportFilter
from fares.models import Itinerary, Trip, Flight
from fares.serializers import ItineraryResultSerializer, ItineraryDiffSerializer, RequestCompareSerializer
from .models import db


class Pagination(LimitOffsetPagination):
    max_limit = 1000
    default_limit = 10


class ListItineraries(ListAPIView):
    serializer_class = ItineraryResultSerializer
    pagination_class = Pagination
    filter_backends = (TwoWayFilter, AirportFilter)
    ordering_fields = ('price', 'duration', 'optimal_score')

    def get_queryset(self):
        query = db.query(Itinerary,
                         self.get_duration_expr().label('duration'),
                         Itinerary.price().label('price')) \
            .outerjoin(onward_trip, Itinerary.onward_trip) \
            .outerjoin(return_trip, Itinerary.return_trip) \
            .options(contains_eager(Itinerary.onward_trip, alias=onward_trip).selectinload(Trip.flights),
                     contains_eager(Itinerary.return_trip, alias=return_trip).selectinload(Trip.flights)
                     )

        return query

    def get_duration_expr(self):
        two_way = TwoWayFilter.get_value(self.request)
        return onward_trip.duration + return_trip.duration \
            if two_way else onward_trip.duration

    def get_optimal_score_expr(self, queryset):
        min_price = select([func.min(aliased(queryset.selectable).c.price)]).as_scalar()
        min_duration = select([func.min(aliased(queryset.selectable).c.duration)]).as_scalar()

        return (
                (Itinerary.price() / min_price)
                * (extract('epoch', self.get_duration_expr()) / extract('epoch', min_duration))
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = queryset.add_column(
            self.get_optimal_score_expr(queryset).label('optimal_score')
        )

        queryset = ItineraryOrderingFilter().filter_queryset(self.request, queryset, self)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ListItineraryDiff(ListAPIView):
    serializer_class = ItineraryDiffSerializer
    pagination_class = Pagination

    def init_params(self, request):
        errors = {}

        try:
            self.left_id = int(request.query_params.get('left_request_id'))
        except (ValueError, TypeError):
            errors['left_request_id'] = 'must be an integer'

        try:
            self.right_id = int(request.query_params.get('right_request_id'))
        except (ValueError, TypeError):
            errors['right_request_id'] = 'must be an integer'

        if errors:
            raise ValidationError(errors)

    def get(self, request, *args, **kwargs):
        self.init_params(request)

        return super().get(request, *args, **kwargs)

    def itinerary_ids_query(self, left_request_id: int, right_request_id: int):
        flight_fingerprint = select(
            [Flight.trip_id,
             func.concat(Flight.carrier_id, '_',
                         Flight.flight_number, '_').label('flight_fingerprint')]) \
            .order_by(Flight.order) \
            .alias("flight_fingerprint")

        itinerary_fingerprint = db.query(Itinerary.id.label('id'),
                                         func.string_agg(flight_fingerprint.c.flight_fingerprint, '|').label(
                                             'fingerprint')) \
            .select_from(Itinerary) \
            .group_by(Itinerary.id) \
            .join(flight_fingerprint, flight_fingerprint.c.trip_id == Itinerary.onward_trip_id)

        request_1 = itinerary_fingerprint.filter(Itinerary.request_id == left_request_id).selectable.alias('left')
        request_2 = itinerary_fingerprint.filter(Itinerary.request_id == right_request_id).selectable.alias('right')

        result = db.query(request_1.c.id.label('left_id'),
                          request_2.c.id.label('right_id'),
                          coalesce(request_1.c.fingerprint,
                                   request_2.c.fingerprint).label('fingerprint')
                          ) \
            .select_from(request_1) \
            .join(request_2, request_2.c.fingerprint == request_1.c.fingerprint, full=True)

        return result

    def get_queryset(self):

        ids = self.itinerary_ids_query(self.left_id, self.right_id) \
            .selectable.alias('ids')

        i_left = aliased(Itinerary, name='itinerary_left')
        i_right = aliased(Itinerary, name='itinerary_right')

        query = db.query(ids.c.fingerprint,
                         i_left,
                         i_right,
                         ) \
            .select_from(ids) \
            .outerjoin(i_left, i_left.id == ids.c.left_id) \
            .outerjoin(i_right, i_right.id == ids.c.right_id) \
            .options(joinedload(i_left.onward_trip).selectinload(Trip.flights),
                     joinedload(i_left.return_trip).selectinload(Trip.flights),
                     joinedload(i_right.onward_trip).selectinload(Trip.flights),
                     joinedload(i_right.return_trip).selectinload(Trip.flights))

        return query


class CompareRequests(APIView):
    serializer_class = RequestCompareSerializer

    def init_params(self, request):
        errors = {}

        try:
            self.left_id = int(request.query_params.get('left_request_id'))
        except (ValueError, TypeError):
            errors['left_request_id'] = 'must be an integer'

        try:
            self.right_id = int(request.query_params.get('right_request_id'))
        except (ValueError, TypeError):
            errors['right_request_id'] = 'must be an integer'

        if errors:
            raise ValidationError(errors)

    def get_optimal_score_expr(self, queryset):
        min_price = select([func.min(aliased(queryset.selectable).c.price)]).as_scalar()
        min_duration = select([func.min(aliased(queryset.selectable).c.duration)]).as_scalar()

        return (
                (Itinerary.price() / min_price)
                * (extract('epoch', onward_trip.duration) / extract('epoch', min_duration))
        )

    def get_query(self, request_id):
        query = db.query(Itinerary,
                         onward_trip.duration.label('duration'),
                         Itinerary.price().label('price')) \
            .filter(Itinerary.request_id == request_id) \
            .outerjoin(onward_trip, Itinerary.onward_trip) \
            .outerjoin(return_trip, Itinerary.return_trip) \
            .options(contains_eager(Itinerary.onward_trip, alias=onward_trip).selectinload(Trip.flights),
                     contains_eager(Itinerary.return_trip, alias=return_trip).selectinload(Trip.flights)
                     )

        query = query.add_column(
            self.get_optimal_score_expr(query).label('optimal_score')
        )

        return query

    def get(self, request):
        self.init_params(request)

        left_query = self.get_query(self.left_id)
        right_query = self.get_query(self.right_id)

        result = {
            'fastest': self.compare(
                left_query.order_by(left_query.statement.c.duration).first(),
                right_query.order_by(left_query.statement.c.duration).first()
            ),

            'cheapest': self.compare(
                left_query.order_by(left_query.statement.c.price).first(),
                right_query.order_by(left_query.statement.c.price).first(),
            ),

            'optimal': self.compare(
                left_query.order_by(left_query.statement.c.optimal_score).first(),
                right_query.order_by(left_query.statement.c.optimal_score).first(),
            )
        }

        data = self.serializer_class(result).data

        return Response(data)

    def compare(self, obj_left, obj_right):
        return {
            'itinerary_left': obj_left,
            'itinerary_right': obj_right,
        }
