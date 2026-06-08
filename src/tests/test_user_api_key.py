from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from src.dependencies.user_api_key import get_user_api_key


def mock_scalar_result(value):
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


@pytest.mark.asyncio
async def test_get_user_api_key_valid(mock_db_session, sample_api_key, sample_user):
    mock_db_session.execute = AsyncMock(
        side_effect=[
            mock_scalar_result(sample_api_key),
            mock_scalar_result(sample_user),
        ]
    )

    user = await get_user_api_key(api_key=sample_api_key.api_key, db=mock_db_session)

    assert user is sample_user
    assert mock_db_session.execute.await_count == 2


@pytest.mark.asyncio
async def test_get_user_api_key_invalid_key(mock_db_session):
    mock_db_session.execute = AsyncMock(return_value=mock_scalar_result(None))

    with pytest.raises(HTTPException) as exc_info:
        await get_user_api_key(api_key="wrong-key", db=mock_db_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid API Key"


@pytest.mark.asyncio
async def test_get_user_api_key_deleted(mock_db_session, sample_api_key):
    sample_api_key.is_deleted = True
    mock_db_session.execute = AsyncMock(return_value=mock_scalar_result(sample_api_key))

    with pytest.raises(HTTPException) as exc_info:
        await get_user_api_key(api_key=sample_api_key.api_key, db=mock_db_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "API Key is deleted"


@pytest.mark.asyncio
async def test_get_user_api_key_inactive(mock_db_session, sample_api_key):
    sample_api_key.is_active = False
    mock_db_session.execute = AsyncMock(return_value=mock_scalar_result(sample_api_key))

    with pytest.raises(HTTPException) as exc_info:
        await get_user_api_key(api_key=sample_api_key.api_key, db=mock_db_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "API Key is deleted"


@pytest.mark.asyncio
async def test_get_user_api_key_user_not_found(mock_db_session, sample_api_key):
    mock_db_session.execute = AsyncMock(
        side_effect=[
            mock_scalar_result(sample_api_key),
            mock_scalar_result(None),
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_user_api_key(api_key=sample_api_key.api_key, db=mock_db_session)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User not found"
