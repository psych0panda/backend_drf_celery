from __future__ import annotations

from django.urls import path

from .views import PromptProcessView, TaskStatusView

urlpatterns = [
    path("process/", PromptProcessView.as_view(), name="prompt-process"),
    path("tasks/<str:task_id>/", TaskStatusView.as_view(), name="task-status"),
] 