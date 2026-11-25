"""Consulta técnica de modelos; las transiciones se realizan en el panel de negocio."""
from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html

# Los grupos nativos no participan en nuestro Usuario; ocultarlos evita dos editores contradictorios.
if admin.site.is_registered(Group):
    admin.site.unregister(Group)


class ConsultaTecnica(admin.ModelAdmin):
    list_per_page=50
    readonly_fields=()

    def get_readonly_fields(self,request,obj=None):
        return [f.name for f in self.model._meta.fields if not any(x in f.name.lower() for x in ('password','token','cifrado','codigo_gestion_hash','respuesta_hash'))]

    def get_fields(self,request,obj=None):
        return self.get_readonly_fields(request,obj)

    def has_add_permission(self,request):return False
    def has_change_permission(self,request,obj=None):return False
    def has_delete_permission(self,request,obj=None):return False
    def has_view_permission(self,request,obj=None):
        return request.user.has_perm(f'{self.model._meta.app_label}.view_{self.model._meta.model_name}')


from adoption.models import EvaluacionAdopcion


class ConsultaEvaluacion(ConsultaTecnica):
    list_display = ('solicitud_id', 'fundacion_id', 'version', 'aceptada_en')
    list_select_related = ('solicitud', 'fundacion')
    search_fields = ()  # No plaintext search or personal data in list views.
    show_full_result_count = False

    def get_queryset(self, request):
        return super().get_queryset(request).defer('contenido_cifrado')

    def has_view_permission(self, request, obj=None):
        from seguridad.autorizacion import es_superusuario
        return es_superusuario(request.user)

    def get_readonly_fields(self, request, obj=None):
        return ('solicitud', 'fundacion', 'version', 'aceptada_en', 'evaluacion')

    @admin.display(description='Evaluación inicial privada')
    def evaluacion(self, obj):
        import json
        from adoption.questionnaire import consultar, para_revision
        return format_html('<pre style="white-space:pre-wrap">{}</pre>',
            json.dumps(para_revision(consultar(obj.solicitud_id)), ensure_ascii=False, indent=2, default=str))

    def change_view(self, request, object_id, form_url='', extra_context=None):
        response = super().change_view(request, object_id, form_url, extra_context)
        if request.method == 'GET' and response.status_code == 200:
            obj = self.get_object(request, object_id)
            from seguridad.servicios import auditar
            auditar(request.user, 'registro.consultar', 'adopcion', obj.solicitud_id,
                obj.fundacion_id, operacion='consulta-tecnica-evaluacion')
        response['Cache-Control'] = 'no-store'
        return response


admin.site.register(EvaluacionAdopcion, ConsultaEvaluacion)

for app in ('core','animals','rescue','adoption','funds','commerce','seguridad'):
    for model in apps.get_app_config(app).get_models():
        if model.__name__ in ('DesafioWeb','LimiteWeb','RevisionPanel') or admin.site.is_registered(model):
            continue
        admin.site.register(model,ConsultaTecnica)

admin.site.site_header='Little Paws Net · Administración técnica'
admin.site.site_title='Little Paws Net'
admin.site.index_title='Consulta de modelos y cuentas. Las operaciones de negocio se realizan en /panel/.'
