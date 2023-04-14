# Internal commands module for Midgard Discord Bot
import os
import interactions
import openstack
import sqlalchemy

from datetime import datetime

from midgard_discord import cloud
from midgard_discord import database
from midgard_discord import networking
from midgard_discord import texts
from midgard_discord import utils


def log(who: str, event: str) -> None:
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] <{who}> {event}")


async def help(ctx: interactions.CommandContext):
    """Send a welcome message."""
    log(ctx.author.name, "/midgard help")
    await ctx.send(texts.WELCOME)


async def register(
    ctx: interactions.CommandContext,
    db_session: sqlalchemy.ext.asyncio.async_sessionmaker,
    os_client: openstack.connection.Connection,
):
    """Register a user to Midgard."""
    log(ctx.author.name, "/midgard register")
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
        await ctx.send(texts.REGISTERED.format(discord_user_id=ctx.author.user.id))
    else:
        await ctx.send(
            texts.ERROR_REGISTERED.format(discord_user_id=ctx.author.user.id)
        )
