# Cache database functions

from sqlalchemy import select
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class OpenStackCredential(Base):
    """OpenStack RC Credential model."""

    __tablename__ = "openstack_credentials"

    username: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str]
    project_name: Mapped[str]
    created_at: Mapped[DateTime] = mapped_column(DateTime(), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(), server_default=func.now())

    def __repr__(self):
        """Return a string representation of the model."""
        return f"<OpenStackCredential(username={self.username}, project_name={self.project_name}>"

    def __getitem__(self, field):
        """Return the value of a field."""
        return self.__dict__[field]


async def init_async_db(DB_URI: str) -> tuple[create_async_engine, async_sessionmaker]:
    """Initialise the database."""
    engine = create_async_engine(DB_URI)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = async_sessionmaker(engine, expire_on_commit=False)
    return engine, session


async def find_user(
    async_session: async_sessionmaker[AsyncSession], discord_user_id: str
):
    """Find a user the Database"""
    stmt = select(OpenStackCredential).where(
        OpenStackCredential.username == discord_user_id
    )
    async with async_session() as session:
        result = (await session.execute(stmt)).first()
        return result[0] if result is not None else None


async def create_user(
    async_session: async_sessionmaker[AsyncSession], discord_user_id: str, **kawrgs
) -> None:
    """Create a new user in the Database"""
    user = OpenStackCredential(username=discord_user_id, **kawrgs)
    async with async_session() as session:
        async with session.begin():
            session.add(user)
    await session.commit()
