import os

import interactions

from dotenv import load_dotenv

from midgard_discord import cloud
from midgard_discord import commands
from midgard_discord import database
from midgard_discord import networking
from midgard_discord import texts


# Setup discord API
load_dotenv()

CACHE_TTL = os.getenv("DB_CACHE_TTL")
bot = interactions.Client(
    token=os.getenv("DISCORD_TOKEN"),
    default_scope=os.getenv("DISCORD_DEFAULT_GUILD_ID").split(","),
)


@bot.event
async def on_ready():
    """This event is called when the bot is ready to start accepting commands."""
    print(f"We're online! We've logged in as {bot.me.name}.")
    print(f"Our latency is {round(bot.latency)} ms.")


@bot.command(name="midgard")
async def midgard(ctx: interactions.CommandContext):
    """Midgard group command"""
    pass


@midgard.subcommand(name="help", description="Get help with Midgard")
async def help(ctx: interactions.CommandContext):
    """Get help with Midgard"""
    await commands.help(ctx)


@midgard.subcommand(name="register", description="Register an account in Midgard")
@interactions.autodefer(delay=2.5)
async def register(ctx: interactions.CommandContext):
    """Request enrolment to Midgard"""
    db_engine, db_session = await database.init_async_db(os.getenv("DB_URI"))
    os_client = cloud.connect()

    await commands.register(ctx, db_session, os_client)

    # Close database connection
    await db_engine.dispose()
    os_client.close()


@midgard.group(name="add")
async def add(ctx: interactions.CommandContext):
    """Set group command"""
    pass


