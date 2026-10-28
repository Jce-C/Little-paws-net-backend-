from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from importlib import import_module
from threading import Barrier
from unittest.mock import patch
from io import StringIO
import os

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import close_old_connections, connection
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Usuario
from adoption.models import SolicitudAdopcion
from adoption.services import resolver_solicitud
from animals.models import CustodiaMascota, Especie, Mascota, Raza
from core.models import Ciudad, EntidadMiembro, EntidadMiembroRol, EntidadVerificable, Fundacion, Permiso, Recurso, Rol, TipoMaestro, UsuarioRol, ValorMaestro
from funds.models import FondoExterno
from .autorizacion import puede, principal_de
from .models import AsignacionFondo, AsignacionRecurso, EventoSeguridad, ResponsableEntidad, TransferenciaResponsabilidad
from .servicios import (
    asignar_entidad, asignar_fondo, asignar_global, devolver, designar_principal,
    gestionar_miembro, guardar_estado_usuario, iniciar_transferencia, resolver_transferencia, tomar,
)


def catalogos():
    # También permite reconstruir datos de referencia tras flush en TransactionTestCase.
    import_module("core.migrations.0004_seed_catalogs_mvp").crear_catalogos(apps, connection.schema_editor())
    import_module("core.migrations.0006_seed_catalogs_remaining").crear_catalogos(apps, connection.schema_editor())
    import_module("seguridad.migrations.0002_catalogo_seguridad").cargar(apps, connection.schema_editor())
    import_module("seguridad.migrations.0005_estados_flujos").cargar(apps, connection.schema_editor())
    import_module("seguridad.migrations.0006_catalogo_flujos").cargar(apps, connection.schema_editor())


def valor(tipo, nombre):
    return ValorMaestro.objects.get(tipo__nombre=tipo, nombre=nombre)


def cuenta(nombre):
    return Usuario.objects.create_user(email=f"{nombre}@example.invalid", nombre=nombre,
                                       password="Clave-Sintetica-Para-Pruebas-6549")


def entidad(nombre):
    return EntidadVerificable.objects.create(nombre=nombre, estado_verificacion=valor("estado_verificacion", "Verificada"))


def miembro_con_rol(usuario, organizacion, codigo):
    miembro, _ = EntidadMiembro.objects.get_or_create(usuario=usuario, entidad=organizacion)
    EntidadMiembroRol.objects.get_or_create(miembro=miembro, rol=Rol.objects.get(codigo=codigo))
    return miembro


class BaseRBAC(TestCase):
    @classmethod
    def setUpTestData(cls):
        catalogos()
        cls.admin = cuenta("seguridad")
        UsuarioRol.objects.create(usuario=cls.admin, rol=Rol.objects.get(codigo="ADMIN_SEGURIDAD"))
        cls.ciudadano = cuenta("ciudadano")
        cls.ana = cuenta("ana")
        cls.carlos = cuenta("carlos")
        cls.otro = cuenta("otro")
        cls.entidad = entidad("Fundación pruebas A")
        cls.ajena = entidad("Fundación pruebas B")
        cls.ana_m = EntidadMiembro.objects.create(usuario=cls.ana, entidad=cls.entidad)
        cls.carlos_m = miembro_con_rol(cls.carlos, cls.entidad, "RESPONSABLE_SECUNDARIO")
        cls.otro_m = miembro_con_rol(cls.otro, cls.ajena, "GESTOR_RESCATES")
        ResponsableEntidad.objects.create(entidad=cls.entidad, principal=cls.ana_m)

    def cliente(self, usuario):
        c = APIClient()
        c.force_authenticate(usuario)
        return c


