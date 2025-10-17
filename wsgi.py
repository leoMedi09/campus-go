"""WSGI entrypoint that imports the Flask `app` from the package.
Use this as the explicit Gunicorn target: `gunicorn wsgi:app`.
"""
from campusgo_api.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3006)
