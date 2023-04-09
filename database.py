# !/usr/bin/env python
# Models fixtures for the application

from sqlalchemy import create_engine
from sqlalchemy import DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.orm import mapped_column, sessionmaker


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


def init_db(DB_URI: str):
    """Initialise the database."""
    engine = create_engine(DB_URI)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
