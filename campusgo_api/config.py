import os
import base64
import tempfile

class Config:
    DB_HOST = os.environ.get('DB_HOST', 'gateway01.us-east-1.prod.aws.tidbcloud.com')
    DB_USER = os.environ.get('DB_USER', '2FaYsF4hcm2iFVK.root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'KAWIpAJ29lNiPfk7')
    DB_NAME = os.environ.get('DB_NAME', 'campusgo')
    DB_PORT = int(os.environ.get('DB_PORT') or 4000)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_secreta_para_jwt')

    # SSL/TLS
    DB_USE_SSL = str(os.environ.get('DB_USE_SSL', 'true')).lower() in ('1', 'true', 'yes')

    # Leer CA desde variable o archivo
    DB_SSL_CA_B64 = os.environ.get('DB_SSL_CA_B64', '')
    if not DB_SSL_CA_B64:
        ca_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db_ssl_ca_b64.txt')
        if os.path.exists(ca_file_path):
            with open(ca_file_path, 'r') as f:
                DB_SSL_CA_B64 = f.read().strip()

    # Crear archivo temporal para el certificado
    DB_SSL_CA_PATH = None
    if DB_SSL_CA_B64:
        try:
            decoded_bytes = base64.b64decode(DB_SSL_CA_B64)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
            temp_file.write(decoded_bytes)
            temp_file.close()
            DB_SSL_CA_PATH = temp_file.name
        except Exception as e:
            print(f"⚠️ Error decodificando DB_SSL_CA_B64: {e}")
            DB_SSL_CA_PATH = None

    # ⚙️ NUEVO: controla si se exponen las rutas de debug
    EXPOSE_DEBUG_ROUTES = os.environ.get('EXPOSE_DEBUG_ROUTES', 'True').lower() in ('1', 'true', 'yes')
