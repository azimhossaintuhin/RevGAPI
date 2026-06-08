from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.core.jwt_auth import create_access_token, verify_token
from src.dependencies.get_user import get_current_user


def test_get_current_user_with_valid_token(sample_user_id):
    token = create_access_token(
        {"user_id": sample_user_id, "email": "test@example.com"}
    )

    user_id = get_current_user(token=token)

    assert str(user_id) == str(sample_user_id)


def test_get_current_user_with_invalid_token():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token="not-a-valid-token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


def test_get_current_user_with_missing_user_id():
    with patch(
        "src.dependencies.get_user.verify_token",
        return_value={"user_id": None, "email": "test@example.com"},
    ):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token="fake-token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


def test_verify_token_round_trip(sample_user_id):
    token = create_access_token(
        {"user_id": sample_user_id, "email": "test@example.com"}
    )
    payload = verify_token(token)

    assert payload["email"] == "test@example.com"
    assert payload["user_id"] == str(sample_user_id)
