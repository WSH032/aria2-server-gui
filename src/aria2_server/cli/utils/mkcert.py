import datetime
import ipaddress
from pathlib import Path
from textwrap import dedent
from typing import List

import typer
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from typing_extensions import Annotated

__all__ = ("mkcert_cli",)


mkcert_cli = typer.Typer(invoke_without_command=True)


def _parse_san_type(san: str) -> x509.GeneralName:
    try:
        return x509.IPAddress(ipaddress.ip_address(san))
    except ValueError:
        pass
    try:
        return x509.IPAddress(ipaddress.ip_network(san))
    except ValueError:
        pass
    return x509.DNSName(san)


# code ref: https://cryptography.io/en/latest/x509/tutorial/#creating-a-self-signed-certificate
# args name ref: https://github.com/FiloSottile/mkcert?tab=readme-ov-file#advanced-options
@mkcert_cli.callback()
def mkcert(
    san: Annotated[
        List[str],
        typer.Argument(
            help=dedent(
                """\
                Subject Alternative Names (SAN). Only support IP address and DNS name.
                e.g: `192.168.137.1`, `localhost`\
            """
            ),
        ),
    ],
    *,
    key_file: Annotated[
        Path,
        typer.Option(
            help="Path to the private key file which will be created.",
            prompt=True,
            dir_okay=False,
            writable=True,
            allow_dash=True,
        ),
    ] = Path("key.pem"),
    cert_file: Annotated[
        Path,
        typer.Option(
            help="Path to the certificate file which will be created.",
            prompt=True,
            dir_okay=False,
            writable=True,
            allow_dash=True,
        ),
    ] = Path("cert.crt"),
    key_file_password: Annotated[
        str,
        typer.Option(
            help=dedent(
                """\
                Password for the private key file.
                If not specified, will create a private key file without password.
                For security reasons, we strongly recommend setting a password for the private key file.\
            """
            ),
            prompt=True,
        ),
    ] = "",
    expiration_days: Annotated[
        int,
        typer.Option(
            help="The number of days the certificate will be valid for.",
            prompt=True,
        ),
    ] = 365,
    organization_name: Annotated[
        str,
        typer.Option(
            help="Organization name for the certificate.",
            prompt=True,
        ),
    ] = "Aria2 Server",
):
    """Generate a self-signed certificate for https server."""
    # Generate our key
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    # Write our key to disk for safe keeping
    encryption_algorithm = (
        serialization.BestAvailableEncryption(key_file_password.encode("utf-8"))
        if key_file_password
        else serialization.NoEncryption()
    )
    with typer.open_file(str(key_file), "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=encryption_algorithm,
            )
        )

    # Various details about who we are. For a self-signed certificate the
    # subject and issuer are always the same.
    subject = issuer = x509.Name(
        [
            # x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            # x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            # x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization_name),
            # x509.NameAttribute(NameOID.COMMON_NAME, "aria2-server.com"),
        ]
    )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=expiration_days)
        )
        .add_extension(
            x509.SubjectAlternativeName([_parse_san_type(_) for _ in san]),
            critical=False,
        )
        # Sign our certificate with our private key
        .sign(key, hashes.SHA256())
    )
    # Write our certificate out to disk.
    with typer.open_file(str(cert_file), "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


if __name__ == "__main__":
    mkcert_cli()
