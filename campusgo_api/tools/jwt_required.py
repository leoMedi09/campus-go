from functools import wraps
from flask import request, jsonify

# Some deploys or import layouts may cause the module to be importable as
# top-level 'tools' instead of the package-relative module. Try both
# forms so the code works both locally and in the container.
try:
    from .jwt_utils import verificar_token
except Exception:
    try:
        from tools.jwt_utils import verificar_token
    except Exception:
        # Let import error surface later when used; assign a placeholder
        verificar_token = None

def jwt_token_requerido(f):
    @wraps(f)
    def envoltura(*args, **kwargs):
        token = None
        if not request.headers.get("Authorization"):
            return jsonify({'status': False, 'data': None, 'message': 'Cabecera no válida'}), 401

        token = request.headers.get("Authorization").split('Bearer ')[1] #Obtener el token del encabezado de la solicitud (Header). Split eliminar 'Bearer ' del token

        if not token:
            return jsonify({'message': 'Token requerido'}), 401

        payload = verificar_token(token)
        if not payload:
            return jsonify({'message': 'Token inválido o expirado'}), 401

        return f(*args, **kwargs)
    return envoltura
