import os


class Config:
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'campusgo')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_para_jwt')

    # SSL/TLS for databases like TiDB Cloud
    # Set DB_USE_SSL to 'true' (case-insensitive) to enable SSL verification.
    DB_USE_SSL = str(os.environ.get('DB_USE_SSL', 'false')).lower() in ('1', 'true', 'yes')
    # You can provide the CA certificate either as a file path in DB_SSL_CA_PATH
    # or as a base64-encoded PEM string in DB_SSL_CA_B64.
    DB_SSL_CA_PATH = os.environ.get('DB_SSL_CA_PATH', '')
    DB_SSL_CA_B64 = os.environ.get('DB_SSL_CA_B64', '')
