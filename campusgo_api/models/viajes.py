from ..conexionBD import Conexion

class Viaje:
    
    def listarViajes(self, filtros):
        db = Conexion().open
        cursor = db.cursor(dictionary=True)

        query = """
            SELECT 
                v.id AS viaje_id,
                v.punto_partida,
                v.destino,
                v.lat_partida,
                v.lng_partida,
                v.lat_destino,
                v.lng_destino,
                v.fecha_hora_salida,
                v.asientos_ofertados,
                v.asientos_disponibles,
                v.restricciones,
                e.nombre AS estado,
                veh.id AS vehiculo_id,
                veh.marca,
                veh.modelo,
                veh.placa,
                veh.color
            FROM viaje v
            JOIN vehiculo veh ON v.vehiculo_id = veh.id
            JOIN estado e ON v.estado_id = e.id
            WHERE 1=1
        """

        params = []

        # -------------------- Filtros --------------------
        campo_busqueda = filtros.get("campo_busqueda")
        texto_busqueda = filtros.get("texto_busqueda")

        if campo_busqueda and texto_busqueda:
            if campo_busqueda in ["punto_partida", "destino"]:
                query += f" AND v.{campo_busqueda} LIKE %s"
                params.append(f"%{texto_busqueda}%")

        if filtros.get("asientos_disponibles") in [True, "true", "1", 1]:
            query += " AND v.asientos_disponibles > 0"

        if filtros.get("sin_restricciones") in [True, "true", "1", 1]:
            query += " AND (v.restricciones IS NULL OR v.restricciones = '')"

        if filtros.get("desde"):
            query += " AND v.fecha_hora_salida >= %s"
            params.append(filtros["desde"])

        if filtros.get("hasta"):
            query += " AND v.fecha_hora_salida <= %s"
            params.append(filtros["hasta"])

        query += " ORDER BY v.fecha_hora_salida ASC"

        # -------------------- Ejecución --------------------
        cursor.execute(query, params)
        viajes = cursor.fetchall()

        cursor.close()
        db.close()

        # -------------------- Formatear salida --------------------
        resultado = {
            "data": []
        }

        for v in viajes:
            viaje = {
                "viaje_id": v["viaje_id"],
                "destino": v["destino"],
                "punto_partida": v["punto_partida"],
                "lat_partida": v["lat_partida"],
                "lng_partida": v["lng_partida"],
                "lat_destino": v["lat_destino"],
                "lng_destino": v["lng_destino"],
                "fecha_hora_salida": v["fecha_hora_salida"].strftime("%d-%m-%Y %H:%M:%S"),
                "asientos_ofertados": v["asientos_ofertados"],
                "asientos_disponibles": v["asientos_disponibles"],
                "restricciones": v["restricciones"],
                "estado": v["estado"],
                "vehiculo": {
                    "id": v["vehiculo_id"],
                    "marca": v["marca"],
                    "modelo": v["modelo"],
                    "placa": v["placa"],
                    "color": v["color"]
                }
            }

            resultado["data"].append(viaje)

        return resultado