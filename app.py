"""
Top-level app entry that re-exports the Flask `app` from the package.
This helps hosts that expect `app:app` at project root.
"""
from campusgo_api.app import app

if __name__ == '__main__':
    # Local dev convenience
    app.run(host='0.0.0.0', port=3006)


# Diagnostic endpoint on the top-level app so we always have a simple verification
@app.route('/__i_am_live__', methods=['GET'])
def root_i_am_live():
    try:
        here = __import__('os').path.dirname(__file__)
        dv_path = __import__('os').path.join(here, 'DEPLOY_VERSION')
        dv = None
        if __import__('os').path.exists(dv_path):
            with open(dv_path, 'r', encoding='utf-8') as f:
                dv = f.read().strip()
    except Exception:
        dv = None
    return {'live': True, 'deploy_version': dv or 'unknown'}, 200
