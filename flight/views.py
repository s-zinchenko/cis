import codecs
import csv
import datetime
from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.generics import ListAPIView, UpdateAPIView, GenericAPIView
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from flight.models import Schedule, Airport, Route, Aircraft
from flight.serializers import SchedulesListSerializer, CancelFlightSerializer, AirportSerialzier, UploadFileSerilizer, \
    UploadFileResSerilizer, ScheduleEditSerializer
from utils.common import to_int


class SchedulesListView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Schedule.objects.all().order_by("date", "time")
    serializer_class = SchedulesListSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['date', 'time', 'economy_price', 'confirmed']
    filterset_fields = ["route__departure_airport__iata_code", "route__arrival_airport__iata_code", "flight_number", "date"]


class CancelFlightView(UpdateAPIView):
    permission_classes = [AllowAny]
    queryset = Schedule.objects.all()
    serializer_class = CancelFlightSerializer


class AirportListView(ListAPIView):
    queryset = Airport.objects.all()
    serializer_class = AirportSerialzier


class ScheduleEditView(UpdateAPIView):
    permission_classes = [AllowAny]
    queryset = Schedule.objects.all()
    serializer_class = ScheduleEditSerializer


class UploadFileView(GenericAPIView):
    permission_classes = [AllowAny,]
    serializer_class = UploadFileSerilizer
    parser_classes = [FileUploadParser]

    def validate_fileds(self, row: dict):
        for key in row.keys():
            if not row[key]:
                return False
        regex = datetime.datetime.strptime
        try:
            regex(row["date"], "%Y-%m-%d")
            regex(row["time"], "%H:%M")
        except ValueError:
            return False
        return True

    def is_valid_fields(self, row) -> bool:
        return self.validate_fileds(row)

    def process_file(self, file) -> dict[str, Any]:
        reader = csv.DictReader(codecs.iterdecode(file, 'utf-8'))
        reader.fieldnames = [
            "action",
            "date",
            "time",
            "flight_number",
            "departure_airport",
            "arrival_airport",
            "aircraft",
            "economy_price",
            "confirmed",
        ]
        add_schedules_obj = []
        added_flight_numbers = []
        added_date = []
        copies_count = 0
        updates_count = 0
        invalid_record_count = -3
        last_id = Schedule.objects.last().id + 1
        for row in reader:
            if not self.is_valid_fields(row):
                invalid_record_count += 1
                continue
            # if row["flight_number"] in added_flight_numbers and row["date"] in added_date:
            if Schedule.objects.filter(flight_number=row["flight_number"], date=row["date"]).exists():
                copies_count += 1
                continue
            if row["action"] == "ADD":
                added_flight_numbers.append(row["flight_number"])
                added_date.append(row["date"])
                try:
                    add_schedules_obj.append(
                        Schedule(
                            id=last_id,
                            date=row["date"],
                            time=row["time"],
                            flight_number=row["flight_number"],
                            route=Route.objects.get(
                                arrival_airport__iata_code=row["arrival_airport"],
                                departure_airport__iata_code=row["departure_airport"]
                            ),
                            aircraft=Aircraft.objects.get(pk=int(row["aircraft"])),
                            economy_price=to_int(row["economy_price"]),
                            confirmed=1 if row["confirmed"] == "OK" else 0,
                        )
                    )
                    last_id +=1
                except Exception:
                    invalid_record_count += 1
            if row["action"] == "EDIT":
                try:
                    Schedule.objects.filter(
                        flight_number=row["flight_number"],
                        date=row["date"]
                    ).update(
                        date=row["date"],
                        time=row["time"],
                        flight_number=row["flight_number"],
                        route=Route.objects.get(
                            arrival_airport__iata_code=row["arrival_airport"],
                            departure_airport__iata_code=row["departure_airport"]
                        ),
                        aircraft=Aircraft.objects.get(pk=int(row["aircraft"])),
                        economy_price=to_int(row["economy_price"]),
                        confirmed=1 if row["confirmed"] == "OK" else 0,
                    )
                    updates_count += 1
                except Exception:
                    invalid_record_count += 1

        created_count = Schedule.objects.bulk_create(add_schedules_obj)
        return {
            "copies_count": copies_count,
            "updates_count": updates_count,
            "created_count": len(created_count),
            "invalid_record_count": invalid_record_count,
        }

    @swagger_auto_schema(request_body=UploadFileSerilizer(), responses={200: UploadFileResSerilizer()})
    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES["file"]
        res = self.process_file(uploaded_file)
        return Response(res)
