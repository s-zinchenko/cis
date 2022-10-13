import json

from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView, UpdateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from amonic.models import User, UserLog, Office, Role, UserCrashReport
from amonic.serializers import UserCrashReportSerializer, UserActivitySerializer, \
    ToggleUserActiveSerializer, UserListSerializer, IdTitleSerializer, UserAddSerializer, EditRoleSerializer, \
    IsGracefulSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
        data = {}
        req_body = json.loads(request.body)
        if not (req_body and req_body.get("email") and req_body.get("password")):
            raise ValidationError(
                {
                    "status": "Bad Request",
                    "code": 400,
                    "msg": "required field: email and password is not filled!"
                }
            )
        email1 = req_body['email']
        password = req_body['password']
        try:
            user = User.objects.get(email=email1)
        except BaseException as e:
            raise ValidationError(
                {
                    "status": "Not Found",
                    "code": 404,
                    "msg": str(e)
                }
            )
        with transaction.atomic():
            token = Token.objects.get_or_create(user=user)[0].key
            if not check_password(password, user.password):
                raise ValidationError(
                    {
                        "status": "Forbidden",
                        "code": 403,
                        "msg": "Incorrect Login credentials"
                    }
                )
            UserLog.objects.create(user=user)

        if user.is_active:
            login(request, user)
            data["message"] = "user logged in"
            data["email_address"] = user.email
            data["is_admin"] = user.is_superuser
            total_time = timezone.now() - UserLog.objects.filter(user=user, login_date__gte=timezone.now() - timezone.timedelta(days=30)).first().login_date
            res = {
                "data": data,
                "token": token,
                "total_time_in_system": f"Time spent on system: {total_time}",
                "msg": f"Hi {user.first_name} {user.last_name}, Welcome to AMONIC Airlines Automation System",

            }
            return Response(res)
        else:
            raise ValidationError(
                {
                    "status": "Forbidden",
                    "code": 403,
                    "msg": "Account not active"
                }
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    with transaction.atomic():
        request.user.auth_token.delete()
        UserLog.objects.filter(user=request.user, logout_date__isnull=True).update(logout_date=timezone.now())
    logout(request)
    return Response({"message": 'User Logged out successfully'})


class UserAddView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserAddSerializer
    permission_classes = [IsAdminUser,]


class OfficeListView(ListAPIView):
    queryset = Office.objects.all()
    serializer_class = IdTitleSerializer
    permission_classes = [IsAdminUser,]


class RoleListView(ListAPIView):
    queryset = Role.objects.all()
    serializer_class = IdTitleSerializer
    permission_classes = [IsAdminUser,]


class EditRoleView(APIView):
    queryset = User.objects.all()
    serializer_class = EditRoleSerializer
    permission_classes = [IsAdminUser, ]

    def post(self, request, *args, **kwargs):
        user_id = self.request.data.pop("id")
        body = self.request.data
        User.objects.filter(pk=user_id).update(**body)
        return Response(
            {
                "status": "ok",
                "code": 200,
            }
        )


class UserListView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        queryset = User.objects.exclude(pk=self.request.user.pk)
        office_id = self.request.query_params.get("office_id")
        if office_id:
            queryset.filter(office_id=int(office_id))
        return queryset


class ToggleUserActiveView(UpdateAPIView):
    permission_classes = [IsAdminUser,]
    serializer_class = ToggleUserActiveSerializer

    def post(self, request, *args, **kwargs):
        user_id = self.request.data["id"]
        user = User.objects.filter(id=user_id).first()
        user.is_active = not user.is_active
        user.save()
        serializer = self.serializer_class({"is_active": user.is_active, "id": user.id})
        return Response(serializer.data)


class UserActivityView(ListAPIView):
    queryset = UserLog.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserActivitySerializer

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        queryset = queryset.filter(user=self.request.user).order_by("-id")
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().select_related("crash_report")
        user_activity = self.filter_queryset(queryset)
        user_activity = user_activity[1:]


        a = UserCrashReport.objects.first()
        for user in user_activity:
            user.time_spent = timezone.now() - user.login_date
            if user.logout_date:
                user.time_spent = user.logout_date - user.login_date
            else:
                user.time_spent = ""

        serializer = self.serializer_class(user_activity, many=True)
        return Response(serializer.data)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated, ]
    # serializer_class = UserInfoSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        total_time = timezone.now() - UserLog.objects.filter(user=user,
                                                             login_date__gte=timezone.now() - timezone.timedelta(
                                                                 days=30)).first().login_date
        total_time = total_time.days * 24 * 60 * 60 + total_time.seconds
        return Response(
            {"id": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name,
             "birthdate": user.birthdate, "role__title": user.role.title if user.role else None,
             "office": user.office.title if user.office else None, "is_active": user.is_active,
             "total_time_in_system": total_time,
             "msg": f"Hi {user.first_name} {user.last_name}, Welcome to AMONIC Airlines Automation System",
             "is_admin": user.is_staff}
        )


class IsGracefulLogoutView(GenericAPIView):
    serializer_class = IsGracefulSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        last_login = UserLog.objects.filter(user=request.user).last()
        data = {"user_log_id": last_login.id, "last_login": last_login.login_date}
        if last_login.logout_date:
            data["is_graceful_logout"] = True
        else:
            data["is_graceful_logout"] = False
        return Response(data)


class SendReportView(CreateAPIView):
    queryset = UserCrashReport.objects.all()
    permission_classes = [IsAuthenticated,]
    serializer_class = UserCrashReportSerializer
