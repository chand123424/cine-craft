# CineCraft AI Engine

Python/FastAPI backend for CineCraft's idea-to-script and script-to-scenes workflow. It does not include React or database persistence. The in-memory store is an integration boundary for Member 3's database layer.

## Structure

```text
backend/
  app/
    main.py
    config.py
    exceptions.py
    routes/
      scripts.py
      scenes.py
    schemas/
      models.py
    services/
      store.py
      ai/
        base.py
        factory.py
        gemini.py
        grok.py
        huggingface.py
        http_provider.py
        mock.py
        prompt_builder.py
        service.py
  tests/
    test_api.py
requirements.txt
.env.example
```

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
$env:PYTHONPATH = "$PWD\backend"
uvicorn app.main:app --app-dir backend --reload
```

Open `http://127.0.0.1:8000/docs`. Set `AI_PROVIDER` to `gemini`, `grok`, or `huggingface` and provide the matching server-side key to use a real provider. Keys are never returned in API responses.

## API workflow

1. `POST /api/scripts/generate` creates `SCRIPT_GENERATED`.
2. `POST /api/scripts/{id}/approve` moves it to `SCRIPT_APPROVED`.
3. `POST /api/scenes/generate` is rejected unless the script is approved, then creates `SCENES_GENERATED`.
4. `POST /api/scenes/{id}/approve` approves each scene. Once all scenes are approved, the script moves to `SCENES_APPROVED`.
5. Media/video states are reserved for the downstream media/video service and represented by `WorkflowState`.

All request and response payloads are Pydantic models. Regeneration uses `target` values `script`, `scene`, `image_prompt`, `audio_prompt`, or `dialogue`; only the targeted content is changed.

## Sample requests

Generate a script:

```json
{"project_id":"project-123","idea":"A courier discovers a message from the future.","genre":"sci-fi","tone":"hopeful","target_platform":"short video"}
```

Generate scenes after approval:

```json
{"project_id":"project-123","script_id":"script_...","visual_style":"neo-noir","user_preferences":"Keep the courier's red jacket consistent."}
```

Regenerate one prompt:

```json
{"target":"image_prompt","instructions":"Make the dawn light warmer and preserve the red jacket."}
```

## Tests

```powershell
$env:PYTHONPATH = "$PWD\backend"
pytest backend/tests -q
```

## Branch

`ai-member2`
