import uuid

import pytest


def create_user_data():

    unique_id = str(uuid.uuid4())[:8]

    return {
        "username": f"taskuser{unique_id}",
        "email": f"taskuser{unique_id}@example.com",
        "password": "password123",
        "full_name": "Task User",
    }


async def register_and_login(
    client,
):

    user_data = create_user_data()

    register_response = await client.post(
        "/auth/register",
        json=user_data,
    )

    assert register_response.status_code == 201

    login_response = await client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    return access_token, user_data


@pytest.mark.asyncio
async def test_create_task(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": "Test Task",
            "description": "Test task description",
            "status": "todo",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["title"] == "Test Task"
    assert data["description"] == "Test task description"
    assert data["status"] == "todo"
    assert data["priority"] == "high"
    assert data["created_by"]


@pytest.mark.asyncio
async def test_create_task_without_auth(
    client,
):

    response = await client.post(
        "/tasks",
        json={
            "title": "Test Task",
            "description": "Test task description",
            "status": "todo",
            "priority": "low",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 401
    assert data["error"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_create_task_invalid_data(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={},
    )

    assert response.status_code == 422

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 422
    assert data["error"] == "VALIDATION_ERROR"
    assert data["message"] == "Invalid request data"


@pytest.mark.asyncio
async def test_get_tasks(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    create_response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": "Get Task",
            "description": "Task for get test",
            "status": "todo",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 201

    response = await client.get(
        "/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["page"] == 1
    assert data["limit"]
    assert data["total"] >= 1
    assert len(data["data"]) >= 1


@pytest.mark.asyncio
async def test_get_tasks_without_auth(
    client,
):

    response = await client.get(
        "/tasks"
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 401
    assert data["error"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_single_task(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    create_response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": "Single Task",
            "description": "Single task description",
            "status": "todo",
            "priority": "low",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = await client.get(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Single Task"


@pytest.mark.asyncio
async def test_get_task_not_found(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    task_id = str(uuid.uuid4())

    response = await client.get(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 404
    assert data["error"] == "NOT_FOUND"
    assert data["message"] == "Task not found"


@pytest.mark.asyncio
async def test_get_task_invalid_id(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    response = await client.get(
        "/tasks/invalid-task-id",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 400
    assert data["error"] == "BAD_REQUEST"
    assert data["message"] == "Invalid task ID"


@pytest.mark.asyncio
async def test_update_task(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    create_response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": "Old Title",
            "description": "Old description",
            "status": "todo",
            "priority": "low",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = await client.put(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": "Updated Title",
            "description": "Updated description",
            "status": "todo",
            "priority": "high",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"
    assert data["status"] == "todo"
    assert data["priority"] == "high"


@pytest.mark.asyncio
async def test_update_task_status(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    create_response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": "Status Task",
            "description": "Status test",
            "status": "todo",
            "priority": "medium",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = await client.patch(
        f"/tasks/{task_id}/status",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "status": "completed",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_update_task_invalid_status(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    create_response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": "Invalid Status Task",
            "description": "Invalid status test",
            "status": "todo",
            "priority": "low",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = await client.patch(
        f"/tasks/{task_id}/status",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "status": "invalid_status",
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 422
    assert data["error"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_delete_task(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    create_response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": "Delete Task",
            "description": "Delete test",
            "status": "todo",
            "priority": "low",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    response = await client.delete(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 204

    get_response = await client.get(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert get_response.status_code == 404

    data = get_response.json()

    assert data["success"] is False
    assert data["status_code"] == 404
    assert data["error"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_task_not_found(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    task_id = str(uuid.uuid4())

    response = await client.delete(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 404
    assert data["error"] == "NOT_FOUND"
    assert data["message"] == "Task not found"


@pytest.mark.asyncio
async def test_delete_task_without_auth(
    client,
):

    task_id = str(uuid.uuid4())

    response = await client.delete(
        f"/tasks/{task_id}"
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 401
    assert data["error"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_user_cannot_access_other_users_task(
    client,
):

    first_token, first_user = await register_and_login(
        client
    )

    create_response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {first_token}"
        },
        json={
            "title": "Private Task",
            "description": "Private task",
            "status": "todo",
            "priority": "high",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    second_token, second_user = await register_and_login(
        client
    )

    response = await client.get(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {second_token}"
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 403
    assert data["error"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_user_cannot_update_other_users_task(
    client,
):

    first_token, first_user = await register_and_login(
        client
    )

    create_response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {first_token}"
        },
        json={
            "title": "Private Update Task",
            "description": "Private task",
            "status": "todo",
            "priority": "low",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    second_token, second_user = await register_and_login(
        client
    )

    response = await client.put(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {second_token}"
        },
        json={
            "title": "Hacked Task",
            "status": "todo",
            "priority": "low",
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 403
    assert data["error"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_user_cannot_delete_other_users_task(
    client,
):

    first_token, first_user = await register_and_login(
        client
    )

    create_response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {first_token}"
        },
        json={
            "title": "Private Delete Task",
            "description": "Private task",
            "status": "todo",
            "priority": "low",
        },
    )

    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    second_token, second_user = await register_and_login(
        client
    )

    response = await client.delete(
        f"/tasks/{task_id}",
        headers={
            "Authorization": f"Bearer {second_token}"
        },
    )

    assert response.status_code == 403

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 403
    assert data["error"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_task_pagination(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    for number in range(3):

        response = await client.post(
            "/tasks",
            headers={
                "Authorization": f"Bearer {access_token}"
            },
            json={
                "title": f"Pagination Task {number}",
                "description": "Pagination test",
                "status": "todo",
                "priority": "low",
            },
        )

        assert response.status_code == 201

    response = await client.get(
        "/tasks?page=1&limit=2",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total"] >= 3
    assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_task_status_filter(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": "Completed Task",
            "description": "Filter test",
            "status": "completed",
            "priority": "low",
        },
    )

    assert response.status_code == 201

    response = await client.get(
        "/tasks?status=completed",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    for task in data["data"]:
        assert task["status"] == "completed"


@pytest.mark.asyncio
async def test_task_priority_filter(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": "High Priority Task",
            "description": "Priority filter test",
            "status": "todo",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    response = await client.get(
        "/tasks?priority=high",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    for task in data["data"]:
        assert task["priority"] == "high"


@pytest.mark.asyncio
async def test_task_search(
    client,
):

    access_token, user_data = await register_and_login(
        client
    )

    response = await client.post(
        "/tasks",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "title": "Unique Search Task",
            "description": "Search test",
            "status": "todo",
            "priority": "medium",
        },
    )

    assert response.status_code == 201

    response = await client.get(
        "/tasks?search=Unique%20Search",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["total"] >= 1

    assert any(
        task["title"] == "Unique Search Task"
        for task in data["data"]
    )