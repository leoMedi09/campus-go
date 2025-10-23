from ..conexionBD import Conexion
import pymysql.cursors
from datetime import datetime

class Viaje:
    def listarViajes(self, filtros):
        db = Conexion().open()  # Asegúrate de usar paréntesis si open es un método
        cursor = db.cursor(pymysql.cursors.DictCursor)

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
                query += f" AND LOWER(v.{campo_busqueda}) LIKE %s"
                params.append(f"%{texto_busqueda.lower()}%")

        if str(filtros.get("asientos_disponibles")).lower() in ["true", "1"]:
            query += " AND v.asientos_disponibles > 0"

        if str(filtros.get("sin_restricciones")).lower() in ["true", "1"]:
            query += " AND (v.restricciones IS NULL OR TRIM(v.restricciones) = '' OR LOWER(v.restricciones) = 'ninguna')"

        if filtros.get("desde"):
            try:
                desde = datetime.strptime(filtros["desde"], "%Y/%m/%d").strftime("%Y-%m-%d")
                query += " AND DATE(v.fecha_hora_salida) >= %s"
                params.append(desde)
            except ValueError:
                pass

        if filtros.get("hasta"):
            try:
                hasta = datetime.strptime(filtros["hasta"], "%Y/%m/%d").strftime("%Y-%m-%d")
                query += " AND DATE(v.fecha_hora_salida) <= %s"
                params.append(hasta)
            except ValueError:
                pass

        query += " ORDER BY v.fecha_hora_salida ASC"

        # -------------------- Ejecución --------------------
        cursor.execute(query, params)
        viajes = cursor.fetchall()

        cursor.close()
        db.close()

        # -------------------- Formatear salida --------------------
        resultado = {"data": []}

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
