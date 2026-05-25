# Internal commands module for Midgard Discord Bot
import os
import interactions
import openstack
import sqlalchemy

from midgard_discord import cloud
from midgard_discord import database
from midgard_discord import networking
from midgard_discord import texts
from midgard_discord import utils


async def help(ctx: interactions.CommandContext):
    """Send a welcome message."""
    await ctx.send(texts.WELCOME, suppress_embeds=True)


async def register(
    ctx: interactions.CommandContext,
    db_session: sqlalchemy.ext.asyncio.async_sessionmaker,
    os_client: openstack.connection.Connection,
):
    """Register a user to Midgard."""
    user = await database.find_user(db_session, str(ctx.author.user.id))

    project_name = f"{os.getenv('OS_DEFAULT_GUILD_PREFIX')}_{ctx.author.user.id}"
    # If we miss the cache, check the database
    if user is None:
        os_user = await cloud.find_user(os_client, str(ctx.author.user.id))
        # If we miss the database, create the user
        if os_user is None:
            # Create user and project in OpenStack
            os_project = await cloud.create_project(os_client, project_name)
            user_password = utils.generate_password()
            os_user = await cloud.create_user(
                os_client,
                str(ctx.author.user.id),
                default_project=os_project,
                password=user_password,
            )

            # # Set roles
            await cloud.set_default_roles(os_client, os_user, os_project)

            # Setup default network
            await cloud.setup_default_network(os_client, os_project)

            # Create security group
            await cloud.create_security_group(os_client, os_project)

            # Cache user in database
            await database.create_user(
                db_session,
                str(ctx.author.user.id),
                password=user_password,
                project_name=project_name,
            )
        # If we find the user in OpenStack, reset the password and cache it in database
        else:
            user_password = utils.generate_password()
            await cloud.update_user(os_client, os_user, password=user_password)
            project = await cloud.find_project(os_client, project_name)
            await database.create_user(
                db_session,
                str(ctx.author.user.id),
                password=user_password,
                project_name=project.name,
            )
        await ctx.send(
            texts.REGISTERED.format(discord_user_id=ctx.author.user.id),
            suppress_embeds=True,
        )
    else:
        await ctx.send(
            texts.ERROR_REGISTERED.format(discord_user_id=ctx.author.user.id),
            suppress_embeds=True,
        )


async def add_keypair(
    ctx: interactions.CommandContext,
    user: database.OpenStackCredential,
    os_client: openstack.connection.Connection,
    public_key: str,
):
    """Add a keypair to a user."""
    if user is None:
        await ctx.send(
            texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id),
            suppress_embeds=True,
        )
    else:
        keypair = await cloud.find_keypair(os_client)
        # Create a new keypair if it doesn't exist
        if keypair is None:
            try:
                await cloud.create_keypair(os_client, public_key)
                await ctx.send(
                    texts.KEYPAIR_UPDATED.format(discord_user_id=ctx.author.user.id),
                    suppress_embeds=True,
                )
            except Exception as e:
                await ctx.send(f"<@{ctx.author.user.id}> {e}")
        # Update the keypair if it exists
        else:
            await cloud.delete_keypair(os_client, keypair)
            try:
                await cloud.create_keypair(os_client, public_key)
                await ctx.send(
                    texts.KEYPAIR_UPDATED.format(discord_user_id=ctx.author.user.id),
                    suppress_embeds=True,
                )
            except Exception as e:
                await ctx.send(f"<@{ctx.author.user.id}> {e}")


async def add_cname(
    ctx: interactions.CommandContext,
    user: database.OpenStackCredential,
    os_client: openstack.connection.Connection,
    hostname: str,
    port: int,
    protocol: str = "http",
):
    """Add a DNS tunnel to your server"""

    if user is None:
        return await ctx.send(
            texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id)
        )
    server = await cloud.find_server(os_client)
    if server is None:
        return await ctx.send(
            texts.ERROR_SERVER_NOT_FOUND.format(discord_user_id=ctx.author.user.id),
            suppress_embeds=True,
        )
    try:
        tunnels = await networking.get_tunnel_config()
        public_ip = [
            ip["addr"]
            for ip in server.addresses["default"]
            if ip["OS-EXT-IPS:type"] == "floating"
        ][0]
        service = f"{protocol}://{public_ip}:{port}"
        networking.add_tunnel_config(tunnels, service, hostname)
        await networking.update_tunnel_config(tunnels)
        await networking.create_dns_record(hostname)
        await ctx.send(
            texts.CNAME_ADDED.format(discord_user_id=ctx.author.user.id),
            ephemeral=True,
            suppress_embeds=True,
        )
    except Exception as e:
        await ctx.send(f"<@{ctx.author.user.id}> {e}")


