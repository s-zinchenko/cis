from rest_framework import serializers

from amonic.models import UserCrashReport, User, UserLog, Role


class UserCrashReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCrashReport
        fields = ("description", "reason", "userlog")

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        validated_data["user"] = self.context['request'].user
        return validated_data


class IsGracefulLogout(serializers.Serializer):
    last_login = serializers.DateTimeField()
    is_graceful_logout = serializers.BooleanField()


class TitleSerializer(serializers.Serializer):
    title = serializers.CharField()


class UnsuccessfulLogoutReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCrashReport
        fields = (
            "reason"
        )


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLog
        fields = (
            "id",
            "login_date",
            "logout_date",
            "time_spent",
            "crash_report",
        )
        depth = 1

    time_spent = serializers.CharField()


class ToggleUserActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "is_active")


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "office",
            "is_active",
            "age",
        )

    role = TitleSerializer()
    office = TitleSerializer()
    age = serializers.IntegerField(required=False)


class IdTitleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()


class UserAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "first_name",
            "last_name",
            "office",
            "birthdate",
            "office_id",
            "role_id",
        )

    role_id = serializers.ChoiceField(choices=Role.objects.filter(title__in=["User", "Пользователь"]).values_list("id", flat=True))


class EditRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id"
            "email"
            "first_name"
            "last_name"
            "office_id"
            "role_id"
        )

    role_id = serializers.ChoiceField(
        choices=Role.objects.filter(title__in=["User", "Пользователь"]).values_list("id", flat=True))


class IsGracefulSerializer(serializers.Serializer):
    user_log_id = serializers.IntegerField()
    last_login = serializers.DateTimeField()
    is_graceful_logout = serializers.BooleanField()


# ?
class UserInfoSerializer(serializers.ModelSerializer):
    role_title = TitleSerializer(read_only=True)
    office_title = TitleSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "birthdate",
            # "role",
            # "office",
            "role_title",
            "office_title",
            "is_active",
            "is_staff",
            "total_time_in_system",
            "msg",
        )
        depth = 1

    msg = serializers.CharField()
    total_time_in_system = serializers.IntegerField()
