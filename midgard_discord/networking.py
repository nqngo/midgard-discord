# Networking component for Midgard Discord Bot

import os
import aiohttp

CF_API_URL = "https://api.cloudflare.com/client/v4"
CF_ACCOUNT_ENDPOINT = "{CF_API_URL}/accounts/{CF_ACCOUNT_ID}"
CF_TUNNEL_ENDPOINT = "{CF_ACCOUNT_ENDPOINT}/cfd_tunnel/{CF_TUNNEL_ID}"
CF_DNS_ENDPOINT = "{CF_API_URL}/zones/{CF_ZONE_ID}/dns_records"


class Ingress:
    """A CloudFlare tunnel ingress rule."""

    def __init__(self, service: str, hostname: str = None, originRequest: dict = None):
        """Initialize the ingress rule."""
        self.service = service
        self.hostname = hostname
        self.originRequest = originRequest

    def __repr__(self) -> str:
        """Return the representation of the ingress rule."""
        if self.hostname:
            return f"<Ingress {self.hostname} --> {self.service} {self.originRequest}>"
        else:
            return f"<Ingress {self.service}>"


def get_client() -> aiohttp.ClientSession:
    """Get a CloudFlare client."""
    headers = {
        "Authorization": f"Bearer {os.getenv('CF_API_KEY')}",
        "Content-Type": "application/json",
    }
    client = aiohttp.ClientSession(headers=headers)
    client.CF_ACCOUNT_ENDPOINT = CF_ACCOUNT_ENDPOINT.format(
        CF_API_URL=CF_API_URL, CF_ACCOUNT_ID=os.getenv("CF_ACCOUNT_ID")
    )
    client.CF_TUNNEL_ENDPOINT = CF_TUNNEL_ENDPOINT.format(
        CF_ACCOUNT_ENDPOINT=client.CF_ACCOUNT_ENDPOINT,
        CF_TUNNEL_ID=os.getenv("CF_TUNNEL_ID"),
    )
    client.CF_DNS_ENDPOINT = CF_DNS_ENDPOINT.format(
        CF_API_URL=CF_API_URL, CF_ZONE_ID=os.getenv("CF_ZONE_ID")
    )
    client.CF_TUNNEL_DNS = f"{os.getenv('CF_TUNNEL_ID')}.cfargotunnel.com"
    return client


async def create_dns_record(hostname: str) -> None:
    """Create a DNS record."""
    async with get_client() as client:
        domain = os.getenv("CF_DOMAIN")
        if hostname.endswith("."):
            hostname = hostname[:-1]
        if not hostname.endswith(domain):
            hostname = f"{hostname}.{domain}"
        async with client.post(
            client.CF_DNS_ENDPOINT,
            json={
                "type": "CNAME",
                "name": hostname,
                "content": client.CF_TUNNEL_DNS,
                "ttl": 1,
                "proxied": True,
            },
        ) as resp:
            return


async def get_tunnel_config() -> list[dict]:
    """Get the tunnel configuration."""
    async with get_client() as client:
        async with client.get(f"{client.CF_TUNNEL_ENDPOINT}/configurations") as resp:
            tunnels = await resp.json()
            return tunnels["result"]["config"]["ingress"]


def add_tunnel_config(
    tunnels: list[dict], service: str, hostname: str, originRequest: dict = None
) -> None:
    """Add a tunnel configuration."""
    for tunnel in tunnels:
        if "hostname" in tunnel and hostname in tunnel["hostname"]:
            raise IndexError(f"Hostname {hostname} already exists.")
    else:
        domain = os.getenv("CF_DOMAIN")
        if hostname.endswith("."):
            hostname = hostname[:-1]
        if not hostname.endswith(domain):
            hostname = f"{hostname}.{domain}"
        ingress = {
            "service": service,
            "hostname": hostname,
            "originRequest": originRequest if originRequest else {},
        }
        tunnels.insert(0, ingress)


async def update_tunnel_config(tunnels: dict[Ingress]) -> None:
    """Update the tunnel configuration."""
    async with get_client() as client:
        async with client.put(
            f"{client.CF_TUNNEL_ENDPOINT}/configurations",
            json={"config": {"ingress": tunnels}},
        ) as resp:
            print(await resp.json())
