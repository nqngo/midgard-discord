import pytest
import openstack
import interactions

from unittest.mock import MagicMock, AsyncMock, patch
from midgard_discord import commands
from midgard_discord import texts


# @pytest.mark.asyncio
# async def test_add_keypair_user_not_existed(ctx):
#     """
#     Test the add_keypair command with user not existed.
#     """
#     async_session = MagicMock()
#     openstackclient = AsyncMock(openstack.connection.Connection)
#     await commands.add_keypair(ctx, async_session, openstackclient)
#     ctx.send.assert_called_once_with(
#         texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id)
#     )


# @pytest.mark.asyncio
# @patch("midgard_discord.database.find_user")
# async def test_add_keypair_user_existed():
#     """
#     Test the add_keypair command with user existed.
#     """
#     async_session = MagicMock()
#     openstackclient = AsyncMock(openstack.connection.Connection)
#     await commands.add_keypair(ctx, async_session, openstackclient)
#     ctx.send.assert_called_once_with(
#         texts.KEYPAIR_UPDATED.format(discord_user_id=ctx.author.user.id)
#     )


# @pytest.mark.asyncio
# @patch("midgard_discord.database.find_user")
# @patch("midgard_discord.database.create_user")
# async def test_add_keypair_keypair_existed():
#     """
#     Test the add_keypair command with keypair existed.
#     """
#     async_session = MagicMock()
#     openstackclient = AsyncMock(openstack.connection.Connection)
#     await commands.add_keypair(ctx, async_session, openstackclient)
#     ctx.send.assert_called_once_with(
#         texts.KEYPAIR_UPDATED.format(discord_user_id=ctx.author.user.id)
#     )
