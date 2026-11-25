"""Traffic arithmetic from measured payloads, without assuming provider prices."""
import argparse
import json
from pathlib import Path


def estimate(report, *, users, journeys_per_day, cold_web_mb, media_mb):
    if users < 1 or journeys_per_day < 1 or cold_web_mb < 0 or media_mb < 0:
        raise ValueError('Escenario de tráfico no válido')
    stages = report['stages']
    journeys = sum(s['journeys'] for s in stages)
    if journeys <= 0:
        raise ValueError('No hay recorridos medidos')
    per_journey = sum(s['sample']['bytes_total'] for s in stages) / journeys
    requests_per_journey = sum(s['sample']['requests'] for s in stages) / journeys
    month = users * journeys_per_day * 30
    api_bytes = per_journey * month
    web_bytes = users * cold_web_mb * 1_000_000
    media_bytes = month * media_mb * 1_000_000
    return {'active_users_assumption': users, 'journeys_per_user_per_day_assumption': journeys_per_day, 'days': 30, 'measured_response_bytes_per_journey': round(per_journey, 1), 'api_requests_per_month': round(month * requests_per_journey), 'api_response_gb': round(api_bytes / 1e9, 3), 'cold_web_gb_assumption': round(web_bytes / 1e9, 3), 'media_gb_assumption': round(media_bytes / 1e9, 3), 'total_response_gb_estimate': round((api_bytes + web_bytes + media_bytes) / 1e9, 3), 'currency_cost': None, 'limits': 'Decimal GB; one cold web download per user/month is assumed. Excludes uploads, headers/TLS, retransmissions, background services, backups, storage, CPU and provider minimum charges. Not a concurrency/capacity promise.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurement',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--cold-web-mb',type=float,default=0,help='Supuesto explícito de descarga fría por usuario/mes, no medición de este script')
    parser.add_argument('--media-mb',type=float,default=0,help='Supuesto de imágenes/media por recorrido, separado del JSON medido')
    args=parser.parse_args()
    report=json.loads(args.measurement.read_text(encoding='utf-8'))
    result={'provider_selected':False,'paid_services_authorized':False,'price_assumed':None,'scenarios':[estimate(report,users=u,journeys_per_day=j,cold_web_mb=args.cold_web_mb,media_mb=args.media_mb) for u,j in [(100,1),(500,3)]],'warning':'Use measured transferred bytes from the target deployment before budgeting money; compression/cache/provider quotas are not inferred.'}
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Escenarios de tráfico guardados, sin estimar precios ni prometer coste cero.')


if __name__=='__main__':main()
