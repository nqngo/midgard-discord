import os
import pytest

from midgard_discord import commands
from midgard_discord import texts


@pytest.mark.asyncio
async def test_create_server_existing_server(
    ctx,
    openstackclient,
    flavor_id,
    image_id,
    find_user_db_patch_some_user,
    find_server_cloud_patch_some_server,
):
    """
    Test the create command with existing server.

    The create command should find the user in database.
    The create command should find the server in the cloud.
    The create command should send an already created message.
    """

    user = find_user_db_patch_some_user.return_value

    await commands.create_server(ctx, user, openstackclient, flavor_id, image_id)

    find_server_cloud_patch_some_server.assert_called_once()

    # The create command should send an already created message.
    ctx.send.assert_called_once_with(
        texts.ERROR_SERVER_ALREADY_EXISTS.format(
            discord_user_id=ctx.author.user.id,
            server_name=find_server_cloud_patch_some_server.return_value.name,
            server_ip=find_server_cloud_patch_some_server.return_value.addresses[
                "default"
            ][0]["addr"],
            hostname=f"{ctx.author.user.id}-ssh.{os.getenv('CF_DOMAIN')}",
        ),
        suppress_embeds=True,
    )


@pytest.mark.asyncio
async def test_create_server_user_not_existed(
    ctx,
    openstackclient,
    flavor_id,
    image_id,
    find_user_db_patch_none,
):
    """
    Test the create command with user not existed.

    The create command should not find the user in database.
    The create command should send a message that the user is not registered.
    """
    user = find_user_db_patch_none.return_value

    await commands.create_server(ctx, user, openstackclient, flavor_id, image_id)

    ctx.send.assert_called_once_with(
        texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id),
        suppress_embeds=True,
    )


@pytest.mark.asyncio
async def test_create_server(
    ctx,
    openstackclient,
    flavor_id,
    image_id,
    find_user_db_patch_some_user,
    find_server_cloud_patch_none,
    create_server_cloud_patch,
    add_security_group_rule_cloud_patch,
    get_tunnel_config_networking_patch,
    add_tunnel_config_networking_patch,
    update_tunnel_config_networking_patch,
    create_dns_record_networking_patch,
):
    """
    Test the create command with server not existed.

    The create command should find the user in database.
    The create command should not find the server in the cloud.
    The create command should create a new server in the cloud.
    The create command should add ssh to the security group.
    The create command should set the portforwarding rules for SSH at Cloudflare.
    The create command should send a created message.
    """

    user = find_user_db_patch_some_user.return_value

    await commands.create_server(ctx, user, openstackclient, flavor_id, image_id)

    # Create a new server
    find_server_cloud_patch_none.assert_called_once()
    create_server_cloud_patch.assert_called_once()
    add_security_group_rule_cloud_patch.assert_called_once_with(openstackclient, 22)
    # Add portforwarding rules for SSH at Cloudflare.
    create_dns_record_networking_patch.assert_called_once()
    get_tunnel_config_networking_patch.assert_called_once()
    add_tunnel_config_networking_patch.assert_called_once()
    update_tunnel_config_networking_patch.assert_called_once()

    # The create command should send a created message.
    ctx.send.assert_called_once_with(
        texts.SERVER_CREATED.format(
            discord_user_id=ctx.author.user.id,
            server_name=create_server_cloud_patch.return_value.name,
            server_ip=create_server_cloud_patch.return_value.addresses["default"][0][
                "addr"
            ],
            hostname=f"{user.username}-ssh.{os.getenv('CF_DOMAIN')}",
        ),
        suppress_embeds=True,
    )
