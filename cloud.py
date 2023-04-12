# OpenStack Cloud helper functions
import asyncio

import keystoneauth1
from keystoneauth1.identity import v3
from keystoneclient.v3 import client as keystone_client
from neutronclient.v2_0 import client as neutron_client

import openstack


# Default values
DEFAULT_SUBNET_CIDR = "10.0.0.0/24"
DEFAULT_SUBNET_GATEWAY_IP = "10.0.0.1"
DEFAULT_ROLE_NAME = "member"
DEFAULT_EXTERNAL_NETWORK = "public1"
DEFAULT_ROUTER_NAME = "midgard-NAT"
DEFAULT_NETWORK_NAME = "midgard-net"
DEFAULT_SUBNET_NAME = "midgard-subnet"
DEFAULT_DNS_NAMESERVERS = ["1.1.1.1", "1.0.0.1"]
DEFAULT_IP_VERSION = 4


def init():
    """Get an OpenStack client."""
    return openstack.connect(cloud="envvars")


async def find_user(client: openstack.connection.Connection, discord_user_id: str):
    """Find a user in Keystone database."""
    return await asyncio.to_thread(
        client.identity.find_user, discord_user_id, ignore_missing=True
    )


async def create_project(client: openstack.connection.Connection, project_name: str):
    """Create a new project in Keystone database."""
    return await asyncio.to_thread(client.identity.create_project, name=project_name)


async def create_user(
    client: openstack.connection.Connection, discord_user_id: str, **kwargs
):
    """Create a new user in Keystone database."""
    return await asyncio.to_thread(
        client.identity.create_user, name=discord_user_id, **kwargs
    )


async def update_user(
    client: openstack.connection.Connection,
    user: openstack.identity.v3.user.User,
    **kwargs,
):
    """Update a user in Keystone database."""
    return await asyncio.to_thread(client.identity.update_user, user, **kwargs)


async def set_default_roles(
    client: openstack.connection.Connection,
    user: openstack.identity.v3.user.User,
    project: openstack.identity.v3.project.Project,
) -> None:
    """Set default roles for a user in a project."""
    member_role = await asyncio.to_thread(client.identity.find_role, DEFAULT_ROLE_NAME)
    await asyncio.to_thread(
        client.identity.assign_project_role_to_user, project, user, member_role
    )


async def setup_default_network(
    client: openstack.connection.Connection,
    project: openstack.identity.v3.project.Project,
) -> None:
    """Setup default network for a project."""
    # Find default NAT project ID
    external_gateway = await asyncio.to_thread(
        client.network.find_network, DEFAULT_EXTERNAL_NETWORK
    )
    # Create default NAT router
    router = await asyncio.to_thread(
        client.network.create_router,
        name=DEFAULT_ROUTER_NAME,
        project_id=project.id,
        external_gateway_info={"network_id": external_gateway.id},
    )

    # Create network
    network = await asyncio.to_thread(
        client.network.create_network, project_id=project.id, name=DEFAULT_NETWORK_NAME
    )

    # Create subnet
    subnet = await asyncio.to_thread(
        client.network.create_subnet,
        network_id=network.id,
        cidr=DEFAULT_SUBNET_CIDR,
        project_id=project.id,
        name=DEFAULT_SUBNET_NAME,
        gateway_ip=DEFAULT_SUBNET_GATEWAY_IP,
        dns_nameservers=DEFAULT_DNS_NAMESERVERS,
        ip_version=DEFAULT_IP_VERSION,
    )

    # Add router interface
    await asyncio.to_thread(
        client.network.add_interface_to_router, router, subnet_id=subnet.id
    )
