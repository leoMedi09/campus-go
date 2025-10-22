from ..conexionBD import Conexion
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime

class Usuario:
    def __init__(self):
        self.ph = PasswordHasher()
    
    def login(self, email, clave):
        # Abrir la conexión
        con = Conexion().open

        # Crear un cursor para ejecutar la sentencia sql
        cursor = con.cursor()
        
        # === CONSULTA SQL CORREGIDA CON JOIN v2 ===
        # Une las tablas usando 'usuario_id' como clave y devuelve
        # el id del usuario bajo el alias 'id' para compatibilidad con el frontend.
        sql = """
            SELECT
                u.id,
                ur.rol_id,
                CONCAT(u.nombres, ' ', u.apellido_paterno, ' ', u.apellido_materno) AS nombre,
                u.email,
                u.clave
            FROM
                usuario AS u
            JOIN
                usuario_rol AS ur ON u.id = ur.usuario_id
            WHERE
                u.email = %s AND ur.estado_id = 1
            LIMIT 1
        """
        
        #Ejecutar la sentencia
        cursor.execute(sql,[email])
                
        # Recuperar los datos del usuario como una tupla
        row = cursor.fetchone()

        # Si se encontró una fila, la convertimos a diccionario
        if row:
            # Obtenemos los nombres de las columnas desde el cursor
            columns = [col[0] for col in cursor.description]
            # Creamos el diccionario combinando los nombres de columna y los valores de la fila
            resultado = dict(zip(columns, row))
        else:
            resultado = None

        #Cerrar el curso y la conexión
        cursor.close()
        con.close()

        if resultado: #Verificando si se encontró al usuario con el email ingresado
            try:
                self.ph.verify(resultado['clave'], clave) 
                return resultado
            except VerifyMismatchError:
                return None
            
        else: #No se ha encontrado al usuario con el email ingreso
            return None
        
    
        
    def obtener_foto(self,id):
        #Abrir la conexión
        con = Conexion().open
        
        #Crear un cursor para ejecutar la sentencia sql
        cursor = con.cursor()
        
        #Definir la sentencia sql
        sql = "select id, coalesce(foto,'x') as foto from usuario where id = %s"
        
        #Ejecutar la sentencia
        cursor.execute(sql,[id])
        
        #Recuperar los datos del usuario
        resultado = cursor.fetchone()
        
        #Cerrar el curso y la conexión
        cursor.close()
        con.close()

        if resultado and resultado['foto'] != 'x':
            return resultado #devolver el resultado si tiene foto
        
        #Si no hay foto devolver None
        return None

    def registrar(self, apellido_paterno, apellido_materno, nombres, dni, telefono, email, clave, rol_id, vehiculo_data=None):
        try:
            # Inicializar recursos
            con = None
            cursor = None

            # 1. Abrir la conexión
            con = Conexion().open
            cursor = con.cursor()

            # 2. Iniciar la transacción
            con.begin()

            # 3. Validar si el email o DNI ya existen
            sql_check_existencia = "SELECT id FROM usuario WHERE email = %s OR dni = %s"
            cursor.execute(sql_check_existencia, [email, dni])
            if cursor.fetchone():
                raise Exception("El email o DNI ya se encuentra registrado.")

            # 4. Hashear la contraseña con Argon2 (ESTA ES LA CORRECCIÓN)
            clave_hasheada = self.ph.hash(clave)

            # 5. Insertar en la tabla 'usuario'
            sql_usuario = """
                INSERT INTO usuario (apellido_paterno, apellido_materno, nombres, dni, telefono, email, clave, estado_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1);
            """
            cursor.execute(sql_usuario, [apellido_paterno, apellido_materno, nombres, dni, telefono, email, clave_hasheada])

            # 6. Obtener el ID del usuario recién creado
            usuario_id = cursor.lastrowid
            if not usuario_id:
                raise Exception("Error crítico: No se pudo obtener el ID del nuevo usuario.")

            # 7. Insertar en la tabla 'usuario_rol'
            sql_usuario_rol = """
                INSERT INTO usuario_rol (usuario_id, rol_id, fecha_hora_asignacion, estado_id)
                VALUES (%s, %s, %s, 1);
            """
            cursor.execute(sql_usuario_rol, [usuario_id, rol_id, datetime.now()])

            # 8. Lógica condicional para registrar el vehículo
            if rol_id == 2: # Asumimos que 2 es el rol_id para 'Conductor'
                if not vehiculo_data:
                    raise Exception("Faltan los datos del vehículo para el rol Conductor.")
                
                # Extraer datos del vehículo
                marca = vehiculo_data.get('marca')
                modelo = vehiculo_data.get('modelo')
                placa = vehiculo_data.get('placa')
                color = vehiculo_data.get('color')
                pasajeros = vehiculo_data.get('pasajeros')

                if not all([marca, modelo, placa, color, pasajeros]):
                    raise Exception("Faltan datos obligatorios del vehículo (marca, modelo, placa, color, pasajeros).")

                sql_check_placa = "SELECT id FROM vehiculo WHERE placa = %s"
                cursor.execute(sql_check_placa, [placa])
                if cursor.fetchone():
                    raise Exception(f"La placa del vehículo '{placa}' ya se encuentra registrada.")

                sql_vehiculo = """
                    INSERT INTO vehiculo (conductor_id, marca, modelo, placa, color, pasajeros, estado_id)
                    VALUES (%s, %s, %s, %s, %s, %s, 1);
                """
                cursor.execute(sql_vehiculo, [usuario_id, marca, modelo, placa, color, pasajeros])

            # 9. Confirmar la transacción
            con.commit()
            return usuario_id, "Usuario registrado con éxito."

        except Exception as e:
            if con:
                con.rollback()
            # Devuelve None en caso de error
            return None, str(e)

        except Exception as e:
            if con:
                con.rollback()
            return False, str(e)

        finally:
            if cursor:
                cursor.close()
            if con:
                con.close()
    
    def validar_existente(self, email, dni):
        #Abrir la conexión
        con = Conexion().open
        
        #Crear un cursor para ejecutar la sentencia sql
        cursor = con.cursor()
        
        #Definir la sentencia sql
        sql = "select count(*) as cantidad from usuario where email = %s or dni = %s"
        
        #Ejecutar la sentencia
        cursor.execute(sql,[email, dni])
        
        #Recuperar los datos del usuario
        resultado = cursor.fetchone()
        
        #Cerrar el curso y la conexión
        cursor.close()
        con.close()

        #Validar si existe email
        if resultado and resultado['cantidad'] > 0:
            return False, "El email ya está en uso" #Ya existe el email

        #Validar si existe dni
        if resultado and resultado['cantidad'] > 0:
            return False, "El DNI ya está en uso" #Ya existe el DNI

    def actualizar(self, apellido_paterno, apellido_materno, nombres, dni, telefono, email, id):
        #Abrir la conexión
        con = Conexion().open
        
        #Crear un cursor para ejecutar la sentencia sql
        cursor = con.cursor()
        
        #Definir la sentencia sql
        sql = """
            UPDATE 
                usuario 
            SET 
            apellido_paterno=%s, 
            apellido_materno=%s,
            nombres=%s, 
            dni=%s, 
            telefono=%s, 
            email=%s,
            fecha_modificacion = NOW()
            WHERE 
                id = %s
        """
        
        #Ejecutar la sentencia
        cursor.execute(sql,[apellido_paterno, apellido_materno, nombres, dni, telefono, email, id])
        
        #Hacer commit para guardar los cambios
        con.commit()
        
        #Cerrar el curso y la conexión
        cursor.close()
        con.close()

        #Retornar al final true
        return True

    def darbaja(self, id):
        #Abrir la conexión
        con = Conexion().open

        #Crear un cursor para ejecutar la sentencia sql
        cursor = con.cursor()

        #Definir la sentencia sql
        sql = "UPDATE usuario SET estado_id = 2, fecha_modificacion = NOW() WHERE id = %s"

        #Ejecutar la sentencia
        cursor.execute(sql, [id])

        #Hacer commit para guardar los cambios
        con.commit()

        #Cerrar el curso y la conexión
        cursor.close()
        con.close()

        #Retornar al final true
        return True

    def actualizarfoto(self, foto, id):
        #Abrir la conexión
        con = Conexion().open

        #Crear un cursor para ejecutar la sentencia sql
        cursor = con.cursor()

        #Definir la sentencia sql
        sql = "UPDATE usuario SET foto = %s, fecha_modificacion = NOW() WHERE id = %s"

        #Ejecutar la sentencia
        cursor.execute(sql, [foto, id])

        #Hacer commit para guardar los cambios
        con.commit()

        #Cerrar el curso y la conexión
        cursor.close()
        con.close()

        #Retornar al final true
        return True, "Foto actualizada correctamente"

    def actualizarclave(self, id, clave, clave_nueva):
        #Abrir la conexión
        con = Conexion().open

        #Crear un cursor para ejecutar la sentencia sql
        cursor = con.cursor()

        #Obtener el hash de la clave actual desde la base de datos
        sql = "SELECT clave FROM usuario WHERE id = %s"
        cursor.execute(sql, [id])
        resultado = cursor.fetchone()
        hash_guardado = resultado['clave'] if resultado else None

        #Verificar la clave actual
        try:
            self.ph.verify(hash_guardado, clave)
        except VerifyMismatchError:
            cursor.close()
            con.close()
            return False, "La clave actual es incorrecta"

        #Actualizar la clave
        sql = "UPDATE usuario SET clave = %s, fecha_modificacion = NOW() WHERE id = %s"
        cursor.execute(sql, [self.ph.hash(clave_nueva), id])
        con.commit()

        #Cerrar el curso y la conexión
        cursor.close()
        con.close()

        #Retornar al final true
        return True, "Clave actualizada correctamente"