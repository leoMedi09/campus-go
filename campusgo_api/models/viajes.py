from ..conexionBD import Conexion
import pymysql.cursors
from datetime import datetime

class Viaje:
    def listarViajes(self, filtros):
        db = Conexion().open
        cursor = db.cursor(pymysql.cursors.DictCursor)

        # Consulta principal: viajes + vehículo + conductor + estado
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
                veh.color,
                u.id AS conductor_id,
                u.nombres,
                u.apellido_paterno,
                u.apellido_materno,
                u.foto AS foto_conductor
            FROM viaje v
            JOIN vehiculo veh ON v.vehiculo_id = veh.id
            JOIN usuario u ON veh.conductor_id = u.id
            JOIN estado e ON v.estado_id = e.id
            WHERE 1=1
        """

        params = []

        # Filtros dinámicos
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

        cursor.execute(query, params)
        viajes = cursor.fetchall()

        # Obtener IDs para buscar pasajeros
        viaje_ids = [v["viaje_id"] for v in viajes] if viajes else []

        pasajeros_por_viaje = {}
        if viaje_ids:
            placeholders = ','.join(['%s'] * len(viaje_ids))
            query_pasajeros = f"""
                SELECT DISTINCT
                    rv.viaje_id,
                    u.id AS usuario_id,
                    u.foto,
                    r.fecha_reserva
                FROM reserva_viaje rv
                JOIN reserva r ON rv.reserva_id = r.id
                JOIN usuario u ON r.pasajero_id = u.id
                WHERE rv.viaje_id IN ({placeholders})
                ORDER BY rv.viaje_id, r.fecha_reserva DESC
            """
            cursor.execute(query_pasajeros, viaje_ids)
            pasajeros_data = cursor.fetchall()
            
            for p in pasajeros_data:
                viaje_id = p["viaje_id"]
                pasajeros_por_viaje.setdefault(viaje_id, []).append(p)

        cursor.close()
        db.close()

        # Construir URLs completas de fotos
        base_url = "https://campusgo-api.onrender.com"  # o http://192.168.1.X:3006 si estás local
        resultado = {"data": []}

        for v in viajes:
            # Foto del conductor
            foto_conductor = v["foto_conductor"] or "uploads/fotos/usuarios/default.png"
            if not foto_conductor.startswith("http"):
                foto_conductor = f"{base_url}/{foto_conductor}"

            # Fotos de pasajeros
            pasajeros = pasajeros_por_viaje.get(v["viaje_id"], [])
            pasajeros_fotos = []
            for p in pasajeros:
                foto_path = p["foto"] or "uploads/fotos/usuarios/default.png"
                if not foto_path.startswith("http"):
                    foto_url = f"{base_url}/{foto_path}"
                else:
                    foto_url = foto_path
                pasajeros_fotos.append(foto_url)

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
                "restricciones": v["restricciones"] or "Ninguna",
                "estado": v["estado"],
                "vehiculo": {
                    "id": v["vehiculo_id"],
                    "marca": v["marca"],
                    "modelo": v["modelo"],
                    "placa": v["placa"],
                    "color": v["color"]
                },
                "conductor": {
                    "id": v["conductor_id"],
                    "nombre": f"{v['nombres']} {v['apellido_paterno']} {v['apellido_materno']}",
                    "foto": foto_conductor
                },
                "pasajeros_fotos": pasajeros_fotos
            }
            resultado["data"].append(viaje)

        return resultado
