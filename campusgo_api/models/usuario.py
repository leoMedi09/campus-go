from conexionBD import Conexion
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


class Usuario:
    def __init__(self):
        self.ph = PasswordHasher()
        
    def login(self, email, clave):
        #Abrir la conexión
        con = Conexion().open
        
        #Crear un cursor para ejecutar la sentencia sql
        cursor = con.cursor()
        
        #Definir la sentencia sql
        sql = "select id, concat(nombres, ' ', apellido_paterno, ' ', apellido_materno, ' ', nombres) as nombre_completo, email, clave from usuario where email = %s"
        
        #Ejecutar la sentencia
        cursor.execute(sql,[email])
        
        #Recuperar los datos del usuario
        resultado = cursor.fetchone()
        
        #Cerrar el curso y la conexión
        cursor.close()
        con.close()
        
        if resultado: #Verificando si se encontró al usuario con el email ingresado
            try:
                self.ph.verify(resultado['clave'], clave) #Verificando la clave almacenada en la BD con la clave que ingresó el usuario
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

    def registrar(self, apellido_paterno, apellido_materno, nombres, dni, telefono, email, clave, estado_id):
        #Abrir la conexión
        con = Conexion().open
        
        #Crear un cursor para ejecutar la sentencia sql
        cursor = con.cursor()
        
        #Definir la sentencia sql
        sql = """
            INSERT INTO usuario(apellido_paterno, apellido_materno,nombres, dni, telefono, email,estado_id, clave)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
        """
        
        #Ejecutar la sentencia
        cursor.execute(sql,[apellido_paterno, apellido_materno, nombres, dni, telefono, email, '1', self.ph.hash(clave)])
        
        #Hacer commit para guardar los cambios
        con.commit()
        
        #Cerrar el curso y la conexión
        cursor.close()
        con.close()

        #Retornar al final true
        return True
    
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