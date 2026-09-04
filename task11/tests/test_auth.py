import uuid

import pytest


def create_user_data():

    unique_id = str(uuid.uuid4())[:8]

    return {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "Test@12345",
        "full_name": "Test User"
    }


@pytest.mark.asyncio
async def test_register_user(client):

    user_data = create_user_data()

    response = await client.post(
        "/auth/register",
        json=user_data
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"]
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["role"] == "user"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_duplicate_registration(client):

    user_data = create_user_data()

    first_response = await client.post(
        "/auth/register",
        json=user_data
    )

    assert first_response.status_code == 201

    second_response = await client.post(
        "/auth/register",
        json=user_data
    )

    assert second_response.status_code == 409

    data = second_response.json()

    assert data["success"] is False
    assert data["status_code"] == 409


@pytest.mark.asyncio
async def test_invalid_registration_data(client):

    response = await client.post(
        "/auth/register",
        json={}
    )

    assert response.status_code == 422

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 422
    assert data["error"] == "VALIDATION_ERROR"
    assert data["message"] == "Invalid request data"


@pytest.mark.asyncio
async def test_login_user(client):

    user_data = create_user_data()

    register_response = await client.post(
        "/auth/register",
        json=user_data
    )

    assert register_response.status_code == 201

    response = await client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_invalid_login(client):

    user_data = create_user_data()

    await client.post(
        "/auth/register",
        json=user_data
    )

    response = await client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": "WrongPassword@123"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 401


@pytest.mark.asyncio
async def test_login_with_unknown_email(client):

    response = await client.post(
        "/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "Test@12345"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 401


@pytest.mark.asyncio
async def test_login_invalid_request(client):

    response = await client.post(
        "/auth/login",
        json={}
    )

    assert response.status_code == 422

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 422
    assert data["error"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_refresh_token(client):

    user_data = create_user_data()

    register_response = await client.post(
        "/auth/register",
        json=user_data
    )

    assert register_response.status_code == 201

    login_response = await client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    assert login_response.status_code == 200

    login_data = login_response.json()

    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": login_data["refresh_token"]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_with_access_token(client):

    user_data = create_user_data()

    await client.post(
        "/auth/register",
        json=user_data
    )

    login_response = await client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    login_data = login_response.json()

    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": login_data["access_token"]
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["success"] is False
    assert data["status_code"] == 401


@pytest.mark.asyncio
async def test_logout_user(client):

    user_data = create_user_data()

    await client.post(
        "/auth/register",
        json=user_data
    )

    login_response = await client.post(
        "/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    login_data = login_response.json()

    response = await client.post(
        "/auth/logout",
        json={
            "refresh_token": login_data["refresh_token"]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["message"] == "Logged out successfully"