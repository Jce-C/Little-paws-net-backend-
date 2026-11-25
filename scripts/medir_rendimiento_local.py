"""Small, repeatable HTTP sample restricted to the isolated local QA service."""
import concurrent.futures
import argparse
import json
import math
import statistics
import time
from pathlib import Path
from urllib.request import HTTPRedirectHandler, Request, build_opener

BASE = "http://127.0.0.1:8016"
OUT = Path("output/rendimiento-local.json")


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        raise ValueError("El ensayo QA no sigue redirecciones")


def get(path):
    if not path.startswith(("/api/adopcion/", "/api/reportes/publicos/", "/panel/login/")) or ".." in path:
        raise ValueError("Ruta fuera del ensayo público QA")
    request = Request(BASE + path, headers={"Accept": "application/json" if path.startswith("/api/") else "text/html"})
    start = time.perf_counter()
    with build_opener(NoRedirects).open(request, timeout=20) as response:
        headers = time.perf_counter()
        body = response.read(1024 * 1024 + 1)
        if len(body) > 1024 * 1024:
            raise ValueError("La muestra excede el presupuesto de 1 MiB")
        if response.status != 200:
            raise ValueError("Respuesta inesperada en QA")
        return {
            "headers_ms": (headers - start) * 1000,
            "total_ms": (time.perf_counter() - start) * 1000,
            "bytes": len(body),
            "content_type": response.headers.get_content_type(),
        }, body


def summarize(rows):
    values = sorted(row["total_ms"] for row in rows)
    return {
        "requests": len(rows),
        "median_ms": round(statistics.median(values), 2),
        "p95_ms": round(values[math.ceil(len(values) * .95) - 1], 2),
        "max_ms": round(max(values), 2),
        "median_headers_ms": round(statistics.median(row["headers_ms"] for row in rows), 2),
        "bytes": sorted({row["bytes"] for row in rows}),
    }


def measure_reports():
    first, body = get("/api/reportes/publicos/")
    data = json.loads(body)
    if not isinstance(data, dict) or set(data) != {"results", "next_cursor"}:
        raise ValueError("El servidor QA no implementa el contrato paginado")
    routes = {"primera_pagina": "/api/reportes/publicos/", "busqueda": "/api/reportes/publicos/?buscar=QA"}
    cursor = data["next_cursor"]
    if cursor is not None:
        if not isinstance(cursor, str) or not cursor.isascii() or not cursor.isdecimal():
            raise ValueError("Cursor inesperado del servidor QA")
        routes["segunda_pagina"] = f"/api/reportes/publicos/?antes={cursor}"
    report = {
        "local_qa_only": True, "debug": True,
        "scope": "Muestra HTTP local pequeña, sin TLS, WAN ni renderizado. No es un ensayo de carga ni una estimación de producción.",
        "sample_records_on_page": len(data["results"]),
        "first_sample": {k: round(v, 2) if isinstance(v, float) else v for k, v in first.items()},
        "request_budget": "Máximo 34 GET, dentro del presupuesto anónimo de 60/minuto si no hay otras lecturas simultáneas de la misma IP.",
        "business_submissions": 0, "routes": {},
    }
    for name, path in routes.items():
        get(path)
        sequential = [get(path)[0] for _ in range(6)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            concurrent_rows = list(pool.map(lambda _: get(path)[0], range(4)))
        report["routes"][name] = {
            "path": path, "sequential": summarize(sequential),
            "four_clients": summarize(concurrent_rows),
        }
    output = Path("output/rendimiento-local-reportes.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reportes", action="store_true", help="Muestra acotada de reportes paginados, sin consumir el presupuesto de acceso")
    args = parser.parse_args()
    if args.reportes:
        measure_reports()
        return
    catalog_row, catalog_body = get("/api/adopcion/catalogo/")
    catalog = json.loads(catalog_body)
    results = catalog["results"]
    if not results:
        raise ValueError("Se necesita una ficha sintética QA ya disponible; no se crean registros.")
    routes = {
        "catalogo": "/api/adopcion/catalogo/",
        "ficha": f'/api/adopcion/mascotas/{results[0]["id_mascota"]}/',
        "login_documento": "/panel/login/",
    }
    report = {
        "local_qa_only": True,
        "sample_records_on_page": len(results),
        "more_pages": catalog["next"] is not None,
        "debug": True,
        "scope": "HTTP local, sin TLS, latencia WAN ni renderizado; no es una prueba de producción ni certificación de carga.",
        "first_catalog_sample": {k: round(v, 2) if isinstance(v, float) else v for k, v in catalog_row.items()},
        "routes": {},
    }
    for name, path in routes.items():
        get(path)  # Warm-up excluded; cached code is distinct from cached HTTP.
        sequential = [get(path)[0] for _ in range(20)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            parallel_rows = list(pool.map(lambda _: get(path)[0], range(20)))
        report["routes"][name] = {
            "path": path, "sequential": summarize(sequential),
            "four_clients": summarize(parallel_rows),
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
