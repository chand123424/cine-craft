# CineCraft Media Backend

FastAPI service for scene image/audio generation, selective regeneration, asset validation, and FFmpeg video composition. It intentionally has no React UI, script-generation engine, or MongoDB implementation.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## FFmpeg

Windows: the project uses `imageio-ffmpeg` automatically when a system `ffmpeg` command is unavailable. For a system installation, run `winget install Gyan.FFmpeg`, restart the terminal, and confirm with `ffmpeg -version`. The image and audio endpoints work without FFmpeg.

## API examples

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/media/image/generate -ContentType 'application/json' -Body '{"project_id":"demo","scene_id":"scene-1","scene_description":"A train arrives","image_prompt":"cinematic train station at dusk","location":"station","visual_style":"film still"}'
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/media/audio/generate -ContentType 'application/json' -Body '{"project_id":"demo","scene_id":"scene-1","text":"The train arrives.","audio_type":"narration","duration_seconds":3}'
```

Generated assets start unapproved by design. The owning approval workflow must set `approved=true` before `/api/videos/create`. The project service must also call `media_store.set_project_approval(project_id, script_approved=True, scenes_approved=True)` through its integration adapter; otherwise video creation returns a clear approval error. For MongoDB, inject `MongoApprovalProvider` with Member 3's existing project collection; it reads only `_id`, `scriptApproved`, and `scenesApproved` and does not define a duplicate document model. Video creation supports `9:16`, `16:9`, and `1:1`, per-scene durations, fade transitions, and an optional approved `music_asset_id` mixed beneath scene audio. Use `GET /api/videos/project/{project_id}` to list a project's videos and `GET /api/videos/{id}` for one video.

## Structure

```text
backend/app/
  main.py models.py
  routes/media.py routes/videos.py
  services/media_store.py
  services/image/generator.py
  services/audio/generator.py
  utils/ffmpeg.py
requirements.txt  .env.example  README.md
```

## Testing

```powershell
pytest
```

Branch name: `media-member4`