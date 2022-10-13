import datetime
import uuid
from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(
        self, email: str, password: str, **extra_fields: dict
    ) -> AbstractBaseUser:
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, email: str = None, password: str = None, **extra_fields: Any
    ) -> AbstractBaseUser:
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str, **extra_fields: Any
    ) -> AbstractBaseUser:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    email = models.EmailField("E-mail", unique=True)
    first_name = models.CharField("Имя", max_length=30, null=True, blank=True)
    last_name = models.CharField(
        "Фамилия", max_length=30, null=True, blank=True
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Определяет, может ли пользователь заходить на админ. сайт"
        ),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Определяет, активен ли пользователь. "
            "Снимите галочку, вместо удаления аккаунта пользователя"
        ),
    )
    role = models.ForeignKey(
        "amonic.Role",
        on_delete=models.PROTECT,
        verbose_name="Роль пользователя",
        blank=True,
        null=True,
    )
    office = models.ForeignKey(
        "amonic.Office",
        on_delete=models.PROTECT,
        verbose_name="Роль пользователя",
        blank=True,
        null=True,
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    birthdate = models.DateField(default=datetime.date.today(), verbose_name="Дата рождения")

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"

    def get_full_name(self) -> str:
        return f"{self.last_name} {self.first_name}"

    def get_short_name(self) -> str:
        return self.email

    @property
    def age(self):
        return int((datetime.date.today() - self.birthdate).days / 365)


class Role(models.Model):
    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    title = models.CharField(max_length=256, verbose_name="название")


class Office(models.Model):
    country = models.ForeignKey(
        "amonic.Country",
        on_delete=models.CASCADE,
        verbose_name="Страна",
        blank=True,
        null=True,
    )
    title = models.CharField(
        max_length=256,
        verbose_name="Название"
    )
    phone = models.CharField(
        max_length=256,
        verbose_name="Телефон"
    )
    contact = models.CharField(
        max_length=256,
        verbose_name="Контакты"
    )


class Country(models.Model):
    name = models.CharField(max_length=128, verbose_name="Название")


class UserLog(models.Model):
    class Meta:
        verbose_name = "Журнал активности пользователя"

    user = models.ForeignKey(
        "amonic.User",
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    login_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата/время входа в систему"
    )
    logout_date = models.DateTimeField(
        auto_now_add=False,
        verbose_name="Дата/время выхода из системы",
        blank=True,
        null=True,
    )
    crash_report = models.OneToOneField("amonic.UserCrashReport", on_delete=models.PROTECT, verbose_name="Сообщение об ошибке", null=True, blank=True)

    def __str__(self):
        return f"{self.user} {self.login_date}"


class UserCrashReport(models.Model):
    class Meta:
        verbose_name = "Отчёт пользователя об ошибке"
        verbose_name_plural = "Отчёты пользователя об ошибках"

    class CrashReason(models.Choices):
        SOFTWARE_CRASH = "software_crash"
        SYSTEM_CRASH = "system_crash"

    user = models.ForeignKey(
        "amonic.User",
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата/время входа в систему"
    )
    description = models.CharField(max_length=2048, verbose_name="Описание ошибки")
    reason = models.CharField(
        max_length=32,
        choices=CrashReason.choices,
        verbose_name="Причина ошибки",
    )

    def __str__(self):
        return f"{self.user.email} {self.reason} {self.date.isoformat()}"
