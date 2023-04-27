import pytest

from midgard_discord import commands
from midgard_discord import texts


@pytest.mark.asyncio
async def test_register_existing_user(
    ctx,
    session,
    openstackclient,
    find_user_db_patch_some_user,
    find_user_cloud_patch_some_user,
):
    """
    Test the register command with existing user.

    The register command should find the user in database.
    The register command should send an already registered message.
    """
    await commands.register(ctx, session, openstackclient)

    find_user_db_patch_some_user.assert_called_once()

    find_user_cloud_patch_some_user.assert_not_called()

    # The register command should send an already registered message.
    ctx.send.assert_called_once_with(
        texts.ERROR_REGISTERED.format(discord_user_id=ctx.author.user.id),
        suppress_embeds=True,
    )


@pytest.mark.asyncio
async def test_register_existing_user_no_cache(
    ctx,
    session,
    openstackclient,
    find_user_db_patch_none,
    find_user_cloud_patch_some_user,
    update_user_cloud_patch,
    create_user_db_patch,
):
    """
    Test the register command with existing user in Keystone but not in cache.

    The register command should not find the user in database.
    The register command should find the user in the Keystone.
    The register command should update the user password in Keystone.
    The register command should create a new user in the database.
    The register command should send a registered message.
    """
    await commands.register(ctx, session, openstackclient)

    # The register command should not find the user in database.
    find_user_db_patch_none.assert_called_once()

    # The register command should find the user in the Keystone.
    find_user_cloud_patch_some_user.assert_called_once()

    # The register command should update the user password in Keystone.
    update_user_cloud_patch.assert_called_once()

    # The register command should create a new user in the database.
    create_user_db_patch.assert_called_once()

    # The register command should send a registered message
    ctx.send.assert_called_once_with(
        texts.REGISTERED.format(discord_user_id=ctx.author.user.id),
        suppress_embeds=True,
    )


@pytest.mark.asyncio
async def test_register_new_user(
    ctx,
    session,
    openstackclient,
    find_user_db_patch_none,
    create_user_db_patch,
    find_user_cloud_patch_none,
    create_project_cloud_patch,
    create_user_cloud_patch,
    setup_default_network_patch,
    create_security_group_cloud_patch,
):
    """
    Test the register command with new user.

    The register command should not find the user in the database.
    The register command should not find the user in Keystone.
    The register command should create a new project in Keystone.
    The register command should create a new user in Keystone.
    The register command should create setup the default network in Neutron.
    The register command should create a security group in Neutron.
    The register command should create a new user in the database.
    The register command should send a registered message.
    """
    await commands.register(ctx, session, openstackclient)

    # The register command should not find the user in the database.
    find_user_db_patch_none.assert_called_once()

    # The register command should not find the user in Keystone.
    find_user_cloud_patch_none.assert_called_once()

    # The register command should create a new project in Keystone.
    create_project_cloud_patch.assert_called_once()

    # The register command should create a new user in Keystone.
    create_user_cloud_patch.assert_called_once()

    # The register command should create setup the default network in Neutron.
    setup_default_network_patch.assert_called_once()

    # The register command should create a security group in Neutron.
    create_security_group_cloud_patch.assert_called_once()

    # The register command should create a new user in the database.
    create_user_db_patch.assert_called_once()

    # The register command should send a registered message.
    ctx.send.assert_called_once_with(
        texts.REGISTERED.format(discord_user_id=ctx.author.user.id),
        suppress_embeds=True,
    )
