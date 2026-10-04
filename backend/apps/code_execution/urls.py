from django.urls import path

from apps.code_execution.views import RunCodeView

urlpatterns = [
    path("run/", RunCodeView.as_view(), name="run-code"),
]
