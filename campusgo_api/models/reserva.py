from ..conexionBD import Conexion

class Reserva:
    def registrar(self, pasajero_id, fecha_reserva, observacion, detalles_viaje):

        try:
            # 1. Abrir la conexión
            con = Conexion().open
            cursor = con.cursor()

            # 2. Insertar en la tabla de reserva
            sql_reserva = """
                INSERT INTO reserva (pasajero_id, fecha_reserva, observacion)
                VALUES (%s, %s, %s);
            """
            cursor.execute(sql_reserva, [pasajero_id, fecha_reserva, observacion])

            # 3. Obtener el último id de la reserva registrada
            reserva_id = cursor.lastrowid
            if not reserva_id:
                raise Exception("No se pudo obtener el ID, porfavor verifique.")
            
            # 4. Insertar en reserva_viaje y actualizar en la tabla viaje
            sql_reserva_viaje = """ 
                INSERT INTO reserva_viaje (reserva_id, viaje_id, estado_id)
                VALUES (%s, %s, %s) ;    
                """
            sql_actualizar_viaje = """
                UPDATE viaje SET asientos_disponibles = asientos_disponibles - 1
                WHERE id = %s AND asientos_disponibles > 0;
            """
            # 5. Iterar en el json array, el cual trae los viajes selecionados por el pasajero 

            for detalle in detalles_viaje:
                viaje_id = detalle.get("viaje_id")
                estado_id = detalle.get("estado_id")

                # 5.1 Reducir el número de asientos disponibles
                cursor.execute(sql_actualizar_viaje, [viaje_id])

                # Verificar si se actualizó algún registro (es decir si habían asientos disponibles)
                if cursor.rowcount == 0:
                    raise Exception(f"No hay asientos disponibles para el viaje con ID {viaje_id}")
                     
                # 5.2 Insertar en la tabla reserva_viaje
                cursor.execute(sql_reserva_viaje, [reserva_id, viaje_id, estado_id])


            # 5.3 (Ejercicios)
            for detalle in detalles_viaje:
                viaje_id = detalle.get("viaje_id")

                # (Ejercicio) Verificar si el viaje_id ingresado es válido
                if not viaje_id or viaje_id <= 0:
                    raise Exception(f"El viaje con el ID {viaje_id} no es válido.")

                # (Ejercicio) #Validar que la fecha de reserva coincida con la fecha del viaje seleccionado
                fecha_reserva = detalle.get("fecha_viaje")
          


            # 6. Confirmar la transacción (Registro de la reserva, registro de la reserva_Viaje y actualización de asientos disponibles)
            con.commit()
            # 7. Retornar una respuesta
            return True, "Reserva y detalles registrados con éxito."
    
        except Exception as e:
            # 8. En caso de ocurra un error hacer rollback y abortar la transacción
            con.rollback()
        
            # 9 . Retornar el error específico
            return False, f"Error al registrar la reserva: {str(e)}"
        
        finally:
            # 10. Cerrar el cursor y la conexión
            cursor.close()
            con.close()
          
    #Hacer una cancelación de reserva de un pasajero solo si se hace con mínimo 1 hora de anticipación, además que no se haya embarcado
    
    #Hacer una cancelación de reserva de un conductor solo si se hace con mínimo 1 hora de anticipación, además que no se haya embarcado