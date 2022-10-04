from datetime import timedelta

import pytz
from django.utils import timezone
from rest_framework import authentication, exceptions
from rest_framework.authtoken.models import Token


class BearerAuthentication(authentication.TokenAuthentication):
    keyword = 'Bearer'

    # def authenticate_credentials(self, key):
    #     try:
    #         token = Token.objects.get(key=key)
    #     except self.model.DoesNotExist:
    #         raise exceptions.AuthenticationFailed('Invalid token')
    #
    #     if not token.user.is_active:
    #         raise exceptions.AuthenticationFailed('User inactive or deleted')
    #
    #     # This is required for the time comparison
    #     utc_now = timezone.now()
    #     utc_now = utc_now.replace(tzinfo=pytz.utc)
    #
    #     if token.created < utc_now - timedelta(hours=8):
    #         raise exceptions.AuthenticationFailed('Token has expired')
    #
    #     return token.user, token
