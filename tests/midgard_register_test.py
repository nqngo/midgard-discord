import pytest
import openstack
import interactions

from unittest.mock import MagicMock, AsyncMock, patch
from midgard_discord import commands
from midgard_discord import texts


@pytest.fixture
def ctx():
    """Return a mock context."""
    return AsyncMock(interactions.CommandContext)


@pytest.mark.asyncio
@patch("midgard_discord.database.find_user", return_value=None)
@patch("midgard_discord.cloud.find_user", return_value=None)
@patch("midgard_discord.database.create_user")
async def test_register_new_user(ctx, *args):
    """
    Test the register command with new user.

    The register command should create a new project in Keystone.
    The register command should create a new user in Keystone.
    The register command should create a new router in Neutron.
    The register command should create network and subnet in Neutron.
    The register command should create a new user in the database.
    The register command should send a registered message.
    """
    async_session = MagicMock()
    openstackclient = AsyncMock(openstack.connection.Connection)
    # TODO The register command should create a new project in Keystone.
    # TODO The register command should create a new user in Keystone.
    # TODO The register command should create a new router in Neutron.
    # TODO The register command should create network and subnet in Neutron.
    # TODO The register command should create a new user in the database.
    # The register command should send a registered message.
    await commands.register(ctx, async_session, openstackclient)
    ctx.send.assert_called_once_with(
        texts.REGISTERED.format(discord_user_id=ctx.author.user.id)
    )


@pytest.mark.asyncio
@patch("midgard_discord.database.find_user", return_value=None)
@patch("midgard_discord.database.create_user")
async def test_register_existing_user_no_cache(ctx, *args):
    """
    Test the register command with existing user in Keystone but not in cache.

    The register command should not create a new project in Keystone.
    The register command should not create a new user in the database.
    The register command should update the user in Keystone.
    The register command should create a new user in the database.
    The register command should send a registered message.
    """
    async_session = MagicMock()
    openstackclient = AsyncMock(openstack.connection.Connection)
    await commands.register(ctx, async_session, openstackclient)
    # TODO The register command should not create a new project in Keystone.
    # TODO The register command should not create a new user in the database.
    # TODO The register command should update the user in Keystone.
    # TODO The register command should create a new user in the database.
    # The register command should send a registered message
    ctx.send.assert_called_once_with(
        texts.REGISTERED.format(discord_user_id=ctx.author.user.id)
    )


@pytest.mark.asyncio
@patch("midgard_discord.database.find_user", return_value="user")
async def test_register_existing_user(ctx):
    """
    Test the register command with existing user.

    The register command should send an already registered message.
    """
    async_session = MagicMock()
    openstackclient = AsyncMock(openstack.connection.Connection)
    await commands.register(ctx, async_session, openstackclient)
    # The register command should send an already registered message.
    ctx.send.assert_called_once_with(
        texts.ERROR_REGISTERED.format(discord_user_id=ctx.author.user.id)
    )
