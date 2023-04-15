import pytest

import interactions

from unittest.mock import AsyncMock
from midgard_discord import commands
from midgard_discord import texts


@pytest.fixture
def ctx():
    """Return a mock context."""
    return AsyncMock(interactions.CommandContext)


@pytest.mark.asyncio
async def test_help(ctx):
    """
    Test the help command.

    The help command should send a welcome message.
    """
    await commands.help(ctx)
    ctx.send.assert_called_once_with(texts.WELCOME, suppress_embeds=True)
