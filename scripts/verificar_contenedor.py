"""Aceptación de la imagen local de CI; no migra ni conecta bases externas."""
import json
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        return None


def request(path, *, secure_proxy=False):
    headers = {'X-Forwarded-Proto': 'https'} if secure_proxy else {}
    req = Request('http://127.0.0.1:18000' + path, headers=headers)
    try:
        with build_opener(NoRedirect).open(req, timeout=3) as response:
            return response.status, response.headers, response.read()
    except HTTPError as error:
        return error.code, error.headers, error.read()


def main():
    deadline = time.monotonic() + 60
    while True:
        try:
            status, _headers, body = request('/api/health/')
            if status == 200 and json.loads(body) == {'status': 'ok'}:
                break
        except (OSError, URLError, ValueError):
            pass
        if time.monotonic() >= deadline:
            raise RuntimeError('El proceso no respondió correctamente en 60 segundos.')
        time.sleep(1)

    status, headers, _body = request('/panel/login/')
    if status != 301 or not headers.get('Location', '').startswith('https://127.0.0.1:18000/'):
        raise RuntimeError('El login HTTP debe redirigir a HTTPS antes de tocar la base.')
    status, headers, body = request('/static/seguridad/logo.svg', secure_proxy=True)
    if status != 200 or 'svg' not in headers.get('Content-Type', '') or b'<svg' not in body:
        raise RuntimeError('El logo estático recopilado no se sirve desde la imagen.')

    # Se comprueba el proceso 1, no el usuario de docker exec (administración del contenedor).
    code = (
        "import json,os,stat;from pathlib import Path;"
        "status=Path('/proc/1/status').read_text();"
        "uid=next(x.split()[1] for x in status.splitlines() if x.startswith('Uid:'));"
        "folder=Path(os.environ['LPN_PRIVATE_ROOT']);"
        "print(json.dumps({'uid':int(uid),'private_owner':folder.stat().st_uid,"
        "'private_mode':stat.S_IMODE(folder.stat().st_mode)}))"
    )
    result = subprocess.run(
        ['docker', 'exec', 'lpn-panel-ci', 'python', '-c', code],
        capture_output=True, text=True, check=True,
    )
    permissions = json.loads(result.stdout)
    if permissions != {'uid': 10001, 'private_owner': 10001, 'private_mode': 0o700}:
        raise RuntimeError('El proceso o el directorio privado tienen permisos inesperados.')
    print(json.dumps({
        'container_acceptance': 'passed', 'health_without_database': True,
        'login_requires_https': True, 'collected_static_available': True,
        'permissions': permissions, 'database_migrated': False,
        'image_pushed': False, 'external_hosting_created': False,
    }, indent=2))


if __name__ == '__main__':
    main()
