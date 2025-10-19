from functools import wraps
from flask import request, jsonify

# Some deploys or import layouts may cause the module to be importable as
# top-level 'tools' instead of the package-relative module. Try both
# forms so the code works both locally and in the container.
try:
    from .jwt_utils import verificar_token
except ImportError as exc:
    raise ImportError('Failed to import jwt_utils from campusgo_api.tools: ' + str(exc))

def jwt_token_requerido(f):
    @wraps(f)
    def envoltura(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or 'Bearer ' not in auth_header:
            return jsonify({'status': False, 'data': None, 'message': 'Cabecera no válida'}), 401

        token = auth_header.split('Bearer ')[1].strip()
        if not token:
            return jsonify({'message': 'Token requerido'}), 401

        payload = verificar_token(token)
        if not payload:
            return jsonify({'message': 'Token inválido o expirado'}), 401

        # Optionally, attach payload to request context if needed in handlers
        return f(*args, **kwargs)
    return envoltura
