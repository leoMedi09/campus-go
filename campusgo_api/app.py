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


@app.route('/__debug__routes_env', methods=['GET'])
def debug_routes_env():
    """Temporary debug endpoint (remove after debugging):
    Returns the list of registered routes and a safe summary of DB_* env vars.
    Does NOT expose full secret values — values are masked or reported as present/absent.
    """
    def mask(v: str) -> str:
        if v is None:
            return None
        if len(v) <= 6:
            return '***'
        return v[:3] + '...' + v[-3:]

    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({'rule': str(rule), 'methods': sorted(list(rule.methods))})

    db_env = {}
    for k, v in os.environ.items():
        if k.startswith('DB_'):
            # Mask value to avoid leaking secrets; include length to know presence
            db_env[k] = {'present': True, 'masked': mask(v), 'length': len(v)}

    # Ensure we report common flags even if not set
    for name in ('DB_USE_SSL', 'DB_SSL_CA_B64', 'DB_SSL_CA_PATH', 'DB_HOST', 'DB_USER', 'DB_NAME'):
        if name not in db_env:
            db_env[name] = {'present': False}

    return jsonify({'routes': routes, 'db_env': db_env}), 200


@app.route('/__version__', methods=['GET'])
def version():
    """Return the contents of DEPLOY_VERSION if present (helpful to know which commit is live)."""
    try:
        base = os.path.dirname(__file__)
        path = os.path.join(base, '..', 'DEPLOY_VERSION')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                v = f.read().strip()
            return jsonify({'version': v}), 200
    except Exception:
        pass
    return jsonify({'version': 'unknown'}), 200


#Iniciar el servicio web con Flask (solo para desarrollo local)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3006))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ('1', 'true')
    app.run(port=port, debug=debug, host='0.0.0.0')