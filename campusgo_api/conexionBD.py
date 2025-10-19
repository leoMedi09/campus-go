import pymysql
import ssl

pymysql.install_as_MySQLdb()

import MySQLdb as dbc
import MySQLdb.cursors
from .config import Config
import os
import base64
import tempfile


def _write_ca_from_b64(b64_string: str) -> str:
    """Decode a base64 PEM and write to a temporary file. Return path."""
    raw = base64.b64decode(b64_string)

    # If the decoded content already looks like a PEM (text containing BEGIN), write it
    if b'-----BEGIN' in raw:
        pem_bytes = raw
    else:
        # Assume raw is DER bytes: wrap into a PEM encoded certificate
        pem_body = base64.encodebytes(raw)
        # Ensure lines use LF (openssl-friendly)
        pem_body = b"".join([line.replace(b"\r\n", b"\n") for line in pem_body.splitlines(True)])
        pem_bytes = b'-----BEGIN CERTIFICATE-----\n' + pem_body + b'-----END CERTIFICATE-----\n'

    # create a temp file that persists for the process lifetime
    fd, path = tempfile.mkstemp(prefix='db_ca_', suffix='.pem')
    with os.fdopen(fd, 'wb') as f:
        f.write(pem_bytes)
    return path


class Conexion:
    def __init__(self):
        connect_kwargs = dict(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            passwd=Config.DB_PASSWORD,
            db=Config.DB_NAME,
            port=Config.DB_PORT,
            cursorclass=dbc.cursors.DictCursor
        )

        # If SSL/TLS is requested, prepare ssl args
        if Config.DB_USE_SSL:
            ca_path = None
            if Config.DB_SSL_CA_PATH:
                ca_path = Config.DB_SSL_CA_PATH
            elif Config.DB_SSL_CA_B64:
                try:
                    ca_path = _write_ca_from_b64(Config.DB_SSL_CA_B64)
                except Exception:
                    ca_path = None

            if ca_path:
                # Prefer using pymysql.connect when SSL is required because it
                # reliably negotiates TLS with ssl={'ca': path} in this runtime.
                # Build args for pymysql (it expects 'password' not 'passwd').
                try:
                    # First attempt: use CA file path
                    pymysql_kwargs = dict(
                        host=Config.DB_HOST,
                        user=Config.DB_USER,
                        password=Config.DB_PASSWORD,
                        db=Config.DB_NAME,
                        port=Config.DB_PORT,
                        cursorclass=dbc.cursors.DictCursor,
                        ssl={'ca': ca_path}
                    )
                    self.dblink = pymysql.connect(**pymysql_kwargs)
                    return
                except ssl.SSLError as e:
                    # If CA file fails, try without strict verification as fallback
                    # (This is less secure but may work if CA cert has issues)
                    try:
                        pymysql_kwargs_fallback = dict(
                            host=Config.DB_HOST,
                            user=Config.DB_USER,
                            password=Config.DB_PASSWORD,
                            db=Config.DB_NAME,
                            port=Config.DB_PORT,
                            cursorclass=dbc.cursors.DictCursor,
                            ssl={'check_hostname': False, 'verify_mode': ssl.CERT_NONE}
                        )
                        self.dblink = pymysql.connect(**pymysql_kwargs_fallback)
                        return
                    except dbc.OperationalError as auth_err:
                        # Check if it's an authentication error (Access denied)
                        if '1105' in str(auth_err) or 'Access denied' in str(auth_err):
                            raise Exception(f"Database authentication failed: {auth_err}. "
                                            "Check DB_USER and DB_PASSWORD environment variables. "
                                            "TiDB Cloud requires user format: <prefix>.<username>")
                        # Otherwise raise original SSL error
                        raise Exception(f"SSL error while loading CA for DB connection: {e}. "
                                        "Ensure DB_SSL_CA_B64 contains a valid base64-encoded PEM or set DB_SSL_CA_PATH to a valid certificate file.")
                    except Exception:
                        # If fallback also fails, raise the original SSL error
                        raise Exception(f"SSL error while loading CA for DB connection: {e}. "
                                        "Ensure DB_SSL_CA_B64 contains a valid base64-encoded PEM or set DB_SSL_CA_PATH to a valid certificate file.")
                except Exception:
                    # fallback to MySQLdb connector if pymysql fails for any other reason
                    connect_kwargs['ssl'] = {'ca': ca_path}

        # Default: use MySQLdb (mysqlclient) shim
        self.dblink = dbc.connect(**connect_kwargs)

    @property
    def open(self):
        return self.dblink
