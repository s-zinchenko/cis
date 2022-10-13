from django.db import models


class Airport(models.Model):
    class Meta:
        verbose_name = "Аэропорт"
        verbose_name_plural = "Аэропорты"

    name = models.CharField(max_length=512, verbose_name="Название аэропорта")
    country = models.ForeignKey("amonic.Country", on_delete=models.CASCADE, verbose_name="Страна")
    iata_code = models.CharField(max_length=3, verbose_name="Код аэропорта ИАТА")


class Route(models.Model):
    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"

    distance = models.IntegerField(verbose_name="Дистанция полёта")
    flight_time = models.IntegerField(verbose_name="Время полёта", default=0)
    departure_airport = models.ForeignKey("flight.Airport", verbose_name="Аэропорт вылета", on_delete=models.CASCADE, related_name="departure")
    arrival_airport = models.ForeignKey("flight.Airport", verbose_name="Аэропорт назначения", on_delete=models.CASCADE, related_name="arrival")


class Aircraft(models.Model):
    class Meta:
        verbose_name = "Самолёт"
        verbose_name_plural = "Самолёты"

    name = models.CharField(max_length=256,)
    make_model = models.CharField(max_length=256)
    total_seats = models.SmallIntegerField(verbose_name="Общее количество мест")
    economy_seats = models.SmallIntegerField(verbose_name="Количество мест в эконом-классе")
    business_seats = models.SmallIntegerField(verbose_name="Количество мест в бизнес-классе")


class Schedule(models.Model):
    class Meta:
        verbose_name = "График вылетов"
        verbose_name_plural = "Графики вылетов"

    date = models.DateField(verbose_name="Дата вылета")
    time = models.TimeField(verbose_name="Время вылета")
    aircraft = models.ForeignKey("flight.Aircraft", verbose_name="Самолёт", on_delete=models.CASCADE,)
    route = models.ForeignKey("flight.Route", verbose_name="Маршрут", on_delete=models.CASCADE,)
    flight_number = models.CharField(max_length=16, verbose_name="Номер рейса")
    economy_price = models.IntegerField(verbose_name="Цена билета в эконом-классе")
    confirmed = models.SmallIntegerField(default=False, verbose_name="Подтверждён?")

    @property
    def get_business_price(self):
        return self.economy_price * 1.35

    @property
    def get_first_class_price(self):
        return self.get_business_price * 1.30
