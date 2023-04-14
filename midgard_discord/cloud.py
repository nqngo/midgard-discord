# OpenStack Cloud helper functions
import asyncio
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
DEFAULT_KEYPAIR_NAME = "midgard-keypair"
DEFAULT_KEYPAIR_TYPE = "ssh"
DEFAULT_SG_DIRECTION = "ingress"
DEFAULT_SG_PROTOCOL = "tcp"
DEFAULT_SG_NAME = "default"
DEFAULT_SG_REMOTE_IP_PREFIX = "0.0.0.0/0"
DEFAULT_SERVER_NAME = "midgard-server"


def connect(
    auth_url: str = None,
    region_name: str = None,
    project_name: str = None,
    username: str = None,
    password: str = None,
    user_domain: str = None,
    project_domain: str = None,
):
    """Connect to an OpenStack client."""
    if not (auth_url or region_name or project_name or username or password):
        return openstack.connect(cloud="envvars")
    else:
        return openstack.connect(
            auth_url=auth_url,
            region_name=region_name,
            project_name=project_name,
            username=username,
            password=password,
            user_domain_name=user_domain,
            project_domain_name=project_domain,
        )


async def find_project(client: openstack.connection.Connection, project_name: str):
    """Find a project in Keystone database."""
    return await asyncio.to_thread(
        client.identity.find_project, project_name, ignore_missing=True
    )


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


async def find_default_network(
    client: openstack.connection.Connection,
    **kwargs,
) -> openstack.network.v2.network.Network:
    """Find default network for a project."""

    return await asyncio.to_thread(
        client.network.find_network, DEFAULT_NETWORK_NAME, ignore_missing=True, **kwargs
    )


async def add_security_group_rule(
    client: openstack.connection.Connection,
    port: int,
    direction: str = DEFAULT_SG_DIRECTION,
) -> None:
    """Setup default security group for a project."""
    # Find security group
    security_group = await asyncio.to_thread(
        client.network.find_security_group,
        DEFAULT_SG_NAME,
    )

    # Create security group rule
    try:
        await asyncio.to_thread(
            client.network.create_security_group_rule,
            security_group_id=security_group.id,
            direction=direction,
            protocol=DEFAULT_SG_PROTOCOL,
            port_range_min=port,
            port_range_max=port,
            remote_ip_prefix=DEFAULT_SG_REMOTE_IP_PREFIX,
        )
    except openstack.exceptions.ConflictException as e:
        raise Exception(e.details.split(".")[0] + ".")


async def find_default_security_group(
    client: openstack.connection.Connection,
    **kwargs,
) -> openstack.network.v2.security_group.SecurityGroup:
    """Find default security group for a project."""
    return await asyncio.to_thread(
        client.network.find_security_group, DEFAULT_SG_NAME, **kwargs
    )


async def find_floating_ip(
    client: openstack.connection.Connection,
    **kwargs,
) -> openstack.network.v2.floating_ip.FloatingIP:
    """Retrun the first available floating IP"""
    return await asyncio.to_thread(client.available_floating_ip, **kwargs)


async def find_keypair(client: openstack.connection.Connection):
    """Find a keypair in a project."""
    return await asyncio.to_thread(
        client.compute.find_keypair,
        DEFAULT_KEYPAIR_NAME,
        ignore_missing=True,
    )


async def create_keypair(
    client: openstack.connection.Connection,
    public_key: str,
) -> None:
    """Create a new keypair for a project."""
    try:
        await asyncio.to_thread(
            client.compute.create_keypair,
            name=DEFAULT_KEYPAIR_NAME,
            public_key=public_key,
            type=DEFAULT_KEYPAIR_TYPE,
        )
    except openstack.exceptions.BadRequestException as e:
        raise Exception(e.details)


async def delete_keypair(
    client: openstack.connection.Connection,
    keypair: openstack.compute.v2.keypair.Keypair,
) -> None:
    """Delete a keypair from a project."""
    await asyncio.to_thread(client.compute.delete_keypair, keypair)


async def list_flavors(
    client: openstack.connection.Connection,
) -> list[openstack.compute.v2.flavor.Flavor]:
    """List all flavors."""
    flavors = await asyncio.to_thread(client.compute.flavors)
    return [flavor for flavor in flavors]


async def list_images(
    client: openstack.connection.Connection,
) -> list[openstack.image.v2.image.Image]:
    """List all images."""
    images = await asyncio.to_thread(client.image.images)
    return [image for image in images]


async def find_server(
    client: openstack.connection.Connection,
    name: str = None,
    **kwargs,
) -> openstack.compute.v2.server.Server:
    """Find a server in a project."""
    if name is None:
        name = DEFAULT_SERVER_NAME
    return await asyncio.to_thread(
        client.compute.find_server,
        name,
        ignore_missing=True,
        **kwargs,
    )


async def create_server(
    client: openstack.connection.Connection, **kwargs
) -> openstack.compute.v2.server.Server:
    """Create a new server in a project."""
    name = kwargs.pop("name", DEFAULT_SERVER_NAME)
    try:
        return await asyncio.to_thread(client.create_server, name=name, **kwargs)
    except openstack.exceptions.BadRequestException as e:
        raise Exception(e.details)