@add.subcommand(
    name="keypair",
    description="Add your SSH-public key in Midgard",
    options=[
        interactions.Option(
            name="public_key",
            description="Your SSH public key",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def keypair(ctx: interactions.CommandContext, public_key: str):
    """Set your SSH-public key in Midgard"""
    db_engine, db_session = await database.init_async_db(os.getenv("DB_URI"))
    user = await database.find_user(db_session, str(ctx.author.user.id))

    if user is None:
        await ctx.send(
            texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id)
        )
    else:
        os_client = cloud.connect(
            auth_url=os.getenv("OS_AUTH_URL"),
            region_name=os.getenv("OS_REGION_NAME"),
            project_name=user.project_name,
            username=user.username,
            password=user.password,
            user_domain=os.getenv("OS_USER_DOMAIN_NAME"),
            project_domain=os.getenv("OS_PROJECT_DOMAIN_NAME"),
        )

        keypair = await cloud.find_keypair(os_client)
        # Create a new keypair if it doesn't exist
        if keypair is None:
            try:
                await cloud.create_keypair(os_client, public_key)
                await ctx.send(
                    f"<@{ctx.author.user.id}> Your public key has been updated!"
                )
            except Exception as e:
                await ctx.send(f"<@{ctx.author.user.id}> {e}")
        # Update the keypair if it exists
        else:
            await cloud.delete_keypair(os_client, keypair)
            try:
                await cloud.create_keypair(os_client, public_key)
                await ctx.send(
                    f"<@{ctx.author.user.id}> Your public key has been updated!"
                )
            except Exception as e:
                await ctx.send(f"<@{ctx.author.user.id}> {e}")
    # Close database connection
    await db_engine.dispose()
    os_client.close()


@add.subcommand(
    name="portforward",
    description="Add port forwarding rules in Midgard",
    options=[
        interactions.Option(
            name="port",
            description="The port you want to forward",
            type=interactions.OptionType.INTEGER,
            required=True,
        ),
        interactions.Option(
            name="protocol",
            description="The protocol you want to forward",
            type=interactions.OptionType.STRING,
            choices=[
                interactions.Choice(name="TCP", value="tcp"),
                interactions.Choice(name="HTTP", value="http"),
                interactions.Choice(name="SSH", value="ssh"),
            ],
            default="http",
        ),
    ],
)
async def portforward(
    ctx: interactions.CommandContext, port: int, protocol: str = "http"
):
    """Add port forwarding rules to security group in Midgard"""
    db_engine, db_session = await database.init_async_db(os.getenv("DB_URI"))
    user = await database.find_user(db_session, str(ctx.author.user.id))

    if user is None:
        await ctx.send(
            texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id)
        )
    else:
        os_client = cloud.connect(
            auth_url=os.getenv("OS_AUTH_URL"),
            region_name=os.getenv("OS_REGION_NAME"),
            project_name=user.project_name,
            username=user.username,
            password=user.password,
            user_domain=os.getenv("OS_USER_DOMAIN_NAME"),
            project_domain=os.getenv("OS_PROJECT_DOMAIN_NAME"),
        )

        server = await cloud.find_server(os_client)
        if server is None:
            await ctx.send(
                texts.ERROR_SERVER_NOT_FOUND.format(discord_user_id=ctx.author.user.id)
            )
        else:
            try:
                tunnels = await networking.get_tunnel_config()
                await cloud.add_security_group_rule(os_client, port)
                public_ip = [
                    ip["addr"]
                    for ip in server.addresses["default"]
                    if ip["OS-EXT-IPS:type"] == "floating"
                ][0]
                service = f"{protocol}://{public_ip}:{port}"
                hostname = f"{user.username}-{protocol}-{port}"
                networking.add_tunnel_config(tunnels, service, hostname)
                await networking.update_tunnel_config(tunnels)
                await networking.create_dns_record(hostname)
                await ctx.send(
                    f"<@{ctx.author.user.id}> Port forwarding rule has been added!",
                    ephemeral=True,
                )
            except Exception as e:
                await ctx.send(f"<@{ctx.author.user.id}> {e}")

    # Close database connection
    await db_engine.dispose()
    os_client.close()


# @add.subcommand(
#     name="dns",
#     description="Add a DNS tunnel to your server",
#     options=[
#         interactions.Option(
#             name="hostname",
#             description="The hostname you want to forward",
#             type=interactions.OptionType.STRING,
#             required=True,
#         ),
#         interactions.Option(
#             name="port",
#             description="The port you want to forward",
#             type=interactions.OptionType.INTEGER,
#             required=True,
#         ),
#         interactions.Option(
#             name="protocol",
#             description="The protocol you want to forward",
#             type=interactions.OptionType.STRING,
#             choices=[
#                 interactions.Choice(name="TCP", value="tcp"),
#                 interactions.Choice(name="HTTP", value="http"),
#                 interactions.Choice(name="SSH", value="ssh"),
#             ],
#             default="http",
#         ),
#     ],
# )
async def add_dns(
    ctx: interactions.CommandContext, hostname: str, port: int, protocol: str = "http"
):
    """Add a DNS tunnel to your server"""

    db_engine, db_session = await database.init_async_db(os.getenv("DB_URI"))
    user = await database.find_user(db_session, str(ctx.author.user.id))

    if user is None:
        await ctx.send(
            texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id)
        )
    else:
        tunnels = await networking.get_tunnel_config()

        try:
            os_client = cloud.connect(
                auth_url=os.getenv("OS_AUTH_URL"),
                region_name=os.getenv("OS_REGION_NAME"),
                project_name=user.project_name,
                username=user.username,
                password=user.password,
                user_domain=os.getenv("OS_USER_DOMAIN_NAME"),
                project_domain=os.getenv("OS_PROJECT_DOMAIN_NAME"),
            )

            server = await cloud.find_server(os_client)
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
                f"<@{ctx.author.user.id}> DNS tunnel has been added to your server!",
                ephemeral=True,
            )
        except Exception as e:
            await ctx.send(f"<@{ctx.author.user.id}> {e}")

    # Close database connection
    await db_engine.dispose()
    os_client.close()


@midgard.group(name="server")
async def server(ctx: interactions.CommandContext):
    """Server group command"""
    pass


@server.subcommand(
    name="launch",
    description="Create a VM server",
    options=[
        interactions.Option(
            name="flavor",
            description="The flavor of the server",
            type=interactions.OptionType.STRING,
            required=True,
            autocomplete=True,
        ),
        interactions.Option(
            name="image",
            description="The image of the server",
            type=interactions.OptionType.STRING,
            required=True,
            autocomplete=True,
        ),
    ],
)
@interactions.autodefer()
async def server_launch(ctx: interactions.CommandContext, flavor: str, image: str):
    """Create a VM server"""
    db_engine, db_session = await database.init_async_db(os.getenv("DB_URI"))
    user = await database.find_user(db_session, str(ctx.author.user.id))

    if user is None:
        await ctx.send(
            texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id)
        )
    else:
        os_client = cloud.connect(
            auth_url=os.getenv("OS_AUTH_URL"),
            region_name=os.getenv("OS_REGION_NAME"),
            project_name=user.project_name,
            username=user.username,
            password=user.password,
            user_domain=os.getenv("OS_USER_DOMAIN_NAME"),
            project_domain=os.getenv("OS_PROJECT_DOMAIN_NAME"),
        )

        server = await cloud.find_server(os_client)
        if server is not None:
            if server.status == "ACTIVE":
                await ctx.send(
                    f"<@{ctx.author.user.id}> Your server is already running."
                )
            else:
                await ctx.send(
                    f"<@{ctx.author.user.id}> Your server is in STATUS {server.status}."
                )
        else:
            keypair = await cloud.find_keypair(os_client)
            security_group = await cloud.find_default_security_group(os_client)
            try:
                # Check if keypair exists
                if keypair is None:
                    raise Exception(
                        texts.ERROR_KEYPAIR_NOT_FOUND.format(
                            discord_user_id=ctx.author.user.id
                        )
                    )
                # Create a Nova server
                server = await cloud.create_server(
                    os_client,
                    key_name=keypair.name,
                    flavor=flavor,
                    image=image,
                    auto_ip=True,
                    security_groups=[security_group.name],
                    reuse_ips=True,
                    wait=True,
                )
                # Set up SSH tunnel
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
                        server_id=server.id,
                        hostname=hostname,
                    ),
                    ephemeral=True,
                )
            except Exception as e:
                await ctx.send(f"<@{ctx.author.user.id}> {e}")

    # Close database connection
    await db_engine.dispose()
    os_client.close()


@server_launch.autocomplete("flavor")
async def server_launch_flavor_autocomplete(
    ctx: interactions.CommandContext, user_input: str = ""
):
    """Autocomplete for create server flavor"""
    db_engine, db_session = await database.init_async_db(os.getenv("DB_URI"))
    user = await database.find_user(db_session, str(ctx.author.user.id))

    if user is None:
        await ctx.send(
            texts.ERROR_NOT_REGISTERED.format(discord_user_id=ctx.author.user.id)
        )
        return

    os_client = cloud.connect(
        auth_url=os.getenv("OS_AUTH_URL"),
        region_name=os.getenv("OS_REGION_NAME"),
        project_name=user.project_name,
        username=user.username,
        password=user.password,
        user_domain=os.getenv("OS_USER_DOMAIN_NAME"),
        project_domain=os.getenv("OS_PROJECT_DOMAIN_NAME"),
    )

    flavors = await cloud.list_flavors(os_client)

    choices = [
        interactions.Choice(
            name=f"{flavor.name} ({flavor.vcpus} vCPUs, {flavor.ram/1024}GB RAM, {flavor.disk}GB HDD)",
            value=flavor.id,
        )
        for flavor in flavors
        if user_input in flavor.name and flavor.vcpus <= 2
    ]
    # Close database connection
    await db_engine.dispose()
    os_client.close()
    await ctx.populate(choices)


@server_launch.autocomplete("image")
async def server_launch_image_autocomplete(
    ctx: interactions.CommandContext, user_input: str = ""
):
    """Autocomplete for create server image"""
    db_engine, db_session = await database.init_async_db(os.getenv("DB_URI"))
    user = await database.find_user(db_session, str(ctx.author.user.id))

    os_client = cloud.connect(
        auth_url=os.getenv("OS_AUTH_URL"),
        region_name=os.getenv("OS_REGION_NAME"),
        project_name=user.project_name,
        username=user.username,
        password=user.password,
        user_domain=os.getenv("OS_USER_DOMAIN_NAME"),
        project_domain=os.getenv("OS_PROJECT_DOMAIN_NAME"),
    )

    images = await cloud.list_images(os_client)

    choices = [
        interactions.Choice(name=image.name, value=image.id)
        for image in images
        if user_input in image.name
    ]
    # Close database connection
    await db_engine.dispose()
    os_client.close()
    await ctx.populate(choices)


def main():
    """Main function"""
    bot.start()


if __name__ == "__main__":
    """Run main function"""
    main()
