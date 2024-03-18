import os

import interactions

from dotenv import load_dotenv

from midgard_discord import cloud
from midgard_discord import commands
from midgard_discord import database
from midgard_discord import texts
from midgard_discord import utils


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
    utils.log(ctx.author.name, "/midgard help")
    await commands.help(ctx)


@midgard.subcommand(name="register", description="Register an account in Midgard")
@interactions.autodefer(delay=2.5)
async def register(ctx: interactions.CommandContext):
    """Request enrolment to Midgard"""
    utils.log(ctx.author.name, "/midgard register")
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
async def add_keypair(ctx: interactions.CommandContext, public_key: str):
    """Set your SSH-public key in Midgard"""
    utils.log(ctx.author.name, f"/midgard add keypair public_key:{public_key}")
    db_engine, db_session = await database.init_async_db(os.getenv("DB_URI"))

    user = await database.find_user(db_session, str(ctx.author.user.id))
    os_client = (
        cloud.connect()
        if user is None
        else cloud.connect(
            auth_url=os.getenv("OS_AUTH_URL"),
            region_name=os.getenv("OS_REGION_NAME"),
            project_name=user.project_name,
            username=user.username,
            password=user.password,
            user_domain=os.getenv("OS_USER_DOMAIN_NAME"),
            project_domain=os.getenv("OS_PROJECT_DOMAIN_NAME"),
        )
    )

    await commands.add_keypair(ctx, user, os_client, public_key)

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
async def add_portforward(
    ctx: interactions.CommandContext, port: int, protocol: str = "http"
):
    """Add port forwarding rules to security group in Midgard"""
    utils.log(
        ctx.author.name, f"/midgard add portforward port:{port} protocol:{protocol}"
    )
    db_engine, db_session = await database.init_async_db(os.getenv("DB_URI"))
    user = await database.find_user(db_session, str(ctx.author.user.id))

    os_client = (
        cloud.connect()
        if user is None
        else cloud.connect(
            auth_url=os.getenv("OS_AUTH_URL"),
            region_name=os.getenv("OS_REGION_NAME"),
            project_name=user.project_name,
            username=user.username,
            password=user.password,
            user_domain=os.getenv("OS_USER_DOMAIN_NAME"),
            project_domain=os.getenv("OS_PROJECT_DOMAIN_NAME"),
        )
    )

    await commands.add_portforward(ctx, user, os_client, port, protocol)

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


@midgard.group(name="server")
async def server(ctx: interactions.CommandContext):
    """Server group command"""
    pass


@server.subcommand(
    name="create",
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
async def server_create(ctx: interactions.CommandContext, flavor: str, image: str):
    """Create a VM server"""
    utils.log(ctx.author.name, f"/midgard server create flavor:{flavor} image:{image}")
    db_engine, db_session = await database.init_async_db(os.getenv("DB_URI"))
    user = await database.find_user(db_session, str(ctx.author.user.id))

    os_client = (
        cloud.connect()
        if user is None
        else cloud.connect(
            auth_url=os.getenv("OS_AUTH_URL"),
            region_name=os.getenv("OS_REGION_NAME"),
            project_name=user.project_name,
            username=user.username,
            password=user.password,
            user_domain=os.getenv("OS_USER_DOMAIN_NAME"),
            project_domain=os.getenv("OS_PROJECT_DOMAIN_NAME"),
        )
    )

    await commands.create_server(ctx, user, os_client, flavor, image)

    # Close database connection
    await db_engine.dispose()
    os_client.close()


@server.subcommand(
    name="rebuild",
    description="Rebuild a VM server",
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
async def server_rebuild(ctx: interactions.CommandContext, flavor: str, image: str):
    """Create a VM server"""
    utils.log(ctx.author.name, f"/midgard server create flavor:{flavor} image:{image}")
    db_engine, db_session = await database.init_async_db(os.getenv("DB_URI"))
    user = await database.find_user(db_session, str(ctx.author.user.id))

    os_client = (
        None
        if user is None
        else cloud.connect(
            auth_url=os.getenv("OS_AUTH_URL"),
            region_name=os.getenv("OS_REGION_NAME"),
            project_name=user.project_name,
            username=user.username,
            password=user.password,
            user_domain=os.getenv("OS_USER_DOMAIN_NAME"),
            project_domain=os.getenv("OS_PROJECT_DOMAIN_NAME"),
        )
    )

    await commands.rebuild_server(ctx, user, os_client, flavor, image)

    # Close database connection
    await db_engine.dispose()
    os_client.close()


@server_create.autocomplete("flavor")
async def server_create_flavor_autocomplete(
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


@server_create.autocomplete("image")
async def server_create_image_autocomplete(
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
