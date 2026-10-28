"""Reaplica identidad al export existente sin tocar los permisos ni sus fixtures."""
from pathlib import Path
import json, re, shutil
ROOT=Path(__file__).resolve().parents[2]
DEMO=ROOT/'demos/panel-editorial'
STATIC=ROOT/'backend-panel/seguridad/static/seguridad'
profiles=json.loads((Path(__file__).parent/'profiles.json').read_text(encoding='utf-8'))
shutil.copy2(Path(__file__).parent/'acceso.css',DEMO/'static/acceso/acceso.css')
shutil.copy2(Path(__file__).parent/'preview.css',DEMO/'preview.css')
def blend(a,b,t):
    return '#'+''.join(f'{round(int(a[i:i+2],16)*(1-t)+int(b[i:i+2],16)*t):02x}' for i in (1,3,5))
rules=['/* Generado desde frontend/panel-design/profiles.json. Solo presentación. */']
for p in profiles:
    a,s=p['accent'],p['soft']
    rules.append(f'[data-profile="{p["id"]}"]'+'{'+f'--lpn-primary:{a};--lpn-primary-hover:{blend(a,"#000000",.15)};--lpn-primary-active:{blend(a,"#000000",.25)};--lpn-sage-soft:{s};--lpn-sidebar:{blend(s,"#fffdf7",.45)};--lpn-table-head:{s};--lpn-table-ink:{a};--lpn-row-hover:{blend(s,"#fffdf7",.4)};'+'}')
(STATIC/'perfiles.css').write_text('\n'.join(rules),encoding='utf-8')
for name in ['icons.svg','LUCIDE-LICENSE.txt','identidad.js','relieve.css','perfiles.css']:
    shutil.copy2(STATIC/name,DEMO/'static/seguridad'/name)
for file in (DEMO/'perfiles').rglob('index.html'):
    code=file.relative_to(DEMO/'perfiles').parts[0]
    html=file.read_text(encoding='utf-8')
    html=html.replace('<span>little paws<span class="marca-sub">NET · PANEL DE GESTIÓN</span></span>','<span class="marca-copy"><span class="marca-nombre">Little Paws Net</span><span class="marca-sub">PANEL DE GESTIÓN</span></span>')
    html=html.replace('Little Paws · Vista de diseño','Little Paws Net · Vista de diseño')
    html=html.replace('/static/seguridad/relieve.css"','/static/seguridad/relieve.css?v=responsive-6"').replace('/preview.css"','/preview.css?v=responsive-6"')
    html=re.sub(r' data-profile="[^"]*"','',html)
    html=html.replace('<body ',f'<body data-profile="{code}" ',1)
    if 'relieve.css' not in html:
        html=html.replace('</head>','<link rel="stylesheet" href="/static/seguridad/perfiles.css"><link rel="stylesheet" href="/static/seguridad/relieve.css"><script src="/static/seguridad/identidad.js" defer></script></head>')
    html=re.sub(r'<meta name="csrf-token" content="[^"]*">','',html)
    html=html.replace('</head>','<meta name="csrf-token" content="demo-sin-sesion"></head>')
    html=re.sub(r'<input type="hidden" name="csrfmiddlewaretoken" value="[^"]*">','',html)
    mapa=dict(zip(['usuarios','roles','recursos','permisos','auditoria','verificaciones','reclamaciones','revision-publicidad','equipo','cuentas','rescates','adopciones','aportes','pedidos','catalogo','fondos','publicidad','expedientes'],['users','shield-check','boxes','key-round','history','clipboard-check','scale','megaphone','building-2','landmark','paw-print','heart-handshake','hand-coins','shopping-bag','package','chart-no-axes-combined','megaphone','stethoscope']))
    def icono(match):
        codigo=re.search(r'/modulos/([^/]+)/',match.group(1))
        nombre=mapa.get(codigo.group(1),'house') if codigo else 'house'
        return match.group(1)+match.group(2)+f'<svg class="lpn-icon" viewBox="0 0 24 24" aria-hidden="true"><use href="/static/seguridad/icons.svg#{nombre}"></use></svg>'+match.group(3)
    html=re.sub(r'(<a[^>]*href="[^"]*"[^>]*>(?:<div[^>]*>)?)(<span class="(?:nav-icono|modulo-icono)"[^>]*>)[^<]*(</span>)',icono,html)
    for marker,name in [('resumen-simbolo','boxes'),('resumen-simbolo arena','building-2'),('resumen-simbolo menta','shield-check')]:
        html=re.sub(r'<span class="'+marker+r'">[^<]*</span>',f'<span class="{marker}" aria-hidden="true"><svg class="lpn-icon" viewBox="0 0 24 24"><use href="/static/seguridad/icons.svg#{name}"></use></svg></span>',html)
    file.write_text(html,encoding='utf-8')
shutil.copy2(Path(__file__).parent/'profiles.json',DEMO/'static/acceso/profiles.json')
base=ROOT/'backend-panel/seguridad/templates/seguridad/web/base.html'
html=base.read_text(encoding='utf-8')
if 'relieve.css' not in html:
    html=html.replace('</head>',"<link rel=\"stylesheet\" href=\"{% static 'seguridad/relieve.css' %}\"><script src=\"{% static 'seguridad/identidad.js' %}\" defer></script></head>")
base.write_text(html,encoding='utf-8')
access=DEMO/'acceso';access.mkdir(exist_ok=True)
page=(Path(__file__).parent/'acceso.html').read_text(encoding='utf-8')
(access/'index.html').write_text(page,encoding='utf-8')
(DEMO/'index.html').write_text(page,encoding='utf-8')
js=DEMO/'static/acceso/acceso.js'
script=js.read_text(encoding='utf-8')
if 'PROFILE_DATA' in script: js.write_text(script.replace('PROFILE_DATA',json.dumps(profiles,ensure_ascii=False)),encoding='utf-8')
gallery='''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Estados de acceso · Little Paws Net</title><link rel="stylesheet" href="/static/seguridad/tokens.css"><link rel="stylesheet" href="/static/acceso/acceso.css"><script src="/static/acceso/acceso.js" defer></script></head><body><main class="state-gallery"><a class="gallery-back" href="/acceso/">← Volver a la bienvenida</a><p class="eyebrow">LITTLE PAWS NET · VISTA DE DISEÑO</p><h1>Un acceso que te acompaña</h1><p>Las ventanas del acceso, con la misma identidad de la bienvenida. Explora sus mensajes y vuelve al formulario cuando quieras.</p><section class="state-grid" aria-label="Estados de acceso"></section></main></body></html>'''
(DEMO/'estados/index.html').write_text(gallery,encoding='utf-8')
(DEMO/'acceso-pendiente/index.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=/acceso/?estado=pendiente#ingreso"><a href="/acceso/?estado=pendiente#ingreso">Ver acceso pendiente</a></html>',encoding='utf-8')
ignore=ROOT/'.gitignore'
s=ignore.read_text(encoding='utf-8')
if '**/node_modules/' not in s: ignore.write_text(s+'\n# Dependencias frontend locales\n**/node_modules/\n',encoding='utf-8')
print('Identidad aplicada a',len(list((DEMO/'perfiles').rglob('index.html'))),'vistas; 13 temas; iconos locales.')
