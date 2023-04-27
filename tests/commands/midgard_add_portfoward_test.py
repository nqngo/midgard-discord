import os
import pytest

from midgard_discord import commands
from midgard_discord import texts


@pytest.mark.asyncio
async def test_add_portforward_user_not_existed(
    ctx, openstackclient, http_port, http_protocol, find_user_db_patch_none
):
    """
    Test the add_portforward command with user not existed.

    The command should not find a user in the database.
    The command should send a message that the user is not registered.
    """
    user = find_user_db_patch_none.return_value
    await commands.add_portforward(ctx, user, openstackclient, http_port, http_protocol)

    ctx.send.assert_called_once_with(
        texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id),
        suppress_embeds=True,
    )


@pytest.mark.asyncio
async def test_add_portforward_server_not_existed(
    ctx,
    openstackclient,
    http_protocol,
    http_port,
    find_user_db_patch_some_user,
    find_server_cloud_patch_none,
):
    """
    Test the add_portforward command with user existed but server not existed.

    The command should find a user in the database.
    The command should not find a server in the cloud.
    The command should send a message that the server is not found.
    """
    user = find_user_db_patch_some_user.return_value

    await commands.add_portforward(ctx, user, openstackclient, http_port, http_protocol)

    find_server_cloud_patch_none.assert_called_once_with(openstackclient)

    ctx.send.assert_called_once_with(
        texts.ERROR_SERVER_NOT_FOUND.format(discord_user_id=ctx.author.user.id),
        suppress_embeds=True,
    )


@pytest.mark.asyncio
async def test_add_portforward(
    ctx,
    openstackclient,
    http_protocol,
    http_port,
    find_user_db_patch_some_user,
    find_server_cloud_patch_some_server,
    add_security_group_rule_cloud_patch,
    get_tunnel_config_networking_patch,
    add_tunnel_config_networking_patch,
    update_tunnel_config_networking_patch,
    create_dns_record_networking_patch,
):
    """
    Test the add_portforward command with user and server existed.

    The command should find a user in the database.
    The command should find a server in the cloud.
    The command should add a security group rule in the cloud.
    The command should get the tunnel config in networking.
    The command should create a DNS record in networking.
    The command should create a Cloudflare tunnel in networking.
    The command should send a message that the portforward is created.
    """
    user = find_user_db_patch_some_user.return_value

    await commands.add_portforward(ctx, user, openstackclient, http_port, http_protocol)

    find_server_cloud_patch_some_server.assert_called_once_with(openstackclient)

    add_security_group_rule_cloud_patch.assert_called_once_with(
        openstackclient, http_port
    )

    create_dns_record_networking_patch.assert_called_once()
    get_tunnel_config_networking_patch.assert_called_once()
    add_tunnel_config_networking_patch.assert_called_once()
    update_tunnel_config_networking_patch.assert_called_once()

    ctx.send.assert_called_once_with(
        texts.PORT_FORWARDED.format(
            discord_user_id=ctx.author.user.id,
            port=http_port,
            protocol=http_protocol,
            server_ip=find_server_cloud_patch_some_server.return_value.addresses[
                "default"
            ][0]["addr"],
            hostname=f"{user.username}-{http_protocol}-{http_port}.{os.getenv('CF_DOMAIN')}",
        ),
        emphemeral=True,
        suppress_embeds=True,
    )
