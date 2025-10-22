import json
from campusgo_api.conexionBD import Conexion

email = 'leonardoguzmans06@gmail.com'
con = None
try:
    con = Conexion().open
    cur = con.cursor()
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
    cur.execute(sql, [email])
    row = cur.fetchone()
    print(json.dumps(row, ensure_ascii=False, default=str))
    cur.close()
except Exception as e:
    print('ERROR:', repr(e))
finally:
    try:
        if con:
            con.close()
    except Exception:
        pass
