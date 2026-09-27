from django.urls import path

from .views import ExecuteCodeView, ExecutionResultView


urlpatterns = [
    path("run/", ExecuteCodeView.as_view(), name="run-code"),
    path(
        "run/<str:token>/",
        ExecutionResultView.as_view(),
        name="run-result",
    ),
]
