# OpenStack Cloud helper functions

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_client


def get_session(
    username: str,
    password: str,
    project_name: str,
    project_domain_name: str,
    user_domain_name: str,
    auth_url: str,
):
    """Get an OpenStack session."""
    auth = v3.Password(
        auth_url=auth_url,
        username=username,
        password=password,
        project_name=project_name,
        project_domain_name=project_domain_name,
        user_domain_name=user_domain_name,
    )
    sess = session.Session(auth=auth)
    return sess


def get_keystone_client(session: session.Session):
    """Get a Keystone client."""
    keystone = keystone_client.Client(session=session)
    return keystone
