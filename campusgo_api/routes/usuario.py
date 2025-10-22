from flask import Blueprint, request, jsonify, send_from_directory
from ..models.usuario import Usuario
from ..tools.jwt_utils import generar_token
from ..tools.jwt_required import jwt_token_requerido
from ..tools.security import password_validate
import os
from werkzeug.utils import secure_filename


#Crear un modulo blueprint para implementar el servicio web de usuario (login, cambiar clave, agregar, etc)
ws_usuario = Blueprint('ws_usuario', __name__)

#Instanciar a la clase usuario
usuario = Usuario()

#Crear un endpoint para permitir al usuario iniciar sesión(login)
@ws_usuario.route('/login', methods=['POST'])
def login():
    #Obtener los datos que se envian como parámetros de entrada
    data = request.get_json()
    
    #pasar los datos de email y clave a variables
    email = data.get('email')
    clave = data.get('clave')
    
    #Validar si contamos con los parámetros de email y clave
    if not all([email, clave]):
        return jsonify({'status': False, 'data': None, 'message': 'Faltan datos obligatorios'}), 400
    
    try:
        #Llamar al método login
        resultado = usuario.login(email, clave)
        
        if resultado: #Si hay resultado
            #retirar la clave del resultado antes de imprimir
            resultado.pop('clave', None)
            
            #Generar el token con JWT
            token = generar_token({"usuario_id": resultado['id']}, 60*60)

            #Incluir en el resultado el token generado
            resultado['token'] = token
            
            #Imprimir el resultado
            return jsonify({'status': True, 'data': resultado, 'message':'Inicio de sesión satisfactorio'}), 200
        
        else:
            return jsonify({'status': False, 'data': None, 'message': 'Credenciales incorrectas'}), 401
            
    except Exception as e:
        return jsonify({'status': False, 'data': None, 'message': str(e)}), 500
    
#Crear un endpoint para obtener la foto del usuario mediante su id
@ws_usuario.route('/usuario/foto/<id>', methods=['GET'])
@jwt_token_requerido
def obtener_foto(id):

    #Validar si se cuenta con el id para mostrar la foto
    if not all([id]):
        return jsonify({'status': False, 'data': None, 'message': 'Faltan datos obligatorios'}), 400
    
    try:
        resultado = usuario.obtener_foto(id)
        if resultado:
            return send_from_directory('uploads/fotos/usuarios', resultado['foto'])
        else:
            return send_from_directory('uploads/fotos/usuarios', 'default.png')
    except Exception as e:
        return jsonify({'status': False, 'data': None, 'message': str(e)}), 500

#Crear un endpoint para registar nuevos usuarios
@ws_usuario.route('/usuario/registrar', methods=['POST'])
def registrar():
    # Obtener los datos JSON que envía la aplicación Android
    data = request.get_json()
    if not data:
        return jsonify({'status': False, 'data': None, 'message': 'No se recibieron datos (JSON inválido)'}), 400

    # Extraer datos del JSON
    apellido_paterno = data.get('apellido_paterno')
    apellido_materno = data.get('apellido_materno')
    nombres = data.get('nombres')
    dni = data.get('dni')
    telefono = data.get('telefono')
    email = data.get('email')
    clave = data.get('clave')
    clave_confirmada = data.get('clave_confirmada') 
    rol_id = data.get('rol_id')
    vehiculo_data = data.get('vehiculo') 

    # Validar campos obligatorios básicos
    if not all([apellido_paterno, nombres, dni, email, clave, clave_confirmada, rol_id]):
        return jsonify({'status': False, 'data': None, 'message': 'Faltan datos obligatorios'}), 400

    # Validar que las contraseñas coincidan
    if clave != clave_confirmada:
        return jsonify({'status': False, 'data': None, 'message': 'Las contraseñas no coinciden'}), 400
        
    # Validar que rol_id sea 1 (Estudiante) o 2 (Conductor)
    if rol_id not in [1, 2]:
        return jsonify({'status': False, 'data': None, 'message': 'El rol especificado no es válido'}), 400
    
    
    # Opcional: Si tienes una función para validar la complejidad de la clave, úsala aquí
    # valida, mensaje = password_validate(clave)
    # if not valida:
    #     return jsonify({'status': False, 'data': None, 'message': mensaje}), 400

    try:
        
        resultado, mensaje = usuario.registrar(
            apellido_paterno, apellido_materno, nombres, dni, telefono, email, clave, rol_id, vehiculo_data
        )

        if resultado:
            return jsonify({'status': True, 'data': { 'id': resultado }, 'message': mensaje}), 201 
        else:
            return jsonify({'status': False, 'data': None, 'message': mensaje}), 409 

    except Exception as e:
        # Manejo de errores internos inesperados en el servidor
        return jsonify({'status': False, 'data': None, 'message': f"Error interno del servidor: {str(e)}"}), 500


    
#Crear un endpoint para actualizar al usuario
@ws_usuario.route('/usuario/actualizar', methods=['PUT'])
@jwt_token_requerido
def actualizar():
    
    #Obtener los datos que se envian como parámetros de entrada
    data = request.get_json()
    
    #pasar los datos a variables
    apellido_paterno = data.get('apellido_paterno')
    apellido_materno = data.get('apellido_materno')
    nombres = data.get('nombres')
    dni = data.get('dni')
    telefono = data.get('telefono')
    email = data.get('email')
    id = data.get('id')

    #Validar si contamos con los parámetros obligatorios
    if not all([apellido_paterno, apellido_materno, nombres, dni, telefono, email, id]):
        return jsonify({'status': False, 'data': None, 'message': 'Faltan datos obligatorios'}), 400

    #Actualizar al usuario
    try:
        resultado = usuario.actualizar(apellido_paterno, apellido_materno, nombres, dni, telefono, email, id)

        if resultado:
            return jsonify({'status': True, 'data': resultado, 'message': 'Usuario actualizado correctamente'}), 200
        else:
            return jsonify({'status': False, 'data': None, 'message': 'Ocurrió un error al actualizar al usuario'}), 500
        
    except Exception as e:
        return jsonify({'status': False, 'data': None, 'message': str(e)}), 500
    

#Crear un endpoint para dar de baja a un usuario
@ws_usuario.route('/usuario/darbaja', methods=['DELETE'])
@jwt_token_requerido
def darbaja():
    #Obtener los datos que se envian como parámetros de entrada

    data = request.get_json()
    id = data.get('id') 

    #Validar si el id es válido
    if not id:
        return jsonify({'status': False, 'data': None, 'message': 'ID inválido'}), 400

    #Dar de baja al usuario
    try:
        resultado = usuario.darbaja(id)

        if resultado:
            return jsonify({'status': True, 'data': resultado, 'message': 'Usuario dado de baja correctamente'}), 200
        else:
            return jsonify({'status': False, 'data': None, 'message': 'Ocurrió un error al dar de baja al usuario'}), 500

    except Exception as e:
        return jsonify({'status': False, 'data': None, 'message': str(e)}), 500
    

#Crear un endpoint para actualizar la foto del usuario
@ws_usuario.route('/usuario/actualizarfoto', methods=['PUT'])
@jwt_token_requerido
def actualizarfoto():
    
    #Obtener los datos que se envian como parámetros de entrada

    id = request.form.get('id')
    foto = request.files.get('foto')

    #Validar si contamos con los parámetros obligatorios
    if not all([id, foto]):
        return jsonify({'status': False, 'data': None, 'message': 'Faltan datos obligatorios'}), 400

    #Actualizar la foto del usuario

    try:
        nombre_foto = None

        if 'foto' in request.files:
            extension = os.path.splitext(foto.filename)[1]
            nombre_foto = secure_filename(f"{id}{extension}")
            ruta_foto = os.path.join("campusgo_api", "uploads", "fotos", "usuarios", nombre_foto)
            foto.save(ruta_foto)

            resultado, mensaje = usuario.actualizarfoto(nombre_foto, id)

            if resultado:
                return jsonify({'status': True, 'data': resultado, 'message': 'Foto de usuario actualizada correctamente'}), 200
            else:
                return jsonify({'status': False, 'data': None, 'message': 'Ocurrió un error al actualizar la foto de usuario'}), 500
        else:
            return jsonify({'status': False, 'data': None, 'message': mensaje}), 500

    except Exception as e:
        return jsonify({'status': False, 'data': None, 'message': str(e)}), 500
    
#Crear un endpoint para cambiar la clave del usuario
@ws_usuario.route('/usuario/actualizarclave', methods=['PUT'])
@jwt_token_requerido
def actualizarclave():
    #Obtener los datos que se envian como parámetros de entrada
    data = request.get_json()
    
    #pasar los datos a variables
    id = data.get('id')
    clave = data.get('clave')
    clave_nueva = data.get('clave_nueva')
    clave_confirmada = data.get('clave_confirmada')

    #Validar si contamos con los parámetros obligatorios
    if not all([id, clave, clave_nueva, clave_confirmada]):
        return jsonify({'status': False, 'data': None, 'message': 'Faltan datos obligatorios'}), 400
    
    #Validar si las claves coinciden
    if clave_nueva != clave_confirmada:
        return jsonify({'status': False, 'data': None, 'message': 'Las claves no coinciden'}), 500

    #Validar la complejidad de la clave
    valida, mensaje = password_validate(clave_nueva)
    if not valida:
        return jsonify({'status': False, 'data': None, 'message': mensaje}), 500
    
    #Actualizar la clave del usuario
    try:
        resultado, mensaje = usuario.actualizarclave(id, clave, clave_nueva)

        if resultado:
            return jsonify({'status': True, 'data': resultado, 'message': 'Clave de usuario actualizada correctamente'}), 200
        else:
            return jsonify({'status': False, 'data': None, 'message': mensaje}), 500
        
    except Exception as e:
        return jsonify({'status': False, 'data': None, 'message': str(e)}), 500