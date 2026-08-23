# CineCraft data and AI memory layer

Database member: `database-member3`

This backend owns MongoDB document models, project ownership checks, vector memory, and RAG context assembly. It does not call an AI provider or process video files.

## Structure

- `backend/app/database/models.py`: Pydantic document models for users, projects, scripts, scenes, characters, media, videos, and approvals.
- `backend/app/database/mongodb.py`: async MongoDB lifecycle and indexes.
- `backend/app/database/repositories/`: persistence and owner/project scoping.
- `backend/app/services/vector/`: embedding and vector-store abstraction. The default store is deterministic in-memory for local development and tests.
- `backend/app/services/memory/`: memory storage/search service.
- `backend/app/services/rag/`: retrieves relevant memory and formats scene context for Member 2's AI engine.
- `backend/app/routes/`: project, character, and memory APIs.

## MongoDB schema design

All documents use MongoDB `_id`, UTC `created_at`, and UTC `updated_at` fields.

- `users`: `email`, `display_name`.
- `projects`: `owner_id`, `title`, `original_idea`, `status`, and script/scene/media/video status fields.
- `scripts`: `project_id`, `version`, `content`, `generated_by`.
- `scenes`: `project_id`, `order`, `title`, `description`, `dialogue`, `character_ids`, `location`.
- `characters`: `project_id`, `name`, `appearance`, `personality`, `clothing`, `role`, `reference_information`.
- `media`: `project_id`, optional `scene_id`, `media_type`, `url`, `prompt`, `metadata`.
- `videos`: `project_id`, `url`, `status`, `metadata`.
- `approvals`: `project_id`, `state`, `approved`, optional `approved_by`, and `notes`.

Approval values are `IDEA`, `SCRIPT_GENERATED`, `SCRIPT_APPROVED`, `SCENES_GENERATED`, `SCENES_APPROVED`, `MEDIA_GENERATED`, `MEDIA_APPROVED`, `VIDEO_GENERATING`, and `COMPLETED`.

## Vector DB design

Each vector record contains `project_id`, `content`, `memory_type`, `metadata`, and `embedding`. Supported memory types include `character`, `scene`, `location`, `story`, `dialogue`, and `creator_preference`. Every search filters by project before ranking, preventing cross-project memory leakage.

`InMemoryVectorStore` is the local default. A Qdrant adapter can implement the `VectorStore` protocol using the same record shape when `CINECRAFT_VECTOR_PROVIDER=qdrant` is selected. The embedding interface is intentionally separate from Member 2's AI provider integration.

## RAG architecture

1. Store character/story/scene/dialogue facts with `POST /api/memory/store`.
2. A new scene request calls `GET /api/memory/search` with its project ID and query.
3. The service ranks project-local embeddings and returns the closest records.
4. `RAGContextService.build_scene_context` formats the records as labeled context.
5. Member 2 passes that context to the AI engine to generate a consistent scene.

## API documentation

FastAPI also exposes interactive docs at `/docs`.

- `POST /api/projects` creates a project.
- `GET /api/projects` lists only the authenticated user's projects.
- `GET /api/projects/{id}` reads an owned project.
- `PUT /api/projects/{id}` updates an owned project.
- `DELETE /api/projects/{id}` deletes an owned project.
- `GET /api/characters/{project_id}` lists characters after ownership validation.
- `POST /api/characters` creates a character for an owned project.
- `PUT /api/characters/{id}` updates a character only when its project is owned.
- `GET /api/memory/search?project_id=<id>&query=<text>&limit=5` searches project memory.
- `POST /api/memory/store` stores project-scoped memory.

Requests require `X-User-Id` containing a valid MongoDB ObjectId. Production authentication should replace this header dependency with the group's auth middleware while preserving the repository owner filters.

## Indexes

- `users.email` unique.
- `projects.owner_id + updated_at` and `projects.status`.
- `scripts.project_id + version`.
- `scenes.project_id + order`.
- `characters.project_id + name`.
- `media.project_id + scene_id`.
- `videos.project_id + created_at`.
- `approvals.project_id + created_at`.

## Sample documents

```json
{
  "_id": "66b000000000000000000001",
  "owner_id": "66b000000000000000000010",
  "title": "The Last Projection",
  "original_idea": "A projectionist discovers one final reel that changes her town.",
  "status": "IDEA",
  "script_status": "pending",
  "scene_status": "pending",
  "media_status": "pending",
  "video_status": "pending",
  "created_at": "2026-08-23T12:00:00Z",
  "updated_at": "2026-08-23T12:00:00Z"
}
```

```json
{
  "project_id": "66b000000000000000000001",
  "name": "Mara Vale",
  "appearance": "Short dark hair and a small scar above her eyebrow",
  "personality": "Observant, stubborn, quietly generous",
  "clothing": "Red wool coat and brass projectionist badge",
  "role": "Protagonist",
  "reference_information": {"visual_reference": "character/mara-v1"}
}
```

## Setup and testing

```powershell
cd backend
python -m pip install -r requirements.txt
$env:PYTHONPATH = "."
uvicorn app.main:app --reload
```

Set `CINECRAFT_MONGODB_URI` to a local MongoDB or MongoDB Atlas connection string. Credentials belong only in environment variables and must never be committed. MongoDB must be reachable when the API starts.

Run the dependency-free memory tests with:

```powershell
python -m pytest tests/test_memory.py
```
