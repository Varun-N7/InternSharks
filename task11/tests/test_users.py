import uuid

import pytest


def create_user_data():

    unique_id = str(uuid.uuid4())[:8]

    return {
        "username": f"testuser{unique_id}",
        "email": f"testuser{unique_id}@example.com",
        "password": "password123",
        "full_name": "Test User",
    }


@pytest.mark.asyncio
async def test_get_current_user(
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

    response = await client.get(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"]
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["role"] == "user"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_current_user_without_auth(
    client,
):

    response = await client.get(
        "/users/me"
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 401
    assert data["error"] == "UNAUTHORIZED"
    assert data["message"]


@pytest.mark.asyncio
async def test_update_current_user(
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

    response = await client.put(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "username": f"updated{uuid.uuid4().hex[:8]}",
            "full_name": "Updated User",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["full_name"] == "Updated User"
    assert data["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_update_user_without_auth(
    client,
):

    response = await client.put(
        "/users/me",
        json={
            "full_name": "Updated User",
        },
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 401
    assert data["error"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_update_user_without_fields(
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

    response = await client.put(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={},
    )

    assert response.status_code == 400

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 400
    assert data["error"] == "BAD_REQUEST"
    assert data["message"] == "No fields provided for update"


@pytest.mark.asyncio
async def test_update_user_invalid_data(
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

    response = await client.put(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "username": "",
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 422
    assert data["error"] == "VALIDATION_ERROR"
    assert data["message"] == "Invalid request data"


@pytest.mark.asyncio
async def test_update_user_duplicate_username(
    client,
):

    first_user = create_user_data()

    first_register = await client.post(
        "/auth/register",
        json=first_user,
    )

    assert first_register.status_code == 201

    second_user = create_user_data()

    second_register = await client.post(
        "/auth/register",
        json=second_user,
    )

    assert second_register.status_code == 201

    login_response = await client.post(
        "/auth/login",
        json={
            "email": second_user["email"],
            "password": second_user["password"],
        },
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = await client.put(
        "/users/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        },
        json={
            "username": first_user["username"],
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 409
    assert data["error"] == "CONFLICT"
    assert data["message"] == "Username already registered"