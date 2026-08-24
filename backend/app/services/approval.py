from typing import Any, Protocol


class ApprovalProvider(Protocol):
    def get(self, project_id: str) -> dict[str, bool] | None: ...


class InMemoryApprovalProvider:
    def __init__(self) -> None:
        self.projects: dict[str, dict[str, bool]] = {}

    def set(self, project_id: str, script_approved: bool, scenes_approved: bool) -> None:
        self.projects[project_id] = {"script_approved": script_approved, "scenes_approved": scenes_approved}

    def get(self, project_id: str) -> dict[str, bool] | None:
        return self.projects.get(project_id)


class MongoApprovalProvider:
    """Reads Member 3's project collection; document ownership stays outside this service."""
    def __init__(self, collection: Any) -> None:
        self.collection = collection

    async def get_async(self, project_id: str) -> dict[str, bool] | None:
        document = await self.collection.find_one({"_id": project_id}, {"scriptApproved": 1, "scenesApproved": 1})
        if not document:
            return None
        return {"script_approved": bool(document.get("scriptApproved")), "scenes_approved": bool(document.get("scenesApproved"))}