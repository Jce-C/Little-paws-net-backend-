from rest_framework.test import APIClient

from core.models import Notificacion
from seguridad.tests import BaseRBAC, valor


class NotificacionesMovilTests(BaseRBAC):
    def setUp(self):
        tipo = valor("tipo_notificacion", "Resultado de adopción")
        self.own = Notificacion.objects.create(usuario=self.ciudadano, tipo_notificacion=tipo, contenido="Resultado propio de prueba")
        self.other = Notificacion.objects.create(usuario=self.otro, tipo_notificacion=tipo, contenido="Resultado ajeno de prueba")

    def test_sin_cuenta_no_puede_listar_ni_marcar(self):
        client = APIClient()
        self.assertEqual(client.get("/api/notificaciones/").status_code, 401)
        self.assertEqual(client.post(f"/api/notificaciones/{self.own.pk}/leer/", {}, format="json").status_code, 401)

    def test_lista_solo_notificaciones_de_la_cuenta(self):
        response = self.cliente(self.ciudadano).get("/api/notificaciones/", {"usuario": self.otro.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id_notificacion"] for row in response.data], [self.own.pk])
        self.assertIsNone(response.data[0]["fecha_lectura"])

    def test_marcar_es_idempotente_y_no_modifica_notificacion_ajena(self):
        client = self.cliente(self.ciudadano)
        url = f"/api/notificaciones/{self.own.pk}/leer/"
        self.assertEqual(client.post(url, {}, format="json").status_code, 200)
        self.own.refresh_from_db()
        first_read = self.own.fecha_lectura
        self.assertIsNotNone(first_read)
        self.assertEqual(client.post(url, {}, format="json").status_code, 200)
        self.own.refresh_from_db()
        self.assertEqual(self.own.fecha_lectura, first_read)
        self.assertEqual(client.post(f"/api/notificaciones/{self.other.pk}/leer/", {}, format="json").status_code, 404)
        self.other.refresh_from_db()
        self.assertIsNone(self.other.fecha_lectura)


    def test_paginacion_y_cache_no_filtran_avisos_ajenos(self):
        for i in range(24):
            Notificacion.objects.create(usuario=self.ciudadano, tipo_notificacion=self.own.tipo_notificacion, contenido=f"Aviso QA {i}")
        client = self.cliente(self.ciudadano)
        first = client.get("/api/notificaciones/?paginado=1")
        self.assertEqual(first["Cache-Control"], "no-store")
        self.assertEqual(len(first.data["results"]), 20)
        second = client.get("/api/notificaciones/", {"paginado": "1", "antes": first.data["next_cursor"]})
        ids = [n['id_notificacion'] for n in first.data['results'] + second.data['results']]
        self.assertEqual(len(set(ids)), 25)
        self.assertNotIn(self.other.pk, ids)
        self.assertIsNone(second.data['next_cursor'])
        self.assertEqual(client.get("/api/notificaciones/?paginado=1&antes=abc").status_code, 400)
        self.assertEqual(APIClient().get("/api/notificaciones/")["Cache-Control"], "no-store")

    def test_destino_solo_si_solicitud_propiedad_y_permiso_vigentes(self):
        from adoption.models import SolicitudAdopcion
        from animals.models import Mascota
        from core.models import Permiso
        pet = Mascota.objects.create(nombre="Luna QA", descripcion_especie="Perro", estado_mascota=valor("estado_mascota", "En adopción"))
        request = SolicitudAdopcion.objects.create(usuario_adoptante=self.ciudadano, mascota=pet, estado_adopcion=valor("estado_adopcion", "Pendiente"))
        self.own.solicitud_adopcion = request
        self.own.save(update_fields=['solicitud_adopcion'])
        client = self.cliente(self.ciudadano)
        row = client.get('/api/notificaciones/').data[0]
        self.assertEqual(row['destino'], {'tipo': 'solicitud_adopcion', 'id': request.pk})
        request.usuario_adoptante = self.otro
        request.save(update_fields=['usuario_adoptante'])
        self.assertIsNone(client.get('/api/notificaciones/').data[0]['destino'])
        request.usuario_adoptante = self.ciudadano
        request.save(update_fields=['usuario_adoptante'])
        Permiso.objects.filter(codigo='adopcion.participar').update(activo=False)
        self.assertIsNone(client.get('/api/notificaciones/').data[0]['destino'])

    def test_fecha_de_lectura_es_la_persistida_en_el_servidor(self):
        url = f'/api/notificaciones/{self.own.pk}/leer/'
        client = self.cliente(self.ciudadano)
        response = client.post(url, {}, format='json')
        self.own.refresh_from_db()
        self.assertEqual(response.data['fecha_lectura'], self.own.fecha_lectura)
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertEqual(client.post(url, {}, format='json').data['fecha_lectura'], self.own.fecha_lectura)
