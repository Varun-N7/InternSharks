from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_jobs_health():
    response = client.get("/jobs/health")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["status_code"] == 200


def test_create_document_analysis_job():
    response = client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "test.txt",
                b"This is a test document.",
                "text/plain",
            )
        },
        data={
            "analysis_type": "summary",
        },
    )

    assert response.status_code == 202

    data = response.json()

    assert data["success"] is True
    assert data["status_code"] == 202
    assert "job_id" in data["data"]
    assert data["data"]["status"] == "queued"


def test_create_extract_job():
    response = client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "test.txt",
                b"Extract information from this document.",
                "text/plain",
            )
        },
        data={
            "analysis_type": "extract",
        },
    )

    assert response.status_code == 202

    data = response.json()

    assert data["success"] is True
    assert "job_id" in data["data"]


def test_invalid_analysis_type():
    response = client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "test.txt",
                b"Test document.",
                "text/plain",
            )
        },
        data={
            "analysis_type": "invalid",
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"]["error_category"] == "invalid_analysis_type"


def test_missing_file():
    response = client.post(
        "/jobs/document-analysis",
        data={
            "analysis_type": "summary",
        },
    )

    assert response.status_code == 422


def test_empty_file():
    response = client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "empty.txt",
                b"",
                "text/plain",
            )
        },
        data={
            "analysis_type": "summary",
        },
    )

    assert response.status_code == 400


def test_get_job():
    create_response = client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "test.txt",
                b"Test document.",
                "text/plain",
            )
        },
        data={
            "analysis_type": "summary",
        },
    )

    assert create_response.status_code == 202

    job_id = create_response.json()["data"]["job_id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["data"]["job_id"] == job_id


def test_get_invalid_job():
    response = client.get("/jobs/does-not-exist")

    assert response.status_code == 404


def test_get_result_before_completion():
    create_response = client.post(
        "/jobs/document-analysis",
        files={
            "file": (
                "test.txt",
                b"Test document.",
                "text/plain",
            )
        },
        data={
            "analysis_type": "summary",
        },
    )

    assert create_response.status_code == 202

    job_id = create_response.json()["data"]["job_id"]

    response = client.get(
        f"/jobs/{job_id}/result"
    )

    assert response.status_code == 409


def test_list_jobs():
    response = client.get("/jobs")

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "jobs" in data["data"]
    assert isinstance(data["data"]["jobs"], list)