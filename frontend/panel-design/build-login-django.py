"""Conecta la presentación aprobada al formulario Django, sin lógica ficticia de autenticación."""
from pathlib import Path
import re, shutil

root=Path(__file__).resolve().parents[2]
source=Path(__file__).resolve().parent
target=root/'backend-panel/seguridad/static/acceso'
target.mkdir(parents=True,exist_ok=True)
assets=root/'demos/panel-editorial/static/acceso'
for name in ['logo.svg','fondo-escritorio.svg','fondo-movil.svg']+[f'nube-{i}.svg' for i in range(1,7)]:
    shutil.copy2(assets/name,target/name)
shutil.copy2(source/'acceso.css',target/'acceso.css')
for name in ('JetBrainsMono.ttf','JetBrainsMono-OFL.txt'):
    shutil.copy2(root/'demos/panel-editorial/static/seguridad/fonts'/name,root/'backend-panel/seguridad/static/seguridad/fonts'/name)

html=(source/'acceso.html').read_text(encoding='utf-8')
html=html.replace('<!doctype html>',"{% load static %}<!doctype html>",1)
html=html.replace('<title>Bienvenido · Little Paws Net</title>','<title>Iniciar sesión · Little Paws Net</title>')
html=html.replace('acceso.js?v=svg-7','entrada.js?v=django-1')
html=html.replace(' defer></script>'," data-assets=\"{% static 'acceso/' %}\" data-icons=\"{% static 'seguridad/icons.svg' %}\" defer></script>",1)
html=html.replace('<body>','<body data-form-active="{% if error or request.method == \'POST\' or request.GET.next %}true{% else %}false{% endif %}">',1)
html=html.replace('href="/" aria-label=', 'href="{% url \'panel:login\' %}" aria-label=',1)
html=html.replace('Vista de diseño','Acceso al equipo')
start=html.index('   <div class="demo-note">')
end=html.index('   <p class="access-help">',start)
form='''   {% if error %}<p id="form-feedback" class="feedback" role="alert">{{ error }}</p>{% endif %}
   <form id="login-form" method="post" action="{% url 'panel:login' %}" novalidate>{% csrf_token %}<input type="hidden" name="next" value="{{ next }}">{{ form.captcha_token }}
    <label for="id_email">Correo electrónico</label>{{ form.email }}
    <div class="label-row"><label for="id_password">Contraseña</label><button class="text-button" type="button" data-access-help>¿La olvidaste?</button></div>
    <div class="password-wrap">{{ form.password }}<button id="show-password" type="button" aria-label="Mostrar contraseña" aria-pressed="false"><svg aria-hidden="true" viewBox="0 0 24 24"><use href="/static/seguridad/icons.svg#eye"></use></svg></button></div>
    <div class="label-row"><label for="id_captcha">¿Cuánto es <b>{{ desafio.suma }}</b>?</label><a class="text-button" href="{% url 'panel:login' %}?next={{ next|urlencode }}#ingreso" aria-label="Obtener otra suma">Otra suma ↻</a></div>{{ form.captcha }}<small class="captcha-help">Completa la suma para continuar. Válida por 5 minutos.</small>
    <button class="primary" id="submit-login" type="submit">Iniciar sesión <span aria-hidden="true">↗</span></button>
   </form>
'''
html=html[:start]+form+html[end:]
html=re.sub(r'<nav aria-label="Navegación de la demostración">.*?</nav>','<span>Solo verás las funciones autorizadas para tu cuenta.</span>',html)
start=html.index('<dialog id="state-dialog"')
html=html[:start]+'''<dialog id="access-help" aria-labelledby="help-title" aria-describedby="help-copy"><button class="close" type="button" data-close-help aria-label="Cerrar ventana">×</button><p class="eyebrow">LITTLE PAWS NET · ACCESO</p><h2 id="help-title">Recupera tu acceso</h2><p id="help-copy">Contacta al responsable de tu organización para revisar tu cuenta. Esta página no envía correos de recuperación ni cambia contraseñas.</p><button class="primary" type="button" data-close-help>Volver al acceso</button></dialog>
<noscript><p class="no-js">Puedes desplazarte al formulario e iniciar sesión sin activar JavaScript. La animación es opcional.</p></noscript></body></html>
'''
def static_url(match):
    path=match[2].removeprefix('/static/')
    name,sep,query=path.partition('?')
    name,hash_sep,fragment=name.partition('#')
    return match[1]+'''="{% static '''+repr(name)+''' %}'''+(sep+query if sep else '')+(hash_sep+fragment if hash_sep else '')+'"'
html=re.sub(r'(src|href)="(/static/[^\"]+)"',static_url,html)
(root/'backend-panel/seguridad/templates/seguridad/web/login.html').write_text(html,encoding='utf-8')
motion=(assets/'acceso.js').read_text(encoding='utf-8').split('const clouds=',1)[1].split('const form=',1)[0]
motion='const clouds='+motion
motion=motion.replace('`/static/acceso/nube-${i+1}.svg`','`${assetBase}nube-${i+1}.svg`')
script='''"use strict";
const assetBase=document.currentScript.dataset.assets,iconBase=document.currentScript.dataset.icons;
'''+motion+'''
const password=document.querySelector('#id_password'),toggle=document.querySelector('#show-password');
toggle?.addEventListener('click',()=>{const visible=password.type==='password';password.type=visible?'text':'password';toggle.setAttribute('aria-pressed',String(visible));toggle.setAttribute('aria-label',visible?'Ocultar contraseña':'Mostrar contraseña');toggle.querySelector('use').setAttribute('href',iconBase+(visible?'#eye-off':'#eye'));});
const help=document.querySelector('#access-help');
document.querySelector('[data-access-help]')?.addEventListener('click',()=>help.showModal());
document.querySelectorAll('[data-close-help]').forEach(b=>b.addEventListener('click',()=>help.close()));
document.querySelector('#login-form')?.addEventListener('submit',()=>{const button=document.querySelector('#submit-login');button.disabled=true;button.textContent='Comprobando acceso…';});
addEventListener('pageshow',()=>{const button=document.querySelector('#submit-login');button.disabled=false;button.textContent='Iniciar sesión ↗';});
if(document.body.dataset.formActive==='true'){
 const show=()=>{document.querySelectorAll('.entry .reveal').forEach(el=>el.classList.add('is-visible'));document.querySelector('#ingreso').scrollIntoView({behavior:'instant'});};
 if(document.readyState==='complete')show();else addEventListener('load',show,{once:true});
}
'''
(target/'entrada.js').write_text(script,encoding='utf-8')
with (target/'acceso.css').open('a',encoding='utf-8') as f:
    f.write('\n.captcha-help{display:block;margin:8px 0 16px;color:#695541}.login-card .feedback{margin-bottom:20px}.label-row>a{font-size:13px}\n')
print('Login Django generado: presentación aprobada, formulario de servidor y recursos locales.')
