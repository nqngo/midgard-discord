import os

import interactions

from dotenv import load_dotenv

from midgard_discord import cloud
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
    await ctx.send(texts.WELCOME)


@midgard.subcommand(name="register", description="Register an account in Midgard")
@interactions.autodefer()
async def register(ctx: interactions.CommandContext):
    """Request enrolment to Midgard"""
    db_engine, db_session = await database.init_async_db(os.getenv("DB_ASYNC_URI"))
    os_client = cloud.connect()
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

            # Add SSH security group
            await cloud.add_ssh_security_group(os_client, os_project, 22)

            # Cache user in database
            await database.create_user(
                db_session,
                str(ctx.author.user.id),
                password=user_password,
                project_name=project_name,
            )
            await ctx.send(
                f"Hi <@{ctx.author.user.id}>, your account has been registered!"
            )
        # If we find the user in OpenStack, reset the password and cache it in database
        else:
            user_password = utils.generate_password()
            await cloud.update_user(os_client, os_user, password=user_password)
            project = await cloud.find_project(os_client, user.default_project)
            await database.create_user(
                db_session,
                str(ctx.author.user.id),
                password=user_password,
                project_name=project.name,
            )
            await ctx.send(
                f"Hi <@{ctx.author.user.id}>, your account has already been registered!"
            )
    else:
        await ctx.send(
            f"Hi <@{ctx.author.user.id}>, your account has already been registered!"
        )
    # Close database connection
    await db_engine.dispose()
    os_client.close()


@midgard.subcommand(
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
async def launch(ctx: interactions.CommandContext, flavor: str, image: str):
    """Create a VM server"""
    db_engine, db_session = await database.init_async_db(os.getenv("DB_ASYNC_URI"))
    user = await database.find_user(db_session, str(ctx.author.user.id))

    if user is None:
        await ctx.send(
            f"<@{ctx.author.user.id}> You need to register first. Use `/midgard register` to do so."
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
                    f"<@{ctx.author.user.id}> Your server is currently {server.status}."
                )
        else:
            keypair = await cloud.find_keypair(os_client)
            security_group = await cloud.find_default_security_group(os_client)
            try:
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
                await ctx.send(
                    f"<@{ctx.author.user.id}> Your server is ready!", ephemeral=True
                )
            except Exception as e:
                await ctx.send(f"<@{ctx.author.user.id}> {e}")

        # except Exception as e:
        #     await ctx.send(f"<@{ctx.author.user.id}> {e}")

    # Close database connection
    await db_engine.dispose()
    os_client.close()


@launch.autocomplete("flavor")
async def launch_flavor_autocomplete(
    ctx: interactions.CommandContext, user_input: str = ""
):
    """Autocomplete for create server flavor"""
    db_engine, db_session = await database.init_async_db(os.getenv("DB_ASYNC_URI"))
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

    flavors = await cloud.list_flavors(os_client)

    choices = [
        interactions.Choice(
            name=f"{flavor.name} ({flavor.vcpus} vCPUs, {flavor.ram/1024}GB RAM, {flavor.disk}GB HDD)",
            value=flavor.id,
        )
        for flavor in flavors
        if user_input in flavor.name
    ]
    # Close database connection
    await db_engine.dispose()
    os_client.close()
    await ctx.populate(choices)


@launch.autocomplete("image")
async def launch_image_autocomplete(
    ctx: interactions.CommandContext, user_input: str = ""
):
    """Autocomplete for create server image"""
    db_engine, db_session = await database.init_async_db(os.getenv("DB_ASYNC_URI"))
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
    db_engine, db_session = await database.init_async_db(os.getenv("DB_ASYNC_URI"))
    user = await database.find_user(db_session, str(ctx.author.user.id))

    if user is None:
        await ctx.send(
            f"<@{ctx.author.user.id}> You need to register first. Use `/midgard register` to do so."
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
    ],
)
async def portforward(ctx: interactions.CommandContext, port: int):
    """Add port forwarding rules to security group in Midgard"""
    db_engine, db_session = await database.init_async_db(os.getenv("DB_ASYNC_URI"))
    user = await database.find_user(db_session, str(ctx.author.user.id))

    if user is None:
        await ctx.send(
            f"<@{ctx.author.user.id}> You need to register first. Use `/midgard register` to do so."
        )
    else:
        os_client = cloud.connect()

        project = await cloud.find_project(os_client, user.project_name)
        try:
            await cloud.add_security_group_rule(os_client, project, port)
            await ctx.send(
                f"<@{ctx.author.user.id}> Port forwarding rule has been added!"
            )
        except Exception as e:
            await ctx.send(f"<@{ctx.author.user.id}> {e}")

    # Close database connection
    await db_engine.dispose()
    os_client.close()


def main():
    """Main function"""
    bot.start()


if __name__ == "__main__":
    """Run main function"""
    main()
