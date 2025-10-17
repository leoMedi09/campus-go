from flask import Blueprint, request, jsonify
from ..models.reserva import Reserva
from ..tools.jwt_required import jwt_token_requerido
from datetime import datetime

#Crear un modulo blueprint para implementar el servicio web de reservas
ws_reserva = Blueprint('ws_reserva', __name__)

#Instanciar la clase reserva
reserva = Reserva()

#Crear un endpoint para registrar una reserva (posiblemente con múltiples viajes)
@ws_reserva.route('/reserva/registrar', methods=['POST'])
@jwt_token_requerido
def registrar():
    #Obtener los datos que se envian como parámetros de entrada
    data = request.get_json()
    
    #Pasar los datos a variables
    pasajero_id = data.get('pasajero_id')
    fecha_reserva = data.get('fecha_reserva') #Fecha en la que el usuario desea viajar
    observacion = data.get('observacion')
    detalles_viaje = data.get('detalles_viaje') #Este es un json array
    
    #Validar si contamos con los parámetros obligatorios
    if not all([pasajero_id, fecha_reserva, detalles_viaje]):
        return jsonify({'status': False, 'data': None, 'message': 'Faltan datos obligatorios'}), 400
    
    #Validar que detalles_viaje no sea una lista vacía
    if not isinstance(detalles_viaje, list) or len(detalles_viaje) == 0:
        return jsonify({'status': False, 'data': None, 'message': 'Detalles de viaje debe ser una lista con al menos un viaje'}), 400

    #Validar la fecha ingresada que sea de día actual en adelante
    fecha_reserva_date = datetime.strptime(fecha_reserva, "%Y-%m-%d").date()
    if not fecha_reserva_date >= datetime.now().date():
        return jsonify({'status': False, 'data': None, 'message': 'La fecha de reserva debe ser del día de hoy en adelante'}), 400

    #Registrar la reserva
    try:
        #Llamar al método registrar de la clase reserva
        resultado, mensaje = reserva.registrar(pasajero_id, fecha_reserva, observacion, detalles_viaje)
        
        if resultado:
            return jsonify({'status': True, 'data': None, 'message': mensaje}), 200
        else:
            #En caso de error (No hay asientos disponibles, algún dato que no se registro, etc)
            return jsonify({'status': False, 'data': None, 'message': mensaje}), 500
            

    except Exception as e:
        #Manejo de errores internos en el servidor
        return jsonify({'status': False, 'data': None, 'message': f"Error interno: {str(e)}"}), 500
  

