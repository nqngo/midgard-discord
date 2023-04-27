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
def private_key():
    """SSH private key."""
    return """-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBpoqQHh3TfVjNOUswevNeR+WNDJXf/e7m62VPFwredQgAAAJBlWyIRZVsi
EQAAAAtzc2gtZWQyNTUxOQAAACBpoqQHh3TfVjNOUswevNeR+WNDJXf/e7m62VPFwredQg
AAAEBsevcz5OvqAxBHdJ1UhN3O5aizozcqMdrmLUnEG4DqiGmipAeHdN9WM05SzB6815H5
Y0Mld/97ubrZU8XCt51CAAAADW5xbmdvQGhlbGhlaW0=
-----END OPENSSH PRIVATE KEY-----"""


@pytest.fixture
def public_key():
    """SSH public key."""
    return "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGmipAeHdN9WM05SzB6815H5Y0Mld/97ubrZU8XCt51C midgard@pytest"


@pytest.fixture
def http_port():
    """Port number."""
    return 8080


@pytest.fixture
def http_protocol():
    """Protocol."""
    return "http"


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


@pytest.fixture
def find_keypair_cloud_patch_none():
    with patch("midgard_discord.cloud.find_keypair", return_value=None) as mock:
        yield mock


@pytest.fixture
def find_keypair_cloud_patch_some_keypair():
    keypair = MagicMock(openstack.compute.v2.keypair.Keypair)
    keypair.id = "333"
    keypair.name = "test_keypair"

    with patch("midgard_discord.cloud.find_keypair", return_value=keypair) as mock:
        yield mock


@pytest.fixture
def create_keypair_cloud_patch():
    keypair = MagicMock(openstack.compute.v2.keypair.Keypair)
    keypair.id = "333"
    keypair.name = "test_keypair"

    with patch("midgard_discord.cloud.create_keypair", return_value=keypair) as mock:
        yield mock


@pytest.fixture
def delete_keypair_cloud_patch():
    with patch("midgard_discord.cloud.delete_keypair") as mock:
        yield mock


@pytest.fixture
def find_server_cloud_patch_none():
    with patch("midgard_discord.cloud.find_server", return_value=None) as mock:
        yield mock


@pytest.fixture
def find_server_cloud_patch_some_server():
    server = MagicMock(openstack.compute.v2.server.Server)
    server.id = "444"
    server.name = "test_server"
    server.addresses = {
        "default": [
            {
                "addr": "192.168.0.8",
                "OS-EXT-IPS:type": "floating",
            },
            {
                "addr": "10.0.0.8",
                "OS-EXT-IPS:type": "fixed",
            },
        ]
    }
    with patch("midgard_discord.cloud.find_server", return_value=server) as mock:
        yield mock


@pytest.fixture
def create_server_cloud_patch():
    server = MagicMock(openstack.compute.v2.server.Server)
    server.id = "444"
    server.name = "test_server"

    with patch("midgard_discord.cloud.create_server", return_value=server) as mock:
        yield mock


@pytest.fixture
def create_security_group_cloud_patch():
    security_group = MagicMock(openstack.network.v2.security_group.SecurityGroup)
    security_group.id = "555"
    security_group.name = "test_security_group"

    with patch(
        "midgard_discord.cloud.create_security_group", return_value=security_group
    ) as mock:
        yield mock


@pytest.fixture
def add_security_group_rule_cloud_patch():
    with patch("midgard_discord.cloud.add_security_group_rule") as mock:
        yield mock


@pytest.fixture
def find_default_security_group_cloud_patch():
    security_group = MagicMock(openstack.network.v2.security_group.SecurityGroup)
    security_group.id = "555"
    security_group.name = "test_security_group"

    with patch(
        "midgard_discord.cloud.find_default_security_group", return_value=security_group
    ) as mock:
        yield mock


@pytest.fixture
def get_tunnel_config_networking_patch():
    with patch("midgard_discord.networking.get_tunnel_config") as mock:
        yield mock


@pytest.fixture
def add_tunnel_config_networking_patch():
    with patch("midgard_discord.networking.add_tunnel_config") as mock:
        yield mock


@pytest.fixture
def update_tunnel_config_networking_patch():
    with patch("midgard_discord.networking.update_tunnel_config") as mock:
        yield mock


@pytest.fixture
def create_dns_record_networking_patch():
    with patch("midgard_discord.networking.create_dns_record") as mock:
        yield mock
