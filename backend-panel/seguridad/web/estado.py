import hashlib
import json
from django.http import JsonResponse
from django.urls import reverse
from .contexto import construir
from seguridad.autorizacion import usuario_activo, motor
from seguridad.realtime import revision


def datos_estado(request,c=None):
    c=c or construir(request)
    datos={'modulos':[{**m,'url':m['url']} for m in c['modulos']],
        'perfil':c['perfil_visual'],'titulo':c['config_panel'].get('titulo_panel','Panel de gestión'),
        'permisos':[r['codigo'] for r in c['resumen_permisos']],
        'roles':c['globales'],'resumen':c['resumen_permisos'],'configuracion':c['config_panel'],
        'navegacion':{'textos':c['titulos_nav'],'grupos':[{'codigo':g['codigo'],'nombre':g['nombre'],'modulos':[{'codigo':m['codigo'],'nombre':m['nombre']} for m in g['modulos']]} for g in c['grupos_navegacion']]},
        'organizaciones':c['organizaciones'],'seleccion':c['entidad_id']}
    texto=json.dumps(datos,ensure_ascii=False,default=str,sort_keys=True)
    datos['firma']=hashlib.sha256(texto.encode()).hexdigest()
    datos['revision']=revision()
    expiraciones=[e['expira'] for e in motor(request.user).excepciones if e['expira']]
    datos['proxima_caducidad']=min(expiraciones).isoformat() if expiraciones else None
    from django.conf import settings
    datos['sesion_hasta']=(request.session.get('lpn_web_inicio',0)+settings.LPN_WEB_SESSION_SECONDS) if request.session.get('lpn_web_inicio') else None
    return datos


def estado(request):
    if not request.user.is_authenticated or not usuario_activo(request.user):
        return JsonResponse({'activo':False},status=401)
    response=JsonResponse({'activo':True,**datos_estado(request)})
    response['Cache-Control']='no-store'
    return response
