import pytest

from midgard_discord import commands
from midgard_discord import texts


@pytest.mark.asyncio
async def test_add_keypair_user_not_existed(
    ctx, openstackclient, public_key, find_user_db_patch_none
):
    """
    Test the add_keypair command with user not existed.

    The command should not find a user in the database.
    The command should send a message that the user is not registered.
    """
    user = find_user_db_patch_none.return_value
    await commands.add_keypair(ctx, user, openstackclient, public_key)

    ctx.send.assert_called_once_with(
        texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id),
        suppress_embeds=True,
    )


@pytest.mark.asyncio
async def test_add_keypair_user_existed(
    ctx,
    openstackclient,
    public_key,
    find_user_db_patch_some_user,
    find_keypair_cloud_patch_none,
    create_keypair_cloud_patch,
):
    """
    Test the add_keypair command with user existed.

    The command should not find a keypair in the database.
    The command should set a keypair for the user in Nova.
    The command should send a message that the keypair is updated.
    """
    user = find_user_db_patch_some_user.return_value

    await commands.add_keypair(ctx, user, openstackclient, public_key)

    find_keypair_cloud_patch_none.assert_called_once_with(openstackclient)

    create_keypair_cloud_patch.assert_called_once_with(openstackclient, public_key)

    ctx.send.assert_called_once_with(
        texts.KEYPAIR_UPDATED.format(discord_user_id=ctx.author.user.id),
        suppress_embeds=True,
    )


@pytest.mark.asyncio
async def test_add_keypair_keypair_existed(
    ctx,
    openstackclient,
    public_key,
    find_user_db_patch_some_user,
    find_keypair_cloud_patch_some_keypair,
    delete_keypair_cloud_patch,
    create_keypair_cloud_patch,
):
    """
    Test the add_keypair command with keypair existed.

    The command should find a keypair in the database.
    The command should delete the keypair in the database.
    The command should set a keypair for the user in Nova.
    The command should send a message that the keypair is updated.
    """

    user = find_user_db_patch_some_user.return_value
    await commands.add_keypair(ctx, user, openstackclient, public_key)

    find_keypair_cloud_patch_some_keypair.assert_called_once_with(openstackclient)

    keypair = find_keypair_cloud_patch_some_keypair.return_value

    delete_keypair_cloud_patch.assert_called_once_with(openstackclient, keypair)
    create_keypair_cloud_patch.assert_called_once_with(openstackclient, public_key)

    ctx.send.assert_called_once_with(
        texts.KEYPAIR_UPDATED.format(discord_user_id=ctx.author.user.id),
        suppress_embeds=True,
    )
