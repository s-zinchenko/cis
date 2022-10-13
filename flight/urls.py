from django.urls import include, path, re_path

from flight.views import SchedulesListView, AirportListView, CancelFlightView, UploadFileView

urlpatterns = [
    path("schedules_list", SchedulesListView.as_view()),
    path("schedule_cancel/<int:pk>", CancelFlightView.as_view()),
    path("airport_list", AirportListView.as_view()),
    # path("upload_file", UploadFileView.as_view()),
    re_path(r'^upload_file/(?P<filename>[^/]+)$', UploadFileView.as_view()),
]
