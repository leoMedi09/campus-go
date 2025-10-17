from flask import Flask, jsonify
# Use package-relative imports so the app can be loaded by gunicorn
from .routes.usuario import ws_usuario
from .routes.vehiculo import ws_vehiculo
from .routes.reserva import ws_reserva
import urllib.request
import socket
import os
from .conexionBD import Conexion

app = Flask(__name__)
app.register_blueprint(ws_usuario)
app.register_blueprint(ws_vehiculo)
app.register_blueprint(ws_reserva)


@app.route('/')
def home():
    return 'CampusGO - Running API Restful'


@app.route('/whoami', methods=['GET'])
def whoami():
    """Dev-only endpoint that returns the public IP address of this container.
    Useful to discover the outbound IP for whitelisting.
    """
    try:
        with urllib.request.urlopen('https://ifconfig.me/ip', timeout=5) as r:
            ip = r.read().decode().strip()
    except Exception as e:
        # fallback: try to get local socket name (not the public IP but useful)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            ip = f'error: {str(e)}'

    return jsonify({'ip': ip})


@app.route('/health-db', methods=['GET'])
def health_db():
    """Simple health check that tries to open a DB connection and run SELECT 1."""
    try:
        db = Conexion()
        cur = db.open.cursor()
        cur.execute('SELECT 1 as ok')
        row = cur.fetchone()
        return jsonify({'ok': True, 'result': row}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


#Iniciar el servicio web con Flask (solo para desarrollo local)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3006))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ('1', 'true')
    app.run(port=port, debug=debug, host='0.0.0.0')