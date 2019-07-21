from typing import List

from pytz import timezone
from rest_framework import serializers

from fares.models import Itinerary


class DurationField(serializers.IntegerField):
    def to_representation(self, value):
        return value.seconds // 60


class AirportSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    icao = serializers.CharField()
    name = serializers.CharField()


class AirlineSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    icao = serializers.CharField()
    name = serializers.CharField()


class FlightSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    source = serializers.CharField(source='source.iata')
    destination = serializers.CharField(source='destination.iata')

    carrier = serializers.CharField(source='carrier.iata')

    flight_number = serializers.CharField()

    departure = serializers.SerializerMethodField()
    arrival = serializers.SerializerMethodField()

    service_class = serializers.CharField()
    ticket_type = serializers.CharField()
    number_of_stops = serializers.IntegerField()
    fare_basis = serializers.CharField()

    def get_departure(self, obj):
        return obj.departure.astimezone(timezone(obj.source.tz))

    def get_arrival(self, obj):
        return obj.arrival.astimezone(timezone(obj.destination.tz))


class TripSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    flights = FlightSerializer(many=True)

    duration = DurationField()


class ItineraryResultSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='Itinerary.id')

    onward_trip = TripSerializer(source='Itinerary.onward_trip')
    return_trip = TripSerializer(source='Itinerary.return_trip')

    duration = DurationField()
    price = serializers.DecimalField(max_digits=20, decimal_places=2)
    optimal_score = serializers.FloatField()


class ItinerarySerializer(serializers.Serializer):
    id = serializers.IntegerField()

    onward_trip = TripSerializer()
    return_trip = TripSerializer()


def service_classes(itinerary: Itinerary) -> List[str]:
    return [f.service_class for f in itinerary.onward_trip.flights]


class ItineraryDiffSerializer(serializers.Serializer):
    itinerary_left = ItinerarySerializer()
    itinerary_right = ItinerarySerializer()

    fingerprint = serializers.CharField()

    changed_fields = serializers.SerializerMethodField()

    def get_changed_fields(self, obj):
        if obj.itinerary_left is None or obj.itinerary_right is None:
            return None

        fields = []
        if obj.itinerary_left.onward_trip.duration != obj.itinerary_right.onward_trip.duration:
            fields.append('duration')

        if service_classes(obj.itinerary_left) != service_classes(obj.itinerary_right):
            fields.append('service_class')

        return fields


class ItineraryCompareSerializer(serializers.Serializer):
    itinerary_left = ItineraryResultSerializer()
    itinerary_right = ItineraryResultSerializer()


class RoutesCompareSerializer(serializers.Serializer):
    only_left = serializers.ListSerializer(child=serializers.ListSerializer(child=serializers.ListSerializer(
        child=serializers.CharField()
    )))
    only_right = serializers.ListSerializer(child=serializers.ListSerializer(child=serializers.ListSerializer(
        child=serializers.CharField()
    )))
    both = serializers.ListSerializer(child=serializers.ListSerializer(child=serializers.ListSerializer(
        child=serializers.CharField()
    )))


class RequestCompareSerializer(serializers.Serializer):
    cheapest = ItineraryCompareSerializer()
    fastest = ItineraryCompareSerializer()
    optimal = ItineraryCompareSerializer()
    routes = RoutesCompareSerializer()
