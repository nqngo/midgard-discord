import datetime
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

import interactions
import openstack

from midgard_discord import database


@pytest.fixture
def ctx():
    """Return a mock context."""
    mock_ctx = AsyncMock(interactions.CommandContext)
    yield mock_ctx
    mock_ctx.reset_mock()


@pytest.fixture
def session():
    """Return a mock session."""
    mock_session = MagicMock()
    return mock_session


@pytest.fixture
def openstackclient():
    """Return a mock openstackclient."""
    mock_openstackclient = MagicMock(openstack.connection.Connection)
    return mock_openstackclient


@pytest.fixture
def find_user_db_patch_none():
    with patch("midgard_discord.database.find_user", return_value=None) as mock:
        yield mock


@pytest.fixture
def find_user_db_patch_some_user():
    user = database.OpenStackCredential(
        username="test_user",
        password="test_password",
        project_name="test_project",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )
    with patch("midgard_discord.database.find_user", return_value=user) as mock:
        yield mock


@pytest.fixture
def create_user_db_patch():
    with patch("midgard_discord.database.create_user") as mock:
        yield mock


@pytest.fixture
def find_project_cloud_patch_none():
    with patch("midgard_discord.cloud.find_project", return_value=None) as mock:
        yield mock


@pytest.fixture
def find_project_cloud_patch_some_project():
    project = MagicMock(openstack.identity.v3.project)
    project.id = "000"
    project.name = "test_project"

    with patch("midgard_discord.cloud.find_project", return_value=project) as mock:
        yield mock


@pytest.fixture
def find_user_cloud_patch_none():
    with patch("midgard_discord.cloud.find_user", return_value=None) as mock:
        yield mock


@pytest.fixture
def find_user_cloud_patch_some_user():
    user = MagicMock(openstack.identity.v3.user)
    user.id = "111"
    user.name = "test_user"
    user.password = "test_password"
    user.default_project_id = "000"

    with patch("midgard_discord.cloud.find_user", return_value=user) as mock:
        yield mock


@pytest.fixture
def create_project_cloud_patch():
    project = MagicMock(openstack.identity.v3.project)
    project.id = "000"
    project.name = "test_project"

    with patch("midgard_discord.cloud.create_project", return_value=project) as mock:
        yield mock


@pytest.fixture
def create_user_cloud_patch():
    user = MagicMock(openstack.identity.v3.user)
    user.id = "111"
    user.name = "test_user"
    user.password = "test_password"
    user.default_project_id = "000"

    with patch("midgard_discord.cloud.create_user", return_value=user) as mock:
        yield mock


@pytest.fixture
def update_user_cloud_patch():
    user = MagicMock(openstack.identity.v3.user)
    user.id = "111"
    user.name = "test_user"
    user.password = "test_password"
    user.default_project_id = "000"

    with patch("midgard_discord.cloud.update_user", return_value=user) as mock:
        yield mock


@pytest.fixture
def find_default_network_cloud_patch_none():
    with patch("midgard_discord.cloud.find_default_network", return_value=None) as mock:
        yield mock


@pytest.fixture
def find_default_network_cloud_patch_some_network():
    network = MagicMock(openstack.network.v2.network.Network)
    network.id = "222"
    network.name = "test_network"

    with patch(
        "midgard_discord.cloud.find_default_network", return_value=network
    ) as mock:
        yield mock


@pytest.fixture
def setup_default_network_patch():
    with patch("midgard_discord.cloud.setup_default_network") as mock:
        yield mock
