from __future__ import annotations

from celery import current_app
from celery.result import AsyncResult
from rest_framework import status, views
from rest_framework.response import Response

from .serializers import PromptSerializer
from .tasks import process_prompt_task


class PromptProcessView(views.APIView):
    """API endpoint that triggers Celery task to process a prompt."""

    serializer_class = PromptSerializer

    def post(self, request, *args, **kwargs):  # noqa: D401
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        prompt: str = serializer.validated_data["prompt"]

        task = process_prompt_task.delay(prompt)
        return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)


class TaskStatusView(views.APIView):
    """Simple endpoint to check Celery task status/results."""

    def get(self, request, task_id: str, *args, **kwargs):  # noqa: D401
        result = AsyncResult(task_id, app=current_app)
        data = {
            "task_id": task_id,
            "state": result.state,
        }
        if result.successful():
            data["result"] = result.result
        return Response(data) 