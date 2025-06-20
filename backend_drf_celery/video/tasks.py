from __future__ import annotations

from celery import chain, chord, group, shared_task

from . import services


# --- Atomic tasks --------------------------------------------------------


@shared_task(name="video.generate_storyboard")
def generate_storyboard_task(prompt: str) -> list[dict]:  # noqa: D401
    return services.generate_storyboard(prompt)


@shared_task(name="video.search_media")
def search_media_task(scene: dict) -> dict:  # noqa: D401
    return services.search_media_for_scene(scene)


@shared_task(name="video.merge_scenes")
def merge_scenes_task(scenes: list[dict]) -> dict:  # noqa: D401
    return services.merge_scenes(scenes)


@shared_task(name="video.compose_video")
def compose_video_task(storyboard: dict) -> str:  # noqa: D401
    return services.compose_video(storyboard)


@shared_task(name="video.publish_youtube")
def publish_youtube_task(video_url: str) -> str:  # noqa: D401
    return services.publish_to_youtube(video_url)


# --- Orchestrator task ---------------------------------------------------


@shared_task(name="video.process_prompt")
def process_prompt_task(prompt: str) -> dict:  # noqa: D401
    """High-level task triggered from the API layer.

    1. Генерируем storyboard (сцены)
    2. Для каждой сцены параллельно ищем медиа (group)
    3. После успешного поиска делаем merge → compose → publish
    Возвращаем `pipeline_id` — id первой задачи внутри цепочки, чтобы клиент
    мог отслеживать дальнейший прогресс.
    """

    # 1) Синхронно генерируем storyboard (быстро: 1-2 сек). В бою это можно
    #    вынести в отдельную Celery-задачу, но для наглядности — здесь.
    scenes = services.generate_storyboard(prompt, scenes=3)

    # 2) Параллельно ищем медиа по каждой сцене
    header = group(search_media_task.s(scene) for scene in scenes)

    # 3) После завершения группы идём далее по цепочке
    body = chain(
        merge_scenes_task.s(),
        compose_video_task.s(),
        publish_youtube_task.s(),
    )

    async_result = chord(header, body).apply_async()

    # Возвращаем id финального callback-таска — его состояние = состояние пайплайна
    return {"pipeline_root_id": async_result.id} 