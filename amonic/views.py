import json
import datetime

from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from amonic.models import User, UserLog, Office, Role


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


@api_view(["POST"])
@permission_classes([IsAdminUser])
def add_user(request):
    req_body = json.loads(request.body)
    if not (
            req_body
            and req_body.get("email")
            and req_body.get("password")
            and req_body.get("first_name")
            and req_body.get("last_name")
            and req_body.get("office")
            and req_body.get("birthdate")
    ):
        raise ValidationError(
            {
                "status": "Bad Request",
                "code": 400,
                "msg": "email, password, first_name, last_name, office, birthdate fields is required"
            }
        )

    try:
        office = req_body.pop("office")
        req_body["office_id"] = office
        req_body["role_id"] = Role.objects.get(title__in=["User", "Пользователь"]).id
        User.objects.create_user(**req_body)
    except Exception as e:
        raise ValidationError(
            {
                "status": "Forbidden",
                "code": 403,
                "msg": str(e)
            }
        )
    return Response(
        {
            "status": "ok",
            "code": 200,
        }
    )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def office_list(request):
    office_list = Office.objects.values("id", "title")
    return Response(
        office_list
    )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def role_list(request):
    role_list = Role.objects.values("id", "title")
    return Response(
        role_list
    )


@api_view(["POST"])
@permission_classes([IsAdminUser])
def edit_role(request):
    req_body = json.loads(request.body)
    allowed_fields = {"id", "email", "first_name", "last_name", "office_id", "role_id"}

    if not set(req_body.keys()).issubset(allowed_fields):
        raise ValidationError(
            {
                "status": "Bad Request",
                "code": 400,
                "msg": f"allowed_fields: {allowed_fields}"
            }
        )

    for k in req_body.keys():
        if req_body.get(k) is None:
            req_body.pop(k)

    user_id = req_body.pop("id")
    User.objects.filter(pk=user_id).update(**req_body)

    return Response(
        {
            "status": "ok",
            "code": 200,
        }
    )


@api_view(["GET"])
@permission_classes([IsAdminUser])
def user_list(request):
    req_query = request.query_params
    user_list = []
    filter = {}
    if not req_query.get("office_id"):
        for user in User.objects.all().values("id", "email", "first_name", "last_name", "birthdate","role__title", "office", "is_active").exclude(pk=request.user.pk):
            user_birthdate = user.pop("birthdate")
            user["age"] = int((datetime.date.today() - user_birthdate).days / 365)
            user_list.append(user)
        return Response(
            user_list
        )

    filter["office_id"] = int(req_query.get("office_id"))

    for user in User.objects.filter(**filter).values("id", "email", "first_name", "last_name", "birthdate", "role__title", "office", "is_active").exclude(pk=request.user.pk):
        user_birthdate = user.pop("birthdate")
        user["age"] = int((datetime.date.today() - user_birthdate).days / 365)
        user_list.append(user)
    return Response(
        user_list
    )


@api_view(["POST"])
@permission_classes([IsAdminUser])
def toggle_user_active(request):
    req_body = json.loads(request.body)
    if not (req_body and req_body.get("user_id")):
        raise ValidationError(
            {
                "status": "Bad Request",
                "code": 400,
                "msg": "required field user_id not filled!"
            }
        )
    user = User.objects.filter(id=req_body.get("user_id")).first()
    if not user:
        raise ValidationError(
            {
                "status": "Not Found",
                "code": 404,
                "msg": "User not found!"
            }
        )

    user.is_active = not user.is_active
    user.save()

    return Response(
        {
            "status": "ok",
            "code": 200,
            "data": {
                "user": {
                    "id": user.id,
                    "is_active": user.is_active,
                }
            }
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_activity(request):
    user_activity = UserLog.objects.filter(user=request.user).values("reason", "login_date", "logout_date").order_by("-id")
    user_activity = list(user_activity)
    res = []
    user_activity.pop(0)

    for user in user_activity:
        # res = {
        #     "time_spent": user["logout_date"] - user["login_date"],
        #     "date":
        # }
        user["time_spent"] = timezone.now() - user["login_date"]
        if user["logout_date"]:
            user["time_spent"] = user["logout_date"] - user["login_date"]
        else:
            user["logout_date"] = user["login_date"] + timezone.timedelta(hours=24)

    return Response(
        user_activity
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = request.user
    total_time = timezone.now() - UserLog.objects.filter(user=user, login_date__gte=timezone.now() - timezone.timedelta(
        days=30)).first().login_date
    total_time = total_time.days * 24 * 60 * 60 + total_time.seconds
    return Response(
        {"id": user.id, "email": user.email, "first_name": user.first_name, "last_name": user.last_name, "birthdate": user.birthdate, "role__title": user.role, "office": user.office, "is_active": user.is_active, "total_time_in_system": total_time,
                "msg": f"Hi {user.first_name} {user.last_name}, Welcome to AMONIC Airlines Automation System",}
    )