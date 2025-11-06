from flask import Blueprint, request, jsonify
from ..models.viajes import Viaje
from ..tools.jwt_required import jwt_token_requerido, verificar_roles

#Crear un modulo blueprint para implementar el servicio web de usuario (login, cambiar clave, registrar, etc)
ws_viaje = Blueprint('ws_viaje', __name__)

#Instanciar a la clase usuario
viaje= Viaje()

@ws_viaje.route('/viajes/filtrar', methods=['POST'])
 
def listar_viajes():
    try:
        filtros = request.get_json()
        
        if not filtros:
            return jsonify({
                "status": False,
                "message": "No se proporcionaron filtros"
            }), 400
        
        resultado = viaje.listarViajes(filtros)
        
        return jsonify({
            "status": True,
            "data": resultado["data"]
        }), 200

    except Exception as e:
        print(f"Error en listar_viajes: {e}")
        return jsonify({
            "status": False,
            "data": None,
            "message": f"Error interno: {str(e)}"
        }), 500

@ws_viaje.route('/viaje/registrar', methods=['POST'])
@verificar_roles([2, 3])  # Solo Conductor (2) y Admin (3) pueden registrar viajes
def registrar_viaje():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": False,
                "data": None,
                "message": "No se proporcionaron datos"
            }), 400
        
        # Extraer parámetros
        vehiculo_id = data.get("vehiculo_id")
        punto_partida = data.get("punto_partida")
        destino = data.get("destino")
        lat_partida = data.get("lat_partida")
        lng_partida = data.get("lng_partida")
        lat_destino = data.get("lat_destino")
        lng_destino = data.get("lng_destino")
        fecha_hora_salida = data.get("fecha_hora_salida")
        asientos_ofertados = data.get("asientos_ofertados")
        restricciones = data.get("restricciones")
        estado_id = data.get("estado_id", 9)  # Por defecto estado 9 si no se especifica
        
        # Validar campos obligatorios
        if not all([vehiculo_id, punto_partida, destino, lat_partida, lng_partida, 
                   lat_destino, lng_destino, fecha_hora_salida, asientos_ofertados]):
            return jsonify({
                "status": False,
                "data": None,
                "message": "Faltan datos obligatorios"
            }), 400
        
        # Validar tipos de datos
        try:
            vehiculo_id = int(vehiculo_id)
            lat_partida = float(lat_partida)
            lng_partida = float(lng_partida)
            lat_destino = float(lat_destino)
            lng_destino = float(lng_destino)
            asientos_ofertados = int(asientos_ofertados)
            estado_id = int(estado_id)
        except (ValueError, TypeError):
            return jsonify({
                "status": False,
                "data": None,
                "message": "Tipos de datos inválidos"
            }), 400
        
        # Registrar el viaje
        resultado, mensaje = viaje.registrar(
            vehiculo_id=vehiculo_id,
            punto_partida=punto_partida,
            destino=destino,
            lat_partida=lat_partida,
            lng_partida=lng_partida,
            lat_destino=lat_destino,
            lng_destino=lng_destino,
            fecha_hora_salida=fecha_hora_salida,
            asientos_ofertados=asientos_ofertados,
            restricciones=restricciones,
            estado_id=estado_id
        )
        
        if resultado:
            return jsonify({
                "status": True,
                "data": None,
                "message": mensaje
            }), 201
        else:
            return jsonify({
                "status": False,
                "data": None,
                "message": mensaje
            }), 400
    
    except Exception as e:
        print(f"Error en registrar_viaje: {e}")
        return jsonify({
            "status": False,
            "data": None,
            "message": f"Error interno: {str(e)}"
        }), 500
