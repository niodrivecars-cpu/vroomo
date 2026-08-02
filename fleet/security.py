"""Central client-IP resolution.

Django only ever sees ``REMOTE_ADDR = 127.0.0.1`` behind the nginx reverse
proxy documented in ``docs/deployment.md``. Every IP-based control (rate
limiting via django-ratelimit, audit logging) must resolve the real client
address through this same helper so they can never disagree.

Trust model
-----------
Forwarded headers are trusted only when the immediate TCP peer (``REMOTE_ADDR``)
is an address listed in ``X_FORWARDED_TRUSTED_PROXIES``. For such peers,
``X-Forwarded-For`` is walked right-to-left (closest hop first), skipping
addresses that are themselves trusted proxies; the rightmost untrusted address
is the client. Because nginx appends the client address with
``proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;``, any
client-supplied ``X-Forwarded-For`` values sit to the LEFT of the appended
address and can never win the walk. If the peer is not a configured trusted
proxy, or the header is absent, ``REMOTE_ADDR`` is used and forwarded data is
ignored — client-supplied forwarding headers are never trusted directly.
"""

from django.conf import settings


def get_trusted_proxies():
    """Addresses of reverse proxies this deployment trusts."""
    return frozenset(getattr(settings, 'X_FORWARDED_TRUSTED_PROXIES', ()) or ())


def get_client_ip(request):
    """Return the client IP resolved through the trusted reverse proxy.

    Falls back to ``REMOTE_ADDR`` when the peer is not a configured trusted
    proxy or no ``X-Forwarded-For`` header is present.
    """
    remote_addr = request.META.get('REMOTE_ADDR', '')
    trusted = get_trusted_proxies()
    if not remote_addr or remote_addr not in trusted:
        return remote_addr
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    addresses = [addr.strip() for addr in xff.split(',') if addr.strip()]
    for addr in reversed(addresses):
        if addr not in trusted:
            return addr
    # Header missing or every hop is a trusted proxy: keep the immediate peer.
    return remote_addr