async def add_portforward(
    ctx: interactions.CommandContext,
    user: database.OpenStackCredential,
    os_client: openstack.connection.Connection,
    port: int,
    protocol: str = "http",
):
    """Add a portforward to an instance."""
    if user is None:
        return await ctx.send(
            texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id),
            suppress_embeds=True,
        )
    server = await cloud.find_server(os_client)
    if server is None:
        return await ctx.send(
            texts.ERROR_SERVER_NOT_FOUND.format(discord_user_id=ctx.author.user.id),
            suppress_embeds=True,
        )
    try:
        tunnels = await networking.get_tunnel_config()
        await cloud.add_security_group_rule(os_client, port)
        public_ip = [
            ip["addr"]
            for ip in server.addresses["default"]
            if ip["OS-EXT-IPS:type"] == "floating"
        ][0]
        service = f"{protocol}://{public_ip}:{port}"
        hostname = f"{user.username}-{protocol}-{port}.{os.getenv('CF_DOMAIN')}"
        networking.add_tunnel_config(tunnels, service, hostname)
        await networking.update_tunnel_config(tunnels)
        await networking.create_dns_record(hostname)
        await ctx.send(
            texts.PORT_FORWARDED.format(
                discord_user_id=ctx.author.user.id,
                protocol=protocol,
                port=port,
                server_ip=public_ip,
                hostname=hostname,
            ),
            emphemeral=True,
            suppress_embeds=True,
        )
    except Exception as e:
        print(e)
        await ctx.send(f"<@{ctx.author.user.id}> {e}")


async def create_server(
    ctx: interactions.CommandContext,
    user: database.OpenStackCredential,
    os_client: openstack.connection.Connection,
    flavor_id: str,
    image_id: str,
):
    """Create a server."""
    if user is None:
        return await ctx.send(
            texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id),
            suppress_embeds=True,
        )
    server = await cloud.find_server(os_client)
    if server is not None:
        public_ip = [
            ip["addr"]
            for ip in server.addresses["default"]
            if ip["OS-EXT-IPS:type"] == "floating"
        ][0]
        return await ctx.send(
            texts.ERROR_SERVER_ALREADY_EXISTS.format(
                discord_user_id=ctx.author.user.id,
                server_name=server.name,
                server_ip=public_ip,
                hostname=f"{ctx.author.user.id}-ssh.{os.getenv('CF_DOMAIN')}",
            ),
            suppress_embeds=True,
        )
    keypair = await cloud.find_keypair(os_client)
    if keypair is None:
        return await ctx.send(
            texts.ERROR_KEYPAIR_NOT_FOUND.format(discord_user_id=ctx.author.user.id),
            suppress_embeds=True,
        )
    try:
        security_group = await cloud.find_default_security_group(os_client)
        server = await cloud.create_server(
            os_client,
            key_name=keypair.name,
            flavor=flavor_id,
            image=image_id,
            auto_ip=True,
            security_groups=[security_group.name],
            reuse_ips=True,
            wait=True,
        )
        tunnels = await networking.get_tunnel_config()
        await cloud.add_security_group_rule(os_client, 22)
        public_ip = [
            ip["addr"]
            for ip in server.addresses["default"]
            if ip["OS-EXT-IPS:type"] == "floating"
        ][0]
        service = f"ssh://{public_ip}:22"
        hostname = f"{user.username}-ssh.{os.getenv('CF_DOMAIN')}"
        networking.add_tunnel_config(tunnels, service, hostname)
        await networking.update_tunnel_config(tunnels)
        await networking.create_dns_record(hostname)
        await ctx.send(
            texts.SERVER_CREATED.format(
                discord_user_id=ctx.author.user.id,
                server_name=server.name,
                hostname=hostname,
            ),
            suppress_embeds=True,
        )
    except Exception as e:
        await ctx.send(f"<@{ctx.author.user.id}> {e}")


async def rebuild_server(
    ctx: interactions.CommandContext,
    user: database.OpenStackCredential,
    os_client: openstack.connection.Connection,
    flavor_id: str,
    image_id: str,
):
    """Rebuild a server."""
    if user is None:
        return await ctx.send(
            texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id),
            suppress_embeds=True,
        )
    server = await cloud.find_server(os_client)
    if server is None:
        return await ctx.send(
            texts.ERROR_SERVER_NOT_FOUND.format(discord_user_id=ctx.author.user.id),
            suppress_embeds=True,
        )
    try:
        await cloud.rebuild_server(os_client, flavor_id, image_id)
        await ctx.send(
            texts.SERVER_REBUILT.format(
                discord_user_id=ctx.author.user.id, server_name=server.name
            ),
            suppress_embeds=True,
        )
    except Exception as e:
        await ctx.send(f"<@{ctx.author.user.id}> {e}")
