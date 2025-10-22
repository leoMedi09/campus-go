#!/usr/bin/env python3
"""Utility: convertir un archivo PEM (ca.pem) a base64 y escribirlo en db_ssl_ca_b64.txt
Usage:
  python scripts/replace_ca_from_pem.py --pem /path/to/ca.pem

Este script sobrescribe el archivo db_ssl_ca_b64.txt en el repo con el contenido base64 (sin saltos de línea extra).
"""
import argparse
import base64
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
OUT_PATH = os.path.join(ROOT, 'db_ssl_ca_b64.txt')

parser = argparse.ArgumentParser()
parser.add_argument('--pem', '-p', required=True, help='Ruta al archivo ca.pem descargado desde TiDB Cloud')
parser.add_argument('--out', '-o', default=OUT_PATH, help='Archivo de salida (base64)')
args = parser.parse_args()

if not os.path.exists(args.pem):
    print(f"ERROR: no existe el archivo PEM: {args.pem}")
    raise SystemExit(1)

with open(args.pem, 'rb') as f:
    pem_bytes = f.read()

# If the file contains PEM with headers, keep it as-is and base64-encode the whole PEM
b64 = base64.b64encode(pem_bytes).decode('ascii')

# Write to output
with open(args.out, 'w', encoding='utf-8') as out:
    out.write(b64)

print(f"Wrote base64 CA to: {args.out}")
print("Next steps:")
print(" - Restart your app so Config picks up the new CA (or set DB_SSL_CA_B64 env var to the base64 string).")
print(" - After restart test: GET /health-db and POST /login")
