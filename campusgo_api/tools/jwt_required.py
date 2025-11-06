from functools import wraps
from flask import request, jsonify

# Some deploys or import layouts may cause the module to be importable as
# top-level 'tools' instead of the package-relative module. Try both
# forms so the code works both locally and in the container.
try:
    from .jwt_utils import verificar_token
    from ..conexionBD import Conexion
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

        # Attach payload to request context for use in handlers
        request.usuario_id = payload.get('usuario_id')
        return f(*args, **kwargs)
    return envoltura

def verificar_roles(roles_permitidos):
    """Decorador para verificar que el usuario tenga uno de los roles permitidos"""
    def decorador(f):
        @wraps(f)
        @jwt_token_requerido
        def envoltura(*args, **kwargs):
            usuario_id = getattr(request, 'usuario_id', None)
            if not usuario_id:
                return jsonify({'status': False, 'data': None, 'message': 'Usuario no identificado'}), 401
            
            # Verificar roles del usuario
            try:
                con = Conexion().open
                cursor = con.cursor()
                sql = "SELECT rol_id FROM usuario_rol WHERE usuario_id = %s AND estado_id = 1"
                cursor.execute(sql, [usuario_id])
                filas = cursor.fetchall()
                
                # Obtener lista de roles del usuario
                roles_usuario = []
                if filas:
                    for r in filas:
                        if isinstance(r, dict):
                            roles_usuario.append(r.get('rol_id'))
                        else:
                            roles_usuario.append(r[0])
                
                cursor.close()
                con.close()
                
                # Verificar si el usuario tiene alguno de los roles permitidos
                tiene_permiso = any(rol in roles_permitidos for rol in roles_usuario)
                
                if not tiene_permiso:
                    return jsonify({
                        'status': False, 
                        'data': None, 
                        'message': 'No tiene permisos para realizar esta acción'
                    }), 403
                
                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({
                    'status': False, 
                    'data': None, 
                    'message': f'Error al verificar permisos: {str(e)}'
                }), 500
        return envoltura
    return decorador
