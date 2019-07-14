from pytz import timezone
from rest_framework import serializers


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

    source = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()

    carrier = serializers.SerializerMethodField()

    flight_number = serializers.CharField()

    departure = serializers.SerializerMethodField()
    arrival = serializers.SerializerMethodField()

    service_class = serializers.CharField()
    ticket_type = serializers.CharField()
    number_of_stops = serializers.IntegerField()
    fare_basis = serializers.CharField()

    def get_source(self, obj):
        return obj.source.iata

    def get_destination(self, obj):
        return obj.destination.iata

    def get_carrier(self, obj):
        return obj.carrier.iata

    def get_departure(self, obj):
        return obj.departure.astimezone(timezone(obj.source.tz))

    def get_arrival(self, obj):
        return obj.departure.astimezone(timezone(obj.destination.tz))


class TripSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    flights = FlightSerializer(many=True)

    duration = serializers.CharField()


class ItinerarySerializer(serializers.Serializer):
    id = serializers.IntegerField()

    onward_trip = TripSerializer()
    return_trip = TripSerializer()