class MotorAccesoTests(BaseRBAC):
    def test_ciudadano_no_administra_seguridad(self):
        self.assertFalse(puede(self.ciudadano, "usuarios.ver"))
        self.assertTrue(puede(self.admin, "usuarios.ver"))

    def test_superusuario_tecnico_no_es_administrador_de_negocio(self):
        self.ciudadano.is_superuser = self.ciudadano.is_staff = True
        self.ciudadano.save()
        self.assertFalse(puede(self.ciudadano, "usuarios.ver"))
        self.assertEqual(self.cliente(self.ciudadano).get("/api/seguridad/usuarios/").status_code, 403)

    def test_revocacion_global_tiene_efecto_inmediato(self):
        UsuarioRol.objects.filter(usuario=self.admin).update(fecha_revocacion=timezone.now())
        self.assertFalse(puede(self.admin, "usuarios.ver"))

    def test_cuenta_inactiva_no_conserva_acceso_por_objeto_en_memoria(self):
        Usuario.objects.filter(pk=self.admin.pk).update(is_active=False)
        self.assertTrue(self.admin.is_active)  # Objeto antiguo deliberadamente obsoleto.
        self.assertFalse(puede(self.admin, "usuarios.ver"))

    def test_rol_de_entidad_no_atraviesa_entidades(self):
        self.assertTrue(puede(self.otro, "caso.ver", entidad_id=self.ajena.pk))
        self.assertFalse(puede(self.otro, "caso.ver", entidad_id=self.entidad.pk))
        self.assertFalse(puede(self.otro, "caso.ver"))

    def test_revocacion_de_rol_o_membresia_retira_acceso(self):
        asignacion = EntidadMiembroRol.objects.get(miembro=self.otro_m)
        asignacion.fecha_revocacion = timezone.now()
        asignacion.save()
        self.assertFalse(puede(self.otro, "caso.ver", entidad_id=self.ajena.pk))
        asignacion.fecha_revocacion = None
        asignacion.save()
        self.otro_m.fecha_salida = timezone.now()
        self.otro_m.save()
        self.assertFalse(puede(self.otro, "caso.ver", entidad_id=self.ajena.pk))

    def test_principal_no_hereda_operaciones_clinicas_ni_financieras(self):
        self.assertTrue(puede(self.ana, "miembros.roles", entidad_id=self.entidad.pk))
        for codigo in ("caso.aceptar", "adopcion.resolver", "aporte.confirmar", "expediente.escribir"):
            self.assertFalse(puede(self.ana, codigo, entidad_id=self.entidad.pk))

    def test_rol_antiguo_amplio_no_se_reactiva_ni_concede(self):
        rol = Rol.objects.get(codigo="GESTOR_FUNDACION")
        self.assertFalse(rol.activo)
        EntidadMiembroRol.objects.create(miembro=self.ana_m, rol=rol)
        self.assertFalse(puede(self.ana, "caso.aceptar", entidad_id=self.entidad.pk))

    def test_recurso_desactivado_anula_permiso(self):
        Recurso.objects.filter(codigo="caso").update(activo=False)
        self.assertFalse(puede(self.otro, "caso.ver", entidad_id=self.ajena.pk))

    def test_no_existe_permiso_por_conocer_o_inventar_codigo(self):
        recurso = Recurso.objects.create(codigo="inventado", nombre="Inventado")
        permiso = Permiso.objects.create(codigo="inventado.ver", descripcion="No implementado", recurso=recurso, accion="ver", alcance="GLOBAL")
        from core.models import RolPermiso
        RolPermiso.objects.create(rol=Rol.objects.get(codigo="ADMIN_SEGURIDAD"), permiso=permiso)
        self.assertFalse(puede(self.admin, "inventado.ver"))


class APIAdministracionTests(BaseRBAC):
    def test_api_exige_autenticacion_y_no_solo_login(self):
        self.assertEqual(APIClient().get("/api/seguridad/roles/").status_code, 401)
        self.assertEqual(self.cliente(self.ciudadano).get("/api/seguridad/roles/").status_code, 403)
        r = self.cliente(self.admin).get("/api/seguridad/roles/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("results", r.data)

    def test_crear_usuario_guarda_hash_sin_exponer_password_o_flags(self):
        r = self.cliente(self.admin).post("/api/seguridad/usuarios/", {
            "nombre": "Nuevo", "email": "nuevo@example.invalid",
            "password": "Otra-Clave-Exclusiva-Pruebas-7529"}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        self.assertNotIn("password", r.data)
        usuario = Usuario.objects.get(email="nuevo@example.invalid")
        self.assertTrue(usuario.check_password("Otra-Clave-Exclusiva-Pruebas-7529"))
        self.assertFalse(usuario.is_staff or usuario.is_superuser)
        evento = EventoSeguridad.objects.latest("pk")
        self.assertEqual(evento.datos, {})

    def test_rechaza_escalamiento_por_campos_no_permitidos(self):
        r = self.cliente(self.admin).post("/api/seguridad/usuarios/", {
            "nombre": "No", "email": "no@example.invalid", "password": "Otra-Clave-Exclusiva-Pruebas-7529",
            "is_superuser": True}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(Usuario.objects.filter(email="no@example.invalid").exists())

    def test_alta_publica_activa_solo_ciudadano(self):
        r = APIClient().post("/api/auth/registro/", {"nombre": "Registro", "email": "registro@example.invalid",
            "password": "Otra-Clave-Exclusiva-Pruebas-7529"}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        u = Usuario.objects.get(email="registro@example.invalid")
        self.assertTrue(u.is_active)
        self.assertEqual(list(UsuarioRol.objects.filter(usuario=u).values_list("rol__codigo", flat=True)), ["CIUDADANO"])

    def test_no_se_puede_desactivar_el_ultimo_admin(self):
        r = self.cliente(self.admin).patch(f"/api/seguridad/usuarios/{self.admin.pk}/", {"is_active": False}, format="json")
        self.assertEqual(r.status_code, 400)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_con_otro_admin_la_baja_si_es_posible_y_el_jwt_no_sigue(self):
        otro_admin = cuenta("seguridad2")
        UsuarioRol.objects.create(usuario=otro_admin, rol=Rol.objects.get(codigo="ADMIN_SEGURIDAD"))
        token = str(RefreshToken.for_user(self.admin).access_token)
        r = self.cliente(otro_admin).patch(f"/api/seguridad/usuarios/{self.admin.pk}/", {"is_active": False}, format="json")
        self.assertEqual(r.status_code, 200)
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(c.get("/api/seguridad/roles/").status_code, 401)

    def test_no_se_puede_revocar_ultimo_admin(self):
        with self.assertRaises(ValidationError):
            asignar_global(self.admin, self.admin.pk, Rol.objects.get(codigo="ADMIN_SEGURIDAD").pk, revocar=True)

    def test_matriz_del_sistema_no_mezcla_seguridad_con_moderacion(self):
        rol = Rol.objects.get(codigo="MODERADOR")
        p = Permiso.objects.get(codigo="usuarios.editar")
        r = self.cliente(self.admin).post(f"/api/seguridad/roles/{rol.pk}/permisos/", {"permisos": [p.pk]}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(puede(self.ciudadano, "usuarios.editar"))

    def test_no_desactivar_control_esencial(self):
        p = Permiso.objects.get(codigo="roles.editar")
        r = self.cliente(self.admin).patch(f"/api/seguridad/permisos/{p.pk}/", {"activo": False}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_catalogo_custom_no_implementa_operaciones_y_no_se_borra(self):
        c = self.cliente(self.admin)
        r = c.post("/api/seguridad/recursos/", {"codigo": "nuevo", "nombre": "Nuevo"}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(c.delete(f"/api/seguridad/recursos/{r.data['id']}/").status_code, 405)
        self.assertEqual(c.post("/api/seguridad/permisos/", {"codigo": "nuevo.ver", "descripcion": "No soportado"}, format="json").status_code, 400)

    def test_mis_accesos_separa_global_y_entidad_sin_secretos(self):
        r = self.cliente(self.ana).get("/api/seguridad/mis-accesos/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["roles_globales"], [])
        self.assertIn("RESPONSABLE_PRINCIPAL", r.data["entidades"][0]["roles"])
        self.assertNotIn("password", str(r.data))

    def test_token_vigente_no_congela_roles_antiguos(self):
        token = str(RefreshToken.for_user(self.admin).access_token)
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(c.get("/api/seguridad/usuarios/").status_code, 200)
        UsuarioRol.objects.filter(usuario=self.admin).update(fecha_revocacion=timezone.now())
        self.assertEqual(c.get("/api/seguridad/usuarios/").status_code, 403)

    def test_crear_y_configurar_rol_personalizado_de_entidad(self):
        c = self.cliente(self.admin)
        r = c.post("/api/seguridad/roles/", {"codigo": "CONSULTA_CASOS", "nombre": "Consulta de casos",
            "ambito": "ENTIDAD", "delegable": True}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        p = Permiso.objects.get(codigo="caso.ver")
        r2 = c.post(f"/api/seguridad/roles/{r.data['id_rol']}/permisos/", {"permisos": [p.pk]}, format="json")
        self.assertEqual(r2.status_code, 200, r2.data)

    def test_bootstrap_no_agrega_admin_si_ya_existe(self):
        with self.assertRaises(CommandError):
            call_command("iniciar_seguridad", email="alguien@example.invalid")

    def test_rol_de_entidad_no_recibe_permiso_global_por_la_matriz(self):
        c = self.cliente(self.admin)
        r = c.post("/api/seguridad/roles/", {"codigo": "EQUIPO_TEST", "nombre": "Equipo",
            "ambito": "ENTIDAD", "delegable": True}, format="json")
        self.assertEqual(r.status_code, 201)
        p = Permiso.objects.get(codigo="usuarios.editar")
        self.assertEqual(c.post(f"/api/seguridad/roles/{r.data['id_rol']}/permisos/",
            {"permisos": [p.pk]}, format="json").status_code, 400)

    def test_rol_historico_no_se_reactiva_desde_la_api(self):
        rol = Rol.objects.get(codigo="GESTOR_FUNDACION")
        r = self.cliente(self.admin).patch(f"/api/seguridad/roles/{rol.pk}/", {"activo": True}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_no_cambiar_alcance_de_permiso_desde_cliente(self):
        p = Permiso.objects.get(codigo="adopcion.resolver")
        r = self.cliente(self.admin).patch(f"/api/seguridad/permisos/{p.pk}/", {"alcance": "GLOBAL"}, format="json")
        self.assertEqual(r.status_code, 400)
        p.refresh_from_db()
        self.assertEqual(p.alcance, "ASIGNADO")

    def test_no_desactivar_recurso_esencial(self):
        recurso = Recurso.objects.get(codigo="roles")
        r = self.cliente(self.admin).patch(f"/api/seguridad/recursos/{recurso.pk}/", {"activo": False}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_no_retirar_permiso_de_transferencia_del_rol_principal(self):
        rol = Rol.objects.get(codigo="RESPONSABLE_PRINCIPAL")
        r = self.cliente(self.admin).post(f"/api/seguridad/roles/{rol.pk}/permisos/", {"permisos": []}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_comprobacion_solo_sobre_usuario_actual(self):
        c = self.cliente(self.ciudadano)
        self.assertEqual(c.post("/api/seguridad/comprobar/", {"permiso": "usuarios.ver"}, format="json").data, {"permitido": False})
        self.assertEqual(c.post("/api/seguridad/comprobar/", {"permiso": "usuarios.ver", "usuario_id": self.admin.pk}, format="json").status_code, 400)

    def test_catalogo_migrado_no_reactiva_usuarios(self):
        self.ciudadano.is_active = False
        self.ciudadano.save()
        import_module("seguridad.migrations.0002_catalogo_seguridad").cargar(apps, connection.schema_editor())
        self.ciudadano.refresh_from_db()
        self.assertFalse(self.ciudadano.is_active)


class ResponsablesTests(BaseRBAC):
    def test_secundario_delega_pero_no_roles_globales(self):
        miembro = gestionar_miembro(self.carlos, self.entidad.pk, self.ciudadano.pk)
        asignar_entidad(self.carlos, self.entidad.pk, miembro.pk, Rol.objects.get(codigo="GESTOR_RESCATES").pk)
        self.assertTrue(puede(self.ciudadano, "caso.aceptar", entidad_id=self.entidad.pk))
        with self.assertRaises(Rol.DoesNotExist):
            asignar_entidad(self.carlos, self.entidad.pk, miembro.pk, Rol.objects.get(codigo="ADMIN_SEGURIDAD").pk)

    def test_secundario_no_puede_otorgar_principal_ordinario(self):
        with self.assertRaises(Rol.DoesNotExist):
            asignar_entidad(self.carlos, self.entidad.pk, self.carlos_m.pk, Rol.objects.get(codigo="RESPONSABLE_PRINCIPAL").pk)
        self.assertFalse(principal_de(self.carlos, self.entidad.pk))

    def test_no_se_retirar_al_principal_por_membresia_o_baja_global(self):
        with self.assertRaises(ValidationError):
            gestionar_miembro(self.carlos, self.entidad.pk, self.ana.pk, retirar=True)
        with self.assertRaises(ValidationError):
            guardar_estado_usuario(self.admin, self.ana, {"is_active": False})

    def test_no_se_puede_actuar_en_entidad_ajena(self):
        with self.assertRaises(PermissionDenied):
            gestionar_miembro(self.carlos, self.ajena.pk, self.ciudadano.pk)

    def test_transferencia_no_cambia_nada_hasta_aceptacion_y_no_retiene_por_defecto(self):
        miembro_con_rol(self.ana, self.entidad, "GESTOR_RESCATES")
        t = iniciar_transferencia(self.ana, self.entidad.pk, self.carlos_m.pk)
        self.assertTrue(principal_de(self.ana, self.entidad.pk))
        self.assertFalse(principal_de(self.carlos, self.entidad.pk))
        resolver_transferencia(self.carlos, t.pk, aceptar=True)
        self.assertTrue(principal_de(self.carlos, self.entidad.pk))
        self.assertFalse(principal_de(self.ana, self.entidad.pk))
        self.assertFalse(puede(self.ana, "miembros.roles", entidad_id=self.entidad.pk))
        self.assertTrue(puede(self.ana, "caso.ver", entidad_id=self.entidad.pk))

    def test_transferencia_con_casilla_conserva_secundario(self):
        t = iniciar_transferencia(self.ana, self.entidad.pk, self.carlos_m.pk, mantener_secundario=True)
        resolver_transferencia(self.carlos, t.pk, aceptar=True)
        self.assertTrue(puede(self.ana, "miembros.roles", entidad_id=self.entidad.pk))
        self.assertFalse(principal_de(self.ana, self.entidad.pk))

    def test_secundario_no_inicia_transferencia_ni_un_tercero_la_acepta(self):
        with self.assertRaises(PermissionDenied):
            iniciar_transferencia(self.carlos, self.entidad.pk, self.ana_m.pk)
        t = iniciar_transferencia(self.ana, self.entidad.pk, self.carlos_m.pk)
        with self.assertRaises(PermissionDenied):
            resolver_transferencia(self.otro, t.pk, aceptar=True)

    def test_sucesor_debe_seguir_autorizado_y_transferencia_no_se_acepta_dos_veces(self):
        t = iniciar_transferencia(self.ana, self.entidad.pk, self.carlos_m.pk)
        EntidadMiembroRol.objects.filter(miembro=self.carlos_m).update(fecha_revocacion=timezone.now())
        with self.assertRaises(PermissionDenied):
            resolver_transferencia(self.carlos, t.pk, aceptar=True)

    def test_reingreso_no_reactiva_roles_historicos(self):
        gestionar_miembro(self.ana, self.entidad.pk, self.carlos.pk, retirar=True)
        gestionar_miembro(self.ana, self.entidad.pk, self.carlos.pk)
        self.assertFalse(puede(self.carlos, "miembros.roles", entidad_id=self.entidad.pk))

    def test_recuperacion_requiere_motivo_y_cancela_transferencia(self):
        t = iniciar_transferencia(self.ana, self.entidad.pk, self.carlos_m.pk)
        with self.assertRaises(ValidationError):
            designar_principal(self.admin, self.entidad.pk, self.carlos.pk, recuperar=True)
        designar_principal(self.admin, self.entidad.pk, self.carlos.pk, recuperar=True, motivo="Recuperación de prueba")
        t.refresh_from_db()
        self.assertEqual(t.estado, "CANCELADA")
        self.assertTrue(principal_de(self.carlos, self.entidad.pk))


class ColasYFondosTests(BaseRBAC):
    def setUp(self):
        self.mod1 = cuenta("mod1")
        self.mod2 = cuenta("mod2")
        for u in (self.mod1, self.mod2):
            UsuarioRol.objects.create(usuario=u, rol=Rol.objects.get(codigo="MODERADOR"))
        from core.models import SolicitudValidacion
        self.solicitud = SolicitudValidacion.objects.create(entidad=self.entidad,
            usuario_solicitante=self.ciudadano, estado_solicitud=valor("estado_solicitud_validacion", "Pendiente"),
            observacion="Dato privado de prueba")

    def test_tomar_asigna_unicamente_y_no_existe_acceso_antes(self):
        self.assertFalse(puede(self.mod1, "entidad.validar", objeto_id=self.solicitud.pk))
        tomar(self.mod1, "verificacion", self.solicitud.pk)
        self.assertTrue(puede(self.mod1, "entidad.validar", objeto_id=self.solicitud.pk))
        self.assertFalse(puede(self.mod2, "entidad.validar", objeto_id=self.solicitud.pk))
        with self.assertRaises(ValidationError):
            tomar(self.mod2, "verificacion", self.solicitud.pk)

    def test_devolver_exige_motivo_y_retira_acceso_sin_cambiar_estado(self):
        tomar(self.mod1, "verificacion", self.solicitud.pk)
        with self.assertRaises(ValidationError):
            devolver(self.mod1, "verificacion", self.solicitud.pk, " ")
        devolver(self.mod1, "verificacion", self.solicitud.pk, "No puedo continuar")
        self.assertFalse(puede(self.mod1, "entidad.validar", objeto_id=self.solicitud.pk))
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado_solicitud.nombre, "Pendiente")
        tomar(self.mod2, "verificacion", self.solicitud.pk)
        self.assertTrue(puede(self.mod2, "entidad.validar", objeto_id=self.solicitud.pk))

    def test_no_se_puede_devolver_trabajo_ajeno(self):
        tomar(self.mod1, "verificacion", self.solicitud.pk)
        with self.assertRaises(PermissionDenied):
            devolver(self.mod2, "verificacion", self.solicitud.pk, "No es mío")

    def test_cola_solo_muestra_identificadores_sin_respuestas_o_documentos(self):
        r = self.cliente(self.mod1).get("/api/seguridad/colas/verificacion/")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data, [{"id": self.solicitud.pk, "recurso": "verificacion"}])
        self.assertNotIn("Dato privado", str(r.data))

    def test_toma_no_acepta_un_usuario_o_entidad_falsificados(self):
        r = self.cliente(self.mod1).post(f"/api/seguridad/asignaciones/verificacion/{self.solicitud.pk}/tomar/",
            {"usuario_id": self.mod2.pk}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(AsignacionRecurso.objects.exists())

    def test_revocar_moderacion_libera_sus_revisiones(self):
        tomar(self.mod1, "verificacion", self.solicitud.pk)
        asignar_global(self.admin, self.mod1.pk, Rol.objects.get(codigo="MODERADOR").pk, revocar=True)
        self.assertFalse(puede(self.mod1, "entidad.validar", objeto_id=self.solicitud.pk))
        tomar(self.mod2, "verificacion", self.solicitud.pk)

    def test_no_permite_autoverificacion(self):
        from core.models import SolicitudValidacion
        propia = SolicitudValidacion.objects.create(entidad=self.entidad, usuario_solicitante=self.mod1,
            estado_solicitud=valor("estado_solicitud_validacion", "Pendiente"))
        with self.assertRaises(PermissionDenied):
            tomar(self.mod1, "verificacion", propia.pk)

    def test_fondos_requieren_asignacion_y_admiten_varios_gestores(self):
        fondo = FondoExterno.objects.create(nombre="Fondo sintético", entidad=self.entidad,
            entidad_administradora="Entidad de prueba", tipo_fondo=valor("tipo_fondo", "General"),
            estado_fondo=valor("estado_fondo", "Activo"))
        miembro_con_rol(self.carlos, self.entidad, "GESTOR_FONDO")
        segundo = miembro_con_rol(self.ciudadano, self.entidad, "GESTOR_FONDO")
        self.assertFalse(puede(self.carlos, "fondo.reportar_distribucion", entidad_id=self.entidad.pk, objeto_id=fondo.pk))
        asignar_fondo(self.ana, fondo.pk, self.carlos_m.pk)
        asignar_fondo(self.ana, fondo.pk, segundo.pk)
        self.assertTrue(puede(self.carlos, "fondo.reportar_distribucion", entidad_id=self.entidad.pk, objeto_id=fondo.pk))
        self.assertTrue(puede(self.ciudadano, "fondo.ver", entidad_id=self.entidad.pk, objeto_id=fondo.pk))
        asignar_fondo(self.ana, fondo.pk, self.carlos_m.pk, revocar=True)
        self.assertFalse(puede(self.carlos, "fondo.ver", entidad_id=self.entidad.pk, objeto_id=fondo.pk))
        self.assertTrue(puede(self.ciudadano, "fondo.ver", entidad_id=self.entidad.pk, objeto_id=fondo.pk))

    def test_via_antigua_de_cuentas_no_publica_sin_aprobacion(self):
        from rescue.models import CuentaFundacion
        antes = CuentaFundacion.objects.count()
        r = self.cliente(self.ana).post(f"/api/fundaciones/{self.entidad.pk}/cuentas/", {}, format="json")
        self.assertEqual(r.status_code, 409)
        self.assertEqual(CuentaFundacion.objects.count(), antes)


class AdopcionAsignadaTests(BaseRBAC):
    def setUp(self):
        ciudad = Ciudad.objects.create(nombre="Ciudad sintética", departamento="Pruebas")
        self.fundacion = Fundacion.objects.create(entidad=self.entidad, nit="NIT-PRUEBA-1", ciudad=ciudad)
        especie = Especie.objects.create(nombre="Perro de prueba")
        raza = Raza.objects.create(especie=especie, nombre="Sin raza de prueba")
        self.mascota = Mascota.objects.create(raza=raza, nombre="Mascota sintética",
            estado_mascota=valor("estado_mascota", "En adopción"))
        CustodiaMascota.objects.create(mascota=self.mascota, fundacion=self.fundacion,
            usuario_registrador=self.ana, fecha_inicio=timezone.now())
        miembro_con_rol(self.carlos, self.entidad, "GESTOR_ADOPCIONES")
        self.solicitud = SolicitudAdopcion.objects.create(mascota=self.mascota, usuario_adoptante=self.ciudadano,
            estado_adopcion=valor("estado_adopcion", "Pendiente"))

    def test_servicio_real_exige_asignacion_ademas_del_rol(self):
        with self.assertRaises(PermissionDenied):
            resolver_solicitud(solicitud_id=self.solicitud.pk, fundacion_id=self.fundacion.pk,
                usuario_actor_id=self.carlos.pk, aprobar=False)
        tomar(self.carlos, "adopcion", self.solicitud.pk)
        resultado = resolver_solicitud(solicitud_id=self.solicitud.pk, fundacion_id=self.fundacion.pk,
            usuario_actor_id=self.carlos.pk, aprobar=False, observacion="Revisión de prueba")
        self.assertEqual(resultado.estado_adopcion.nombre, "Rechazada")
        with self.assertRaises(ValidationError):
            devolver(self.carlos, "adopcion", self.solicitud.pk, "Ya resuelta")

    def test_otro_rol_o_entidad_no_toma_ni_resuelve(self):
        with self.assertRaises(PermissionDenied):
            tomar(self.otro, "adopcion", self.solicitud.pk)
        self.assertFalse(puede(self.ana, "adopcion.resolver", entidad_id=self.entidad.pk, objeto_id=self.solicitud.pk))


class ZConcurrenciaTests(TransactionTestCase):
    def setUp(self):
        catalogos()

    def test_solo_un_moderador_toma_la_misma_solicitud(self):
        from core.models import SolicitudValidacion
        entidad_prueba = entidad("Concurrencia sintética")
        solicitante = cuenta("solicitante_concurrencia")
        solicitud = SolicitudValidacion.objects.create(entidad=entidad_prueba, usuario_solicitante=solicitante,
            estado_solicitud=valor("estado_solicitud_validacion", "Pendiente"))
        usuarios = [cuenta("concurrente1"), cuenta("concurrente2")]
        for usuario in usuarios:
            UsuarioRol.objects.create(usuario=usuario, rol=Rol.objects.get(codigo="MODERADOR"))
        barrera = Barrier(2)

        def intentar(pk):
            close_old_connections()
            usuario = Usuario.objects.get(pk=pk)
            barrera.wait(timeout=10)
            try:
                tomar(usuario, "verificacion", solicitud.pk)
                return "asignada"
            except ValidationError:
                return "ocupada"
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            resultados = list(pool.map(intentar, [u.pk for u in usuarios]))
        self.assertCountEqual(resultados, ["asignada", "ocupada"])
        self.assertEqual(AsignacionRecurso.objects.filter(fecha_revocacion__isnull=True).count(), 1)


class ZZDemoIntegracionTests(TransactionTestCase):
    def test_demo_actualizada_es_idempotente_y_pasa_los_flujos(self):
        from cryptography.fernet import Fernet
        from django.core.cache import cache
        catalogos()
        cache.clear()
        with patch.dict(os.environ, {"LPN_DEMO_PASSWORD": "Demo-Sintetica-Para-Pruebas-9416",
                                    "LPN_DATA_KEY": Fernet.generate_key().decode()}):
            call_command("seed_demo", stdout=StringIO())
            cantidad = Usuario.objects.count()
            call_command("seed_demo", stdout=StringIO())
            self.assertEqual(Usuario.objects.count(), cantidad)
            call_command("verify_demo", stdout=StringIO())
