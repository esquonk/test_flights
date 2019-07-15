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

    duration = serializers.CharField()


class ItineraryResultSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='Itinerary.id')

    onward_trip = TripSerializer(source='Itinerary.onward_trip')
    return_trip = TripSerializer(source='Itinerary.return_trip')

    duration = serializers.CharField()
    price = serializers.DecimalField(max_digits=20, decimal_places=2)
    optimal_score = serializers.FloatField()


class ItinerarySerializer(serializers.Serializer):
    id = serializers.IntegerField()

    onward_trip = TripSerializer()
    return_trip = TripSerializer()


class ItineraryDiffSerializer(serializers.Serializer):
    itinerary_left = ItinerarySerializer()
    itinerary_right = ItinerarySerializer()
