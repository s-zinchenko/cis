from django.contrib import admin

from amonic.models import UserLog, Country, Office, Role, User


@admin.register(UserLog)
class UserLogAdmin(admin.ModelAdmin):
    fields = (
        "user",
        "reason",
        "logout_date",
    )


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    pass


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    pass


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
