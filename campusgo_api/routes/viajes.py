from flask import Blueprint, request, jsonify
from ..models.viajes import Viaje
from ..tools.jwt_required import jwt_token_requerido

#Crear un modulo blueprint para implementar el servicio web de usuario (login, cambiar clave, registrar, etc)
ws_viaje = Blueprint('ws_viaje', __name__)

#Instanciar a la clase usuario
viaje= Viaje()

@ws_viaje.route('/viajes/filtrar', methods=['POST'])
def listar_viajes():
    try:
        filtros = request.get_json()
        
        if not filtros:
            return jsonify({"error": "No se proporcionaron filtros"}), 400
        
        resultado = viaje.listarViajes(filtros)
        
        return jsonify(resultado), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500