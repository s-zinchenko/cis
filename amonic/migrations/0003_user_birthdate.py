# Generated by Django 4.1.1 on 2022-09-19 18:22

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amonic', '0002_alter_userlog_logout_date_alter_userlog_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='birthdate',
            field=models.DateField(default=datetime.datetime(2022, 9, 19, 18, 22, 46, 74165, tzinfo=datetime.timezone.utc), verbose_name='Дата рождения'),
        ),
    ]