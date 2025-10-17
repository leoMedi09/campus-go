import os


class Config:
    DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'campusgo')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_para_jwt')
