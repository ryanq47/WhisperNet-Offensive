from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
from pathlib import Path

from modules.config import Config

# notes, may need to think about SAN n stuff when matching domain to the cert

def generate_pem(key_path: str, key_name: str, cert_path: str, cert_name: str):
    # Convert string paths to pathlib Paths
    key_dir = Path(key_path)
    cert_dir = Path(cert_path)

    # Ensure directories exist
    key_dir.mkdir(parents=True, exist_ok=True)
    cert_dir.mkdir(parents=True, exist_ok=True)

    # Generate a private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Create a public key
    public_key = private_key.public_key()

    # Configuration values
    cn = Config().config.server.tls.tls_cn
    org = Config().config.server.tls.tls_org
    country = Config().config.server.tls.tls_country
    email = Config().config.server.tls.tls_email
    expire = Config().config.server.tls.tls_expire

    # Create a certificate builder
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, country),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
        x509.NameAttribute(NameOID.COMMON_NAME, cn),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, email),
    ])

    builder = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        public_key
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        # Certificate will be valid for the configured number of days
        datetime.datetime.utcnow() + datetime.timedelta(days=expire)
    ).sign(private_key, hashes.SHA256(), default_backend())

    # Write private key to a file
    private_key_path = key_dir / f"{key_name}.pem"
    with private_key_path.open("wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Write certificate to a file
    certificate_path = cert_dir / f"{cert_name}.pem"
    with certificate_path.open("wb") as f:
        f.write(builder.public_bytes(serialization.Encoding.PEM))

    print(f"TLS certificate and private key generated successfully.\n"
          f"Private Key: {private_key_path}\nCertificate: {certificate_path}")
