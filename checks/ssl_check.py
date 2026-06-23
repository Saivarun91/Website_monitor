import ssl
import socket

from datetime import datetime
from urllib.parse import urlparse


def get_ssl_expiry_days(url):

    hostname = urlparse(url).hostname

    context = ssl.create_default_context()

    with socket.create_connection(
        (hostname, 443)
    ) as sock:

        with context.wrap_socket(
            sock,
            server_hostname=hostname
        ) as ssock:

            cert = ssock.getpeercert()

    expiry_date = datetime.strptime(
        cert["notAfter"],
        "%b %d %H:%M:%S %Y %Z"
    )

    days_left = (
        expiry_date - datetime.utcnow()
    ).days

    return days_left