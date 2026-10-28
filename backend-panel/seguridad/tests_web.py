import re
import time
from datetime import timedelta

from django.test import Client, override_settings
from django.utils import timezone

from core.models import UsuarioRol, Rol
from .models import DesafioWeb, LimiteWeb
from .tests import BaseRBAC, cuenta, miembro_con_rol
from .web.acceso import limitar, huella


@override_settings(SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
class AccesoWebTests(BaseRBAC):
    def setUp(self):
        self.browser = Client(enforce_csrf_checks=True)

    def formulario(self, browser=None):
        browser = browser or self.browser
        pagina = browser.get("/panel/login/")
        self.assertEqual(pagina.status_code, 200)
        desafio = pagina.context["desafio"]
        suma = sum(int(x.strip()) for x in desafio["suma"].split("+"))
        return {"email": self.admin.email, "password": "Clave-Sintetica-Para-Pruebas-6549",
            "captcha_token": desafio["token"], "captcha": suma,
            "csrfmiddlewaretoken": str(pagina.context["csrf_token"])}

    def entrar(self, usuario=None):
        d = self.formulario()
        d["email"] = (usuario or self.admin).email
        r = self.browser.post("/panel/login/", d)
        self.assertEqual(r.status_code, 302)
        return r

    def test_login_usa_suma_servidor_y_no_entrega_respuesta(self):
        d = self.formulario()
        fila = DesafioWeb.objects.get(pk=d["captcha_token"])
        self.assertNotEqual(fila.respuesta_hash, str(d["captcha"]))
        pagina = self.browser.get("/panel/login/").content.decode()
        self.assertNotRegex(pagina, r'(data-(answer|respuesta)|name="respuesta")')
        self.assertNotIn(fila.respuesta_hash, pagina)
        self.assertTrue(self.browser.cookies["csrftoken"]["httponly"])

    def test_login_csrf_obligatorio(self):
        d = self.formulario()
        del d["csrfmiddlewaretoken"]
        r = self.browser.post("/panel/login/", d)
        self.assertEqual(r.status_code, 403)
        self.assertNotIn("_auth_user_id", self.browser.session)

    def test_login_visual_conserva_formulario_servidor_sin_perfiles_ficticios(self):
        pagina = self.browser.get("/panel/login/")
        self.assertContains(pagina, 'class="clouds"')
        self.assertContains(pagina, 'acceso/fondo-movil.svg')
        self.assertContains(pagina, 'acceso/fondo-escritorio.svg')
        self.assertContains(pagina, 'name="csrfmiddlewaretoken"')
        self.assertContains(pagina, 'name="captcha_token"')
        self.assertNotContains(pagina, 'demo-profile')
        self.assertNotContains(pagina, 'fill-demo')
        self.assertNotContains(pagina, 'DemoLittlePaws')
        self.assertNotContains(pagina, 'autofocus')

    def test_login_correcto_rota_sesion_y_no_guarda_jwt(self):
        d = self.formulario()
        antes = self.browser.session.session_key
        r = self.browser.post("/panel/login/", d)
        self.assertEqual(r.url, "/panel/")
        self.assertNotEqual(antes, self.browser.session.session_key)
        self.assertEqual(int(self.browser.session["_auth_user_id"]), self.admin.pk)
        self.assertTrue(self.browser.cookies["sessionid"]["httponly"])
        self.assertEqual(self.browser.cookies["sessionid"]["samesite"], "Lax")
        self.assertNotIn("access_token", str(dict(self.browser.session)))

    def test_captcha_erroneo_y_reutilizado_no_autentica(self):
        d = self.formulario()
        respuesta = d["captcha"]
        d["captcha"] = 30
        self.assertEqual(self.browser.post("/panel/login/", d).status_code, 400)
        d["captcha"] = respuesta
        self.assertEqual(self.browser.post("/panel/login/", d).status_code, 400)
        self.assertNotIn("_auth_user_id", self.browser.session)

    def test_captcha_expirado_no_autentica(self):
        d = self.formulario()
        DesafioWeb.objects.filter(pk=d["captcha_token"]).update(expira=timezone.now()-timedelta(seconds=1))
        self.assertEqual(self.browser.post("/panel/login/", d).status_code, 400)

    def test_captcha_de_otra_sesion_no_autentica_ni_se_consume(self):
        robado = self.formulario()
        otra = Client(enforce_csrf_checks=True)
        propio = self.formulario(otra)
        robado["csrfmiddlewaretoken"] = propio["csrfmiddlewaretoken"]
        self.assertEqual(otra.post("/panel/login/", robado).status_code, 400)
        self.assertFalse(DesafioWeb.objects.get(pk=robado["captcha_token"]).consumido)

    def test_credenciales_invalidas_e_inactivas_responden_igual_sin_password(self):
        d = self.formulario()
        d["email"] = "inexistente@example.invalid"
        desconocido = self.browser.post("/panel/login/", d)
        self.admin.is_active = False
        self.admin.save(update_fields=["is_active"])
        d = self.formulario()
        inactivo = self.browser.post("/panel/login/", d)
        self.assertEqual(desconocido.context["error"], inactivo.context["error"])
        self.assertNotContains(inactivo, d["password"], status_code=400)

    def test_limite_login_comparte_cuenta_entre_sesiones(self):
        for _ in range(8):
            d = self.formulario()
            d["password"] = "Incorrecta-Sintetica"
            self.assertEqual(self.browser.post("/panel/login/", d).status_code, 400)
        otra = Client(enforce_csrf_checks=True)
        d = self.formulario(otra)
        r = otra.post("/panel/login/", d)
        self.assertEqual(r.status_code, 429)
        self.assertEqual(r["Retry-After"], "900")

    def test_limite_captcha_evitar_emision_sin_control(self):
        for _ in range(60):
            limitar("captcha-ip", "127.0.0.1", 60)
        self.assertEqual(self.browser.get("/panel/login/").status_code, 429)

    def test_login_no_acepta_redireccion_externa(self):
        d = self.formulario()
        d["next"] = "https://example.invalid/robar"
        self.assertEqual(self.browser.post("/panel/login/", d).url, "/panel/")

    def test_cerrar_sesion_exige_post_csrf_y_revoca_cookie(self):
        self.entrar()
        self.assertEqual(self.browser.get("/panel/logout/").status_code, 405)
        self.assertEqual(self.browser.post("/panel/logout/", {}).status_code, 403)
        pagina = self.browser.get("/panel/")
        self.assertEqual(self.browser.post("/panel/logout/", {"csrfmiddlewaretoken": str(pagina.context["csrf_token"])}).status_code, 302)
        self.assertNotIn("_auth_user_id", self.browser.session)
        self.assertEqual(self.browser.get("/panel/").status_code, 302)

    def test_ciudadano_y_superusuario_sin_rol_no_entran_al_panel(self):
        self.ciudadano.is_staff, self.ciudadano.is_superuser = True, True
        self.ciudadano.save()
        self.entrar(self.ciudadano)
        self.assertEqual(self.browser.get("/panel/").status_code, 403)
        self.assertEqual(self.browser.get("/panel/modulos/usuarios/").status_code, 403)

    def test_principal_ve_su_equipo_pero_no_seguridad_global(self):
        self.entrar(self.ana)
        pagina = self.browser.get("/panel/")
        self.assertContains(pagina, "Equipo y responsables")
        self.assertNotContains(pagina, 'href="/panel/modulos/usuarios/"')
        self.assertEqual(self.browser.get("/panel/modulos/usuarios/").status_code, 403)

    def test_cambio_entidad_rechaza_organizacion_ajena(self):
        self.entrar(self.ana)
        pagina = self.browser.get("/panel/")
        r = self.browser.post("/panel/organizacion/", {"entidad_id": self.ajena.pk,
            "csrfmiddlewaretoken": str(pagina.context["csrf_token"])})
        self.assertEqual(r.status_code, 403)
        self.assertNotEqual(self.browser.session.get("lpn_entidad"), self.ajena.pk)

    def test_cambiar_a_otra_entidad_propia_recalcula_permisos(self):
        miembro_con_rol(self.ana, self.ajena, "RESPONSABLE_SECUNDARIO")
        self.entrar(self.ana)
        pagina = self.browser.get("/panel/")
        r = self.browser.post("/panel/organizacion/", {"entidad_id": self.ajena.pk,
            "csrfmiddlewaretoken": str(pagina.context["csrf_token"])})
        self.assertEqual(r.status_code, 302)
        nueva = self.browser.get("/panel/")
        self.assertEqual(nueva.context["seleccion"]["id"], self.ajena.pk)
        self.assertEqual(self.browser.get("/panel/modulos/cuentas/").status_code, 403)

    def test_puente_de_rol_no_sustituye_la_designacion_del_principal(self):
        miembro_con_rol(self.ciudadano, self.entidad, "GESTOR_RESCATES")
        miembro_con_rol(self.ciudadano, self.entidad, "RESPONSABLE_PRINCIPAL")
        self.entrar(self.ciudadano)
        pagina = self.browser.get("/panel/")
        self.assertEqual(pagina.status_code, 200)
        self.assertNotContains(pagina, "Responsable principal")

    def test_revocar_rol_actualiza_navegacion_sin_otro_login(self):
        self.entrar()
        self.assertEqual(self.browser.get("/panel/modulos/usuarios/").status_code, 200)
        UsuarioRol.objects.filter(usuario=self.admin).update(fecha_revocacion=timezone.now())
        self.assertEqual(self.browser.get("/panel/modulos/usuarios/").status_code, 403)

    def test_sesion_vencida_no_se_extiende_al_consultar_la_api(self):
        self.entrar()
        sesion = self.browser.session
        sesion["lpn_web_inicio"] = time.time()-1801
        sesion.save()
        self.assertEqual(self.browser.get("/api/seguridad/usuarios/").status_code, 401)
        self.assertNotIn("_auth_user_id", self.browser.session)

    def test_sesion_api_exige_csrf_y_permite_operacion_con_token(self):
        self.entrar()
        self.assertEqual(self.browser.get("/api/seguridad/usuarios/").status_code, 200)
        datos = {"nombre": "Cuenta sintética web", "email": "nueva_web@example.invalid", "password": "Clave-Web-Sintetica-72869"}
        self.assertEqual(self.browser.post("/api/seguridad/usuarios/", datos, content_type="application/json").status_code, 403)
        pagina = self.browser.get("/panel/")
        r = self.browser.post("/api/seguridad/usuarios/", datos, content_type="application/json",
            HTTP_X_CSRFTOKEN=str(pagina.context["csrf_token"]))
        self.assertEqual(r.status_code, 201)
        self.assertNotIn("password", r.json())

    def test_cuenta_desactivada_pierde_sesion_y_datos(self):
        self.entrar()
        self.admin.is_active = False
        self.admin.save()
        self.assertEqual(self.browser.get("/panel/").status_code, 302)
        self.assertEqual(self.browser.get("/api/seguridad/usuarios/").status_code, 401)

    def test_nombre_html_se_escapa_y_panel_no_se_cachea(self):
        self.admin.nombre = "<script>alert(1)</script>"
        self.admin.save()
        self.entrar()
        r = self.browser.get("/panel/")
        self.assertNotContains(r, "<script>alert(1)</script>")
        self.assertContains(r, "&lt;script&gt;")
        self.assertIn("no-store", r["Cache-Control"])

    def test_panel_solo_lectura_no_ofrece_edicion_ni_asignacion(self):
        from core.models import Permiso, RolPermiso
        rol = Rol.objects.create(codigo="LECTOR_AUDITORIA", nombre="Consulta de seguridad", ambito="GLOBAL")
        for codigo in ("usuarios.ver", "roles.ver", "recursos.ver", "permisos.ver"):
            RolPermiso.objects.create(rol=rol, permiso=Permiso.objects.get(codigo=codigo))
        UsuarioRol.objects.create(usuario=self.ciudadano, rol=rol)
        self.entrar(self.ciudadano)
        for modulo in ("usuarios", "roles", "recursos", "permisos"):
            with self.subTest(modulo=modulo):
                pagina = self.browser.get(f"/panel/modulos/{modulo}/")
                self.assertEqual(pagina.status_code, 200)
                self.assertFalse(pagina.context["puede_crear"])
                self.assertFalse(pagina.context["puede_editar"])
                self.assertContains(pagina, 'data-editar="false"')
                self.assertContains(pagina, 'data-asignar-roles="false"')

    def test_panel_administrador_expone_solo_las_acciones_del_modulo(self):
        self.entrar()
        usuarios = self.browser.get("/panel/modulos/usuarios/")
        self.assertContains(usuarios, 'data-editar="true"')
        self.assertContains(usuarios, 'data-asignar-roles="true"')
        roles = self.browser.get("/panel/modulos/roles/")
        self.assertContains(roles, 'data-editar="true"')
        self.assertContains(roles, 'data-asignar-roles="false"')


from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace
from django.db import close_old_connections
from django.test import TransactionTestCase
from .web.acceso import consumir


class WebConcurrenciaTests(TransactionTestCase):
    def test_solo_una_peticion_consume_un_desafio(self):
        import uuid
        token = uuid.uuid4()
        DesafioWeb.objects.create(token=token, sesion_hash=huella("sesion-sintetica"),
            respuesta_hash=huella(f"{token}:7"), expira=timezone.now()+timedelta(minutes=5))
        barrera = Barrier(2)

        def intento(_):
            close_old_connections()
            barrera.wait(timeout=10)
            try:
                return consumir(SimpleNamespace(session=SimpleNamespace(session_key="sesion-sintetica")), str(token), "7")
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertCountEqual(list(pool.map(intento, [0, 1])), [True, False])

    def test_limite_por_ventana_no_se_pierde_entre_procesos(self):
        barrera = Barrier(2)

        def intento(_):
            close_old_connections()
            barrera.wait(timeout=10)
            try:
                return limitar("prueba", "cuenta-sintetica", 1)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertCountEqual(list(pool.map(intento, [0, 1])), [True, False])
