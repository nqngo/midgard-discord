import datetime
import pytest
from midgard_discord.database import init_async_db, find_user, create_user

TEST_DB_URI = "sqlite+aiosqlite:///:memory:"


@pytest.mark.asyncio
async def test_init_async_db():
    engine, async_session = await init_async_db(TEST_DB_URI)
    assert engine is not None
    assert async_session is not None
    await engine.dispose()


@pytest.mark.asyncio
async def test_find_user_no_result():
    engine, async_session = await init_async_db(TEST_DB_URI)
    result = await find_user(async_session, "non_existent_user")
    assert result is None
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_find_user():
    discord_user_id = "test_user"
    password = "test_password"
    project_name = "test_project"
    engine, async_session = await init_async_db(TEST_DB_URI)
    # Check that the user has not existed yet
    result = await find_user(async_session, discord_user_id)
    assert result is None
    # Create the user
    await create_user(
        async_session, discord_user_id, password=password, project_name=project_name
    )
    # Check that the user has been created
    result = await find_user(async_session, discord_user_id)
    assert result is not None
    assert result.username == discord_user_id
    assert result.password == password
    assert result.project_name == project_name
    assert result.created_at is not None
    assert result.updated_at is not None
    now = datetime.datetime.now()
    assert now > result.created_at
    assert now > result.updated_at
    await engine.dispose()
