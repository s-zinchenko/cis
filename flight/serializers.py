from rest_framework import serializers

from flight.models import Schedule, Aircraft, Route, Airport


class AircraftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = (
            "id",
            "name",
            "make_model",
        )


class AirportSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "iata_code",
        )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "departure_airport",
            "arrival_airport",
        )
        depth = 1

    departure_airport = AirportSerialzier()
    arrival_airport = AirportSerialzier()


class SchedulesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = (
            "id",
            "date",
            "time",
            "aircraft",
            "route",
            "flight_number",
            "economy_price",
            "confirmed",
            "business_price",
            "first_class_price",
        )

        depth = 1

    aircraft = AircraftSerializer()
    route = RouteSerializer()
    business_price = serializers.IntegerField(source="get_business_price")
    first_class_price = serializers.IntegerField(source="get_first_class_price")


class CancelFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = (
            "id",
            "confirmed",
        )


class ScheduleEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = (
            "date",
            "time",
            "economy_price",
        )


class UploadFileResSerilizer(serializers.Serializer):
    copies_count = serializers.IntegerField()
    updates_count = serializers.IntegerField()
    created_count = serializers.IntegerField()
    invalid_record_count = serializers.IntegerField()


class UploadFileSerilizer(serializers.Serializer):
    file = serializers.FileField(required=True)
