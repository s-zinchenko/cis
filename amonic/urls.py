from django.urls import include, path
from rest_framework import routers

from amonic.views import (
    login_user,
    logout_user,
    add_user,
    office_list,
    role_list,
    edit_role,
    user_list,
    toggle_user_active, user_activity,
)

router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path("login", login_user),
    path("logout", logout_user),
    path("add_user", add_user),
    path("office_list", office_list),
    path("user_list", user_list),
    path("role_list", role_list),
    path("edit_role", edit_role),
    path("toggle_activity", toggle_user_active),
    path("user_activity", user_activity),
]