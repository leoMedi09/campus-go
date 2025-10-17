"""
Top-level app entry that re-exports the Flask `app` from the package.
This helps hosts that expect `app:app` at project root.
"""
from campusgo_api.app import app

if __name__ == '__main__':
    # Local dev convenience
    app.run(host='0.0.0.0', port=3006)
