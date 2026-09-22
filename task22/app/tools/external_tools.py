from app.services.external_project_service import (
    get_external_project_status,
)


def get_external_project_status_tool(
    project_id: int,
    failure_mode: str = "success",
):
    return get_external_project_status(
        project_id=project_id,
        failure_mode=failure_mode,
    )