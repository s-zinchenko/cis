from django.urls import include, path
from rest_framework import routers

from amonic.views import (
    login_user,
    logout_user,
    OfficeListView,
    RoleListView,
    SendReportView, IsGracefulLogoutView, UserInfoView, UserActivityView, ToggleUserActiveView, UserListView,
    UserAddView, EditRoleView,
)

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),

    path("login", login_user),
    path("logout", logout_user),

    path("edit_role", EditRoleView.as_view()),
    path("add_user", UserAddView.as_view()),
    path("office_list", OfficeListView.as_view()),
    path("role_list", RoleListView.as_view()),
    path("user_list", UserListView.as_view()),
    path('user', UserInfoView.as_view()),
    path("toggle_activity", ToggleUserActiveView.as_view()),
    path("user_activity", UserActivityView.as_view()),
    path("send_report", SendReportView.as_view()),
    path("is_graceful_logout", IsGracefulLogoutView.as_view()),
]