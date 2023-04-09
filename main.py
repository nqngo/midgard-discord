import os
import asyncio
import datetime

from sqlalchemy import select
import interactions

from dotenv import load_dotenv

import cloud
import database
import utils


# Setup discord API
load_dotenv()

CACHE_TTL = os.getenv("DB_CACHE_TTL")
bot = interactions.Client(
    token=os.getenv("DISCORD_TOKEN"),
    default_scope=os.getenv("DISCORD_DEFAULT_GUILD_ID"),
)

# Setup database
db = database.init_db(os.getenv("DB_URI"))


# Setup OpenStack cloud session
os_session = cloud.get_session(
    username=os.getenv("OS_USERNAME"),
    auth_url=os.getenv("OS_AUTH_URL"),
    password=os.getenv("OS_PASSWORD"),
    project_name=os.getenv("OS_PROJECT_NAME"),
    project_domain_name=os.getenv("OS_PROJECT_DOMAIN_NAME"),
    user_domain_name=os.getenv("OS_USER_DOMAIN_NAME"),
)
keystone = cloud.get_keystone_client(os_session)


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
    # TODO: Bring help text to a separate file
    help_text = """
Welcome to Midgard. Midgard is a private OpenStack cloud for VAIT testing, training, and development purpose.
At the moment, Midgard offers the following capacities:
    1. Virtual Machines.
    2. Persistent Volume Storages.

For more information, please visit https://docs.midgard.lab.nqngo.com
"""
    await ctx.send(help_text)


@midgard.subcommand(name="register", description="Register a new account with Midgard")
async def register(ctx: interactions.CommandContext):
    """Register a new OpenStack account with Midgard"""

    # Get the user's OpenStack credential from cache database
    stmt = select(database.OpenStackCredential).where(
        database.OpenStackCredential.username == str(ctx.author.user.id)
    )
    credential = await asyncio.to_thread(utils.try_except, db.scalars(stmt), None)
    context_msg = None
    if credential is None:
        project_name = f"{os.getenv('OS_DEFAULT_GUILD_PREFIX')}_{ctx.author.user.id}"
        user = await asyncio.to_thread(utils.find_user, keystone, ctx.author.user.id)
        # If user does not exist, create a new account
        if user is None:
            # Create a new OpenStack project
            project = keystone.projects.create(
                project_name,
                os.getenv(
                    "OS_PROJECT_DOMAIN_NAME"
                ).lower(),  # TODO: This is a hack to make it work with default domain name
            )
            # Create a new OpenStack user
            password = await asyncio.to_thread(utils.generate_password)
            user = await asyncio.to_thread(
                keystone.users.create,
                f"{ctx.author.user.id}",
                default_project=project,
                password=password,
            )
            context_msg = f"""
Hi <@{ctx.author.user.id}>, your account has been successfully created!

Welcome to **Midgard**!"""
            timestamp = datetime.datetime.now()
            print(
                f"[{timestamp:%Y-%m-%d %H:%M:%S}] New account created: {ctx.author.user.id}."
            )
        # Otherwise, we might have lost the cache, update with a new password
        else:
            password = await asyncio.to_thread(utils.generate_password)
            await asyncio.to_thread(
                keystone.users.update,
                user,
                password=password,
            )
            context_msg = f"<@{ctx.author.user.id}>, your account already exists!"

        # Save the result to database
        credential = database.OpenStackCredential(
            username=user.name,
            project_name=project_name,
            password=password,
        )
        db.add(credential)
        db.commit()

        await ctx.send(context_msg)
    # If we hit the cache, just confirm we exists
    else:
        # TODO: Recheck if the user still exists in Keystone
        # TODO: Recheck if the project still exists in Keystone
        # TODO: Extract the user and project creation into a separate function
        await ctx.send(f"<@{ctx.author.user.id}>, your account already exists!")


bot.start()
