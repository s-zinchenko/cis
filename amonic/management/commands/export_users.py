import csv

from django.contrib.auth.hashers import make_password
from django.core.management import BaseCommand

from amonic.models import User, Role, Office


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        with open("data/UserData.csv") as f:
            reader = csv.DictReader(f)
            # for row in reader: print(row)
            User.objects.bulk_create(
                [
                    User(
                        email=row["email"],
                        first_name=row["first_name"],
                        last_name=row["last_name"],
                        is_active=True if row["is_active"] == 1 else False,
                        role_id=Role.objects.get(title=row["role"]).id,
                        office_id=Office.objects.get(title=row["office"]).id,
                        birthdate=row["birthdate"],
                        password=make_password(row["password"]),
                    ) for row in reader
                ]
            )

