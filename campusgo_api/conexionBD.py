import pymysql
pymysql.install_as_MySQLdb()

import MySQLdb as dbc
import MySQLdb.cursors
from .config import Config
import os
import base64
import tempfile


def _write_ca_from_b64(b64_string: str) -> str:
    """Decode a base64 PEM and write to a temporary file. Return path."""
    data = base64.b64decode(b64_string)
    # create a temp file that persists for the process lifetime
    fd, path = tempfile.mkstemp(prefix='db_ca_', suffix='.pem')
    with os.fdopen(fd, 'wb') as f:
        f.write(data)
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
                except Exception:
                    # fallback to MySQLdb connector if pymysql fails for any reason
                    connect_kwargs['ssl'] = {'ca': ca_path}

        # Default: use MySQLdb (mysqlclient) shim
        self.dblink = dbc.connect(**connect_kwargs)

    @property
    def open(self):
        return self.dblink
