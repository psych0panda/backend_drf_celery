"""Domain-level services for the video application.

All pure business logic should live here so that it can be reused from
Django views, Celery workers or any other interface without duplication.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List


# ---------- Storyboard generation ----------


def generate_storyboard(prompt: str, scenes: int = 3) -> List[Dict[str, Any]]:
    """Fake LLM call that returns list of *scenes*.

    In production здесь бы был вызов OpenAI / LangChain. Для демо возвращаем N
    одинаковых сцен с текстом.
    """
    time.sleep(1)  # эмулируем задержку сети / LLM
    return [
        {
            "idx": idx,
            "text": f"Scene {idx + 1} based on: {prompt}",
        }
        for idx in range(scenes)
    ]


# ---------- Media search step (parallel) ----------


def search_media_for_scene(scene: Dict[str, Any]) -> Dict[str, Any]:
    """Pretend to query external media API and enrich scene with media_url."""
    time.sleep(random.uniform(0.5, 1.5))  # network latency simulation
    scene["media_url"] = f"https://cdn.example.com/{scene['idx']}.jpg"
    return scene


# ---------- Merge results ----------


def merge_scenes(scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Collect scenes with media into a single storyboard dict."""
    return {"scenes": scenes}


# ---------- Compose video ----------


def compose_video(storyboard: Dict[str, Any]) -> str:
    """Pretend to render final video returning S3 URL."""
    time.sleep(2)  # simulate ffmpeg rendering
    return "https://s3.example.com/fake_video.mp4"


# ---------- Publish to YouTube ----------


def publish_to_youtube(video_url: str) -> str:
    """Pretend to publish video and return YouTube link."""
    time.sleep(1)
    return "https://youtube.com/watch?v=dQw4w9WgXcQ" 