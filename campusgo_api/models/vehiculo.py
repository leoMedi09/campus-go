from ..conexionBD import Conexion
import pymysql

class Vehiculo:
       
    def registrar(self, conductor_id, marca, modelo, placa, color, pasajeros):
        #Abrir la conexión
        con = Conexion().open
        
        #Crear un cursor para ejecutar la sentencia sql
        cursor = con.cursor()
        
        #Definir la sentencia sql para validar el vehiculo por placa
        sql = "SELECT 1 AS cantidad FROM vehiculo WHERE placa=%s"
        
        #Ejecutar la sentencia
        cursor.execute(sql,[placa])
        
        #Recuperar los datos del usuario
        resultado = cursor.fetchone()
        
        #Validar por placa
        if resultado:
            return False, 'La placa que intenta registrar ya se encuentra registrada'
        
        #Definir la sentencia sql
        sql = """
            INSERT INTO vehiculo (conductor_id, marca, modelo, placa, color, pasajeros, estado_id) 
            VALUES (%s, %s, %s, %s, %s, %s, 1);
        """
        
        #Ejecutar la sentencia
        cursor.execute(sql,[conductor_id, marca, modelo, placa, color, pasajeros])
        
        #Confirmar los datos en la BD
        con.commit()
        
        #Cerrar el curso y la conexión
        cursor.close()
        con.close()
        
        #Retonar al final true
        return True, 'ok'
    
    def listar_por_conductor(self, conductor_id):
        con = Conexion().open
        cursor = con.cursor(pymysql.cursors.DictCursor)
        try:
            sql = """
                SELECT id, marca, modelo, placa, color, pasajeros
                FROM vehiculo
                WHERE conductor_id = %s AND estado_id = 1
                ORDER BY marca, modelo, placa
            """
            cursor.execute(sql, [conductor_id])
            datos = cursor.fetchall() or []
            return True, datos
        except Exception as e:
            return False, str(e)
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                con.close()
            except Exception:
                pass