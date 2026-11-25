"""Isolated Windows/MySQL capacity fixture; not a deployment entry point.

Requires an explicitly configured local test instance via LPN_TEST_MYSQL_*.
Never imports a database URL, never drops schemas, and binds only loopback.
"""
from pathlib import Path
import os,sys,json,secrets,uuid,gc,ctypes,io
from ctypes import wintypes
if os.name != 'nt':
    raise SystemExit('Este perfil de memoria usa Windows; validar el host Linux por separado.')
root=Path(__file__).resolve().parents[1]
cfg={'port':int(os.environ['LPN_TEST_MYSQL_PORT'])}
if os.environ['LPN_TEST_MYSQL_HOST']!='127.0.0.1' or cfg['port']==3306:
    raise SystemExit('Se requiere MySQL de pruebas en loopback y puerto separado.')
schema='lpn_capacity91_'+uuid.uuid4().hex[:8]
import MySQLdb
conn=MySQLdb.connect(host='127.0.0.1',port=cfg['port'],user=os.environ['LPN_TEST_MYSQL_USER'],passwd=os.environ['LPN_TEST_MYSQL_PASSWORD'])
with conn.cursor() as c: c.execute('CREATE DATABASE `'+schema+'` CHARACTER SET utf8mb4')
conn.close()
os.environ['DJANGO_SETTINGS_MODULE']='config.settings_test_mysql'
os.environ.setdefault('DJANGO_SECRET_KEY','isolated-capacity-only')
sys.path.insert(0,str(root/'backend-panel'))
private=root/'.private-data/capacity';private.mkdir(parents=True,exist_ok=True)
from cryptography.fernet import Fernet
os.environ['LPN_DATA_KEY']=Fernet.generate_key().decode()
import django;django.setup()
from django.conf import settings
settings.DATABASES['default']['NAME']=schema
settings.DEBUG=False
settings.PASSWORD_HASHERS=['django.contrib.auth.hashers.PBKDF2PasswordHasher']
settings.SESSION_COOKIE_SECURE=False;settings.CSRF_COOKIE_SECURE=False
from django.core.management import call_command
call_command('migrate',interactive=False,stdout=io.StringIO())
from seguridad.tests import catalogos,valor
catalogos()
from importlib import import_module
from django.apps import apps
from django.db import connection
import_module('seguridad.migrations.0020_comunidad_y_ayudas').cargar(apps,connection.schema_editor())
from accounts.models import Usuario
from core.models import UsuarioRol,Rol,Ciudad,EntidadVerificable,Fundacion,Tienda
from animals.models import Mascota,CustodiaMascota
from commerce.models import Producto
from django.utils import timezone
password=secrets.token_urlsafe(28)
user=Usuario.objects.create(email='capacity-login@example.invalid',nombre='Persona QA capacidad',debe_cambiar_clave=False)
user.set_password(password);user.save()
UsuarioRol.objects.create(usuario=user,rol=Rol.objects.get(codigo='CIUDADANO'))
city=Ciudad.objects.create(nombre='Ciudad QA capacidad',departamento='Departamento sintético')
entity=EntidadVerificable.objects.create(nombre='Organización QA capacidad',estado_verificacion=valor('estado_verificacion','Verificada'))
foundation=Fundacion.objects.create(entidad=entity,ciudad=city,nit='QA-CAPACITY-ONLY')
pet=Mascota.objects.create(nombre='Animal inicial QA',descripcion_especie='Perro',estado_mascota=valor('estado_mascota','En adopción'))
CustodiaMascota.objects.create(mascota=pet,fundacion=foundation,usuario_registrador=user,fecha_inicio=timezone.now())
store=Tienda.objects.create(entidad=entity,ciudad=city,direccion='Dirección sintética QA')
product=Producto.objects.create(tienda=store,nombre='Producto inicial QA',precio='25000.00',existencias=10,categoria_producto=valor('categoria_producto','Alimentos'),tipo_producto=valor('tipo_producto','Alimento seco'),estado_producto=valor('estado_producto','Disponible'))
(private/'credentials.json').write_text(json.dumps({'schema':schema,'email':user.email,'password':password,'product':product.pk,'store':store.pk}),encoding='utf-8')

