import os
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest")
os.environ.setdefault("UPLOAD_FOLDER", "uploads")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "postgres")
os.environ.setdefault("POSTGRES_DB", "rag")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_HOST", "localhost")


@pytest.fixture
def sample_user_id():
    return uuid4()


@pytest.fixture
def sample_user(sample_user_id):
    user = MagicMock()
    user.id = sample_user_id
    user.email = "test@example.com"
    return user


@pytest.fixture
def sample_api_key(sample_user_id):
    api_key = MagicMock()
    api_key.user_id = sample_user_id
    api_key.api_key = "ari-api-test-key"
    api_key.is_deleted = False
    api_key.is_active = True
    return api_key


@pytest.fixture
def mock_db_session():
    return AsyncMock()


def mock_scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result
