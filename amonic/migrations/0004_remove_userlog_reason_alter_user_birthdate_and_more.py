# Generated by Django 4.1.1 on 2022-10-04 18:30

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('amonic', '0003_user_birthdate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userlog',
            name='reason',
        ),
        migrations.AlterField(
            model_name='user',
            name='birthdate',
            field=models.DateField(default=datetime.datetime(2022, 10, 4, 18, 30, 57, 590425, tzinfo=datetime.timezone.utc), verbose_name='Дата рождения'),
        ),
        migrations.CreateModel(
            name='UserCrashReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Дата/время входа в систему')),
                ('description', models.CharField(max_length=2048, verbose_name='Описание ошибки')),
                ('reason', models.CharField(blank=True, choices=[('software_crash', 'Software Crash'), ('system_crash', 'System Crash')], max_length=32, null=True, verbose_name='Причина ошибки')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Отчёт пользователя об ошибке',
                'verbose_name_plural': 'Отчёты пользователя об ошибках',
            },
        ),
    ]
