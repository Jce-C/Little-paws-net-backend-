"""Presentation groups built from effective modules, never role-name shortcuts."""
from django.utils.translation import gettext as _

ACCESS = ('roles', 'recursos', 'permisos', 'roles-usuario', 'excepciones')

def organizar(modulos,config=None):
    from .titulos_navegacion import GRUPOS, titulo
    config=config or {}
    cards=[]
    for m in modulos:
        if m['codigo'] in ACCESS and m['codigo']!='excepciones':
            cards.append({**m,'tab':{'roles-usuario':'usuarios'}.get(m['codigo'],m['codigo'])})
    cards.sort(key=lambda c:ACCESS.index(c['codigo']))
    groups=[];lookup={};security=[]
    for code in ('usuarios','accesos','auditoria'):
        if code=='accesos':
            if cards:security.append({'codigo':'accesos','nombre':titulo(config,'nav_accesos','Roles y recursos'),'icono':'shield-check','url':cards[0]['url'],'hijos':len(cards),'activos':ACCESS})
        else:
            m=next((m for m in modulos if m['codigo']==code),None)
            if m:security.append({**m,'activos':(code,)})
    if security:groups.append({'codigo':'seguridad','nombre':titulo(config,'nav_grupo_seguridad','Seguridad'),'icono':'shield-check','modulos':security})
    org=next((m for m in modulos if m['codigo']=='organizaciones'),next((m for m in modulos if m['codigo'] in ('equipo','cuentas')),None))
    for m in modulos:
        if m['codigo'] in ('organizaciones','equipo','cuentas'):
            if m is not org:continue
            m={**m,'codigo':'organizaciones','activos':('organizaciones','equipo','cuentas')}
        if m['codigo'] in ACCESS+('usuarios','auditoria','configuracion'):continue
        key=m.get('grupo_codigo') or m['grupo']
        if key not in lookup:
            group={'codigo':'grupo-'+str(key),'nombre':titulo(config,'nav_grupo_'+str(key),GRUPOS.get(key,m['grupo'])),'icono':m['icono'],'modulos':[]};lookup[key]=group;groups.append(group)
        lookup[key]['modulos'].append({**m,'activos':m.get('activos',(m['codigo'],))})
    for group in groups:group['cantidad']=len(group['modulos'])
    return {'grupos_navegacion':groups,'cantidad_modulos':sum(g['cantidad'] for g in groups),'tarjetas_seguridad':cards}