assert settings.DATABASES['default']['HOST']=='127.0.0.1' and settings.DATABASES['default']['NAME']==schema and cfg['port']!=3306
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import PublicacionComunidad
from django.utils import timezone
PublicacionComunidad.objects.create(autor=user,contenido='Historia inicial QA capacidad')
probe=APIClient();probe.force_authenticate(user)
def queries():
    rows=[]
    for path in ['/api/adopcion/catalogo/','/api/catalogo/productos/','/api/comunidad/publicaciones/','/api/mascotas/mias/?pagina=1&limite=3']:
        probe.get(path)
        with CaptureQueriesContext(connection) as captured:
            response=probe.get(path)
            if hasattr(response,'render'):response.render()
            assert response.status_code==200,(path,response.status_code)
            rows.append({'path':path,'sql_queries':len(captured),'bytes':len(response.content)})
    return rows
baseline=queries()
extra=Mascota.objects.bulk_create([Mascota(nombre=f'Animal QA capacidad {i}',descripcion_especie='Perro',estado_mascota=pet.estado_mascota) for i in range(999)])
extra=list(Mascota.objects.filter(nombre__startswith='Animal QA capacidad ').order_by('pk'))
CustodiaMascota.objects.bulk_create([CustodiaMascota(mascota=p,fundacion=foundation,usuario_registrador=user,fecha_inicio=timezone.now()) for p in extra])
Producto.objects.bulk_create([Producto(tienda=store,nombre=f'Producto QA capacidad {i}',precio='25000.00',existencias=10,categoria_producto=product.categoria_producto,tipo_producto=product.tipo_producto,estado_producto=product.estado_producto,descripcion='Descripción sintética de la prueba de capacidad.') for i in range(499)])
PublicacionComunidad.objects.bulk_create([PublicacionComunidad(autor=user,contenido=f'Historia sintética QA capacidad {i}') for i in range(249)])
actors=[]
for i in range(8):
    actor=Usuario.objects.create(email=f'capacity{i}@example.invalid',nombre=f'Actor QA {i}',debe_cambiar_clave=False)
    actor.set_unusable_password();actor.save()
    UsuarioRol.objects.create(usuario=actor,rol=Rol.objects.get(codigo='CIUDADANO'))
    Mascota.objects.bulk_create([Mascota(nombre=f'Mascota propia QA {i}-{j}',dueno=actor,descripcion_especie='Perro',estado_mascota=valor('estado_mascota','Con dueño')) for j in range(10)])
    actors.append({'token':str(RefreshToken.for_user(actor).access_token)})
probe.force_authenticate(Usuario.objects.get(email='capacity0@example.invalid'))
scaled=queries()
out=Path(os.environ.get('LPN_CAPACITY_REPORT_DIR',str(root/'output/capacidad-local')));out.mkdir(parents=True,exist_ok=True)
(out/'sql-escalado.json').write_text(json.dumps({'fixture_only':True,'baseline':baseline,'scaled':scaled,'sizes':{'available_pets':1000,'products':500,'community_posts':250,'actors':8,'owned_pets':80},'instrumentation':'Django test client with CaptureQueriesContext; excludes network. No SQL texts or secrets.'},indent=2),encoding='utf-8')
nonce=secrets.token_urlsafe(32)
creds=json.loads((private/'credentials.json').read_text());creds.update(nonce=nonce,schema=schema,actors=actors)
(private/'credentials.json').write_text(json.dumps(creds),encoding='utf-8')
class Counters(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage']]
kernel=ctypes.WinDLL('kernel32',use_last_error=True);psapi=ctypes.WinDLL('psapi',use_last_error=True)
kernel.GetCurrentProcess.restype=wintypes.HANDLE
psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD];psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
def marker():
    mem=Counters();mem.cb=ctypes.sizeof(mem)
    assert psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(mem),mem.cb)
    return {'nonce':nonce,'schema':schema,'debug':settings.DEBUG,'fixture_only':True,'working_set_bytes':mem.WorkingSetSize,'private_bytes':mem.PrivateUsage,'dataset':{'available_pets':1000,'products':500,'community_posts_at_start':250,'actors':8,'owned_pets':80},'configuration':{'server':'single-process Uvicorn/ASGI','database':'MySQL isolated loopback','password_hasher':user.password.split('$')[0],'password_login_samples':3,'connection_max_age':settings.DATABASES['default'].get('CONN_MAX_AGE',0)}}
from config.asgi import application as django_app
async def app(scope,receive,send):
    if scope['type']=='http' and scope['path']=='/__qa_capacity__/':
        body=json.dumps(marker()).encode()
        await send({'type':'http.response.start','status':200,'headers':[(b'content-type',b'application/json')]})
        await send({'type':'http.response.body','body':body});return
    await django_app(scope,receive,send)
gc.collect()
print('Fixture aislada preparada: 1000 mascotas, 500 productos, ocho actores; ASGI en 127.0.0.1:8021.',flush=True)
import uvicorn
uvicorn.run(app,host='127.0.0.1',port=8021,log_level='warning')
