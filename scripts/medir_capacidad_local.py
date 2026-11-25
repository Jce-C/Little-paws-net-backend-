"""Bounded, opt-in workload against the isolated capacity fixture only."""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import statistics
import time
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE = 'http://127.0.0.1:8021'
MAX_BODY = 1024 * 1024
READS = ['/api/adopcion/catalogo/', '/api/catalogo/productos/', '/api/comunidad/publicaciones/', '/api/mascotas/mias/?pagina=1&limite=3']
WRITES = ['/api/comunidad/publicaciones/', '/api/pedidos/']


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        raise ValueError('El ensayo QA no sigue redirecciones')


def request(method, path, body=None, token=None):
    if path not in READS + WRITES + ['/__qa_capacity__/', '/api/auth/token/']:
        raise ValueError('Ruta fuera del ensayo QA')
    if method not in {'GET', 'POST'} or (method == 'POST' and path not in WRITES + ['/api/auth/token/']):
        raise ValueError('Método fuera del ensayo QA')
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    encoded = json.dumps(body).encode() if body is not None else None
    start = time.perf_counter()
    try:
        response = build_opener(NoRedirects).open(Request(BASE + path, data=encoded, headers=headers, method=method), timeout=15)
    except HTTPError as error:
        response = error
    with response:
        payload = response.read(MAX_BODY + 1)
        if len(payload) > MAX_BODY:
            raise ValueError('Respuesta QA mayor a 1 MiB')
        elapsed = (time.perf_counter() - start) * 1000
        parsed = json.loads(payload)
        return {'method': method, 'path': path, 'status': response.status, 'bytes': len(payload), 'ms': round(elapsed, 3)}, parsed


def summary(rows):
    values = sorted(r['ms'] for r in rows)
    if not values:
        raise ValueError('Muestra vacía')
    def percentile(q): return round(values[math.ceil(len(values) * q) - 1], 2)
    return {'requests': len(rows), 'p50_ms': round(statistics.median(values), 2), 'p95_ms': percentile(.95), 'p99_ms': percentile(.99), 'max_ms': round(values[-1], 2), 'bytes_total': sum(r['bytes'] for r in rows), 'statuses': dict(Counter(str(r['status']) for r in rows))}


def validate_fixture(credentials, marker):
    if not isinstance(credentials.get('nonce'), str) or len(credentials['nonce']) < 24:
        raise ValueError('Credenciales QA sin identificador de instancia')
    if marker.get('nonce') != credentials['nonce'] or marker.get('schema') != credentials.get('schema') or not marker.get('schema', '').startswith('lpn_capacity91_'):
        raise ValueError('El servidor no es la instancia QA esperada')
    if marker.get('debug') is not False or marker.get('fixture_only') is not True:
        raise ValueError('La instancia debe ser QA aislada y sin DEBUG')
    if len(credentials.get('actors', [])) != 8 or any(not isinstance(a.get('token'), str) or not a['token'] for a in credentials['actors']):
        raise ValueError('Se requieren ocho actores sintéticos')
    if any(type(credentials.get(k)) is not int or credentials[k] < 1 for k in ['store', 'product']):
        raise ValueError('Identificadores QA no válidos')


def run(credentials):
    status, marker = request('GET', '/__qa_capacity__/')
    if status['status'] != 200:
        raise ValueError('Instancia QA no disponible')
    validate_fixture(credentials, marker)
    # Successful authentication is sampled separately, not on every screen read.
    logins = []
    for _ in range(3):
        row, result = request('POST', '/api/auth/token/', {'email': credentials['email'], 'password': credentials['password']})
        if row['status'] != 200 or not result.get('access'):
            raise ValueError('La autenticación QA no superó la comprobación')
        logins.append(row)
    stages = []
    def actor(index):
        token = credentials['actors'][index]['token']
        rows = []
        for _ in range(4):
            for path in READS:
                row, _ = request('GET', path, token=token)
                rows.append(row)
            for path, body in [('/api/comunidad/publicaciones/', {'contenido': 'Historia sintética de capacidad QA.'}), ('/api/pedidos/', {'id_tienda': credentials['store'], 'lineas': [{'id_producto': credentials['product'], 'cantidad': 1}]})]:
                row, result = request('POST', path, body, token)
                if row['status'] == 201 and path == '/api/pedidos/' and result.get('cobrado') is not False:
                    raise ValueError('Un pedido QA no debe procesar pagos')
                rows.append(row)
        return rows
    # Exactly 52 short journeys / 312 business requests, bounded at 8 clients.
    for concurrency in [1, 4, 8]:
        _, before = request('GET', '/__qa_capacity__/')
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            rows = [r for result in pool.map(actor, range(concurrency)) for r in result]
        seconds = time.perf_counter() - start
        _, after = request('GET', '/__qa_capacity__/')
        groups = defaultdict(list)
        for row in rows:
            groups[row['method'] + ' ' + row['path']].append(row)
        errors = sum(row['status'] != (201 if row['method']=='POST' else 200) for row in rows)
        stages.append({'clients': concurrency, 'journeys': concurrency * 4, 'unexpected_status_count':errors,'duration_seconds': round(seconds, 3), 'requests_per_second': round(len(rows) / seconds, 2), 'sample': summary(rows), 'routes': {path: summary(values) for path, values in groups.items()}, 'server_before': {k: before[k] for k in ['working_set_bytes', 'private_bytes']}, 'server_after': {k: after[k] for k in ['working_set_bytes', 'private_bytes']}})
    # No secrets, tokens, nonce, cookies, request/response bodies in the report.
    return {'local_qa_only': True, 'debug': False, 'production_capacity_certified': False,'unexpected_status_count':sum(s['unexpected_status_count'] for s in stages), 'dataset': marker['dataset'], 'configuration': marker['configuration'], 'authentication': summary(logins), 'stages': stages, 'limits': 'Loopback, single ASGI process, bounded synthetic journeys. Excludes TLS, WAN, real devices and sustained load. Working set/private bytes are server process snapshots, not Android memory or sampled per-stage peaks.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--credentials', type=Path, required=True, help='Archivo privado de la instancia QA; nunca publicarlo')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = run(json.loads(args.credentials.read_text(encoding='utf-8')))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    if result['unexpected_status_count']:
        raise SystemExit('El ensayo contiene respuestas inesperadas; informe conservado, no se acepta como carga aprobada.')
    print('Informe local guardado; revisar errores, límites y muestras antes de sacar conclusiones.')


if __name__ == '__main__':
    main()
