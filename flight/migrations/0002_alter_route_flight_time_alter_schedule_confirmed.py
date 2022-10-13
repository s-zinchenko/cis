# Generated by Django 4.1.1 on 2022-10-13 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flight', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='flight_time',
            field=models.IntegerField(default=0, verbose_name='Время полёта'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='confirmed',
            field=models.SmallIntegerField(default=False, verbose_name='Подтверждён?'),
        ),
    ]
