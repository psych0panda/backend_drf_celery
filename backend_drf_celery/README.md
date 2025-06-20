# Backend DRF + Celery Demo

Minimal showcase of a Django Rest Framework application that triggers a Celery task using an explicit **service layer** for business logic and keeping infrastructure concerns separate.

## Key ideas

1. **3-layer separation**
   * **API (views/serializers)** — accept & validate HTTP-input, no business logic.
   * **Services (`video.services`)** — pure Python, reusable from views or tasks.
   * **Tasks (`video.tasks`)** — thin Celery wrappers that delegate to services.
2. **Celery autodiscovery** via `config.celery.app.autodiscover_tasks()`.
3. Docker-Compose stack (`web`, `worker`, `redis`) for local dev.

## Quick start

```bash
# 1. Build images & start stack
cp .env.sample .env  # adjust if needed
docker compose up --build

# 2. Make a request
curl -X POST http://localhost:8000/api/process/ \
     -H 'Content-Type: application/json' \
     -d '{"prompt": "Create a video about AI"}'
# → {"task_id": "<uuid>"}

# 3. Poll task status
curl http://localhost:8000/api/tasks/<uuid>/
```

Демоданные заменены «заглушками» — настоящие вызовы OpenAI, Depositphotos, ffmpeg и т.д. подключаются внутри соответствующих функций `video.services.*`.

## Новый Celery-pipeline

В `video.tasks` добавлены атомарные задачи:

* `generate_storyboard_task` — синтез сцен
* `search_media_task` (исполняется параллельно через `group`)
* `merge_scenes_task` — callback `chord`-а
* `compose_video_task` → `publish_youtube_task`

Оркестратор `process_prompt_task` строит:

`generate → chord(search_media) → merge → compose → publish`

Таким образом внешний API остаётся прежним (`/api/process/`), а под капотом работает отказоустойчивый конвейер Celery.

## Celery Task Flow

```
              +---------------------------+
(prompt) ---> | 1) generate_storyboard    |  (simple task)
              +-------------+-------------+
                            |
          +-----------------v-----------------+
          | group( search_media(scene_i) )    |  # параллельно
          +-----------------+-----------------+
                            |
          +-----------------v-----------------+
          | chord callback: merge_media       |
          +-----------------+-----------------+
                            |
              +-------------v-------------+
              | 4) compose_final_video    |
              +-------------+-------------+
                            |
              +-------------v-------------+
              | 5) publish_to_youtube     |
              +---------------------------+
```

## Additional Notes

1. **Isolation of Errors**: If a task fails, it only affects that specific task, not the entire pipeline.
2. **Parallelism**: Tasks can run concurrently, which is ideal for tasks like media search or generating images for multiple scenes.
3. **Idempotency and Restart**: If a task fails, it can be retried without restarting the entire pipeline.
4. **Monitoring and Metrics**: It's easy to see how much time each step takes.
5. **Horizontal Scaling**: Separate pools of workers can be maintained for different tasks, balancing resources more effectively than with a single shared worker.
6. **Reusability**: Tasks can be reused in different pipelines or contexts without duplicating code.

## When Not to Split

1. **Atomic Tasks**: If a task takes less than 30 seconds and there's no benefit from parallelism, adding unnecessary granularity will add overhead.
2. **Too Many Small Tasks**: Too many small tasks can lead to a deluge of messages in the broker, which can degrade performance.

## Conclusion

Breaking down the pipeline into `chain/group/chord` gives fault tolerance, scalability, and easy monitoring, while keeping the external API (views) unchanged—which aligns with the principles of *clean architecture*: the UI layer is not dependent on the details of orchestration deep down. 

## Prompt storage (new `prompts` app)

Модели:

| Model | Цель |
|-------|------|
| `Prompt` | текущая активная версия системных / шаблонных prompt'ов (type, text, parameters, tags) |
| `PromptVersion` | неизменяемые слепки текста для аудита и откатов (FK→Prompt, version, author) |
| `UserPrompt` | сырые пользовательские запросы, для аналитики и retraining |

Поле `parameters` хранит JSON c настройками LLM (model, temperature…).

Для полнотекстового/семантического поиска можно добавить pgvector-таблицу `PromptEmbedding`, если переключитесь на Postgres. 

## New models in prompts app

1. `Prompt`  
   • type (system/template/tool/user)  
   • text, parameters (JSON), tags (JSON-array)  
   • active `version`, creation/update dates.

2. `PromptVersion`  
   • FK → Prompt, version number, text, parameters, author  
   • immutable snapshot; unique pair `(prompt, version)`.

3. `UserPrompt`  
   • FK → User, original user text, language, arbitrary metadata  
   • suitable for analytics and retraining.

All models are already entered in `prompts/models.py`, and `prompts.apps.PromptsConfig` added to `INSTALLED_APPS`.  

To apply in the database:

```bash
docker compose run --rm web python manage.py makemigrations prompts
docker compose run --rm web python manage.py migrate
```

If later decide to switch to Postgres + pgvector, can add `PromptEmbedding` model with `VectorField`. 