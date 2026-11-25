from django.test import Client
from django.utils.translation import override, gettext
from seguridad.tests import BaseRBAC
from seguridad.i18n import traducir_formulario
from seguridad.web.usuarios import UsuarioForm
from seguridad.templatetags.panel_i18n import rol_ui
from core.models import Recurso
from django import forms
from rest_framework.exceptions import ErrorDetail
from seguridad.i18n import texto_error


class IdiomaPanelTests(BaseRBAC):
    def english(self):
        c=Client();c.force_login(self.admin);c.cookies['lpn_language']='en';return c

    def test_english_dashboard_menu_and_matrix_are_localized(self):
        c=self.english()
        page=c.get('/panel/')
        self.assertContains(page,'Your activity in numbers')
        self.assertContains(page,'Registered users')
        self.assertContains(page,'Roles per person')
        self.assertContains(page,'Security administrator')
        self.assertNotContains(page,'data-sidebar-close')
        matrix=c.get('/panel/seguridad/?tab=permisos')
        self.assertContains(matrix,'Permissions by role')
        self.assertContains(matrix,'Save permissions')
        self.assertNotContains(matrix,'Guardar permisos')

    def test_form_labels_translate_without_changing_field_keys(self):
        with override('en'):
            form=traducir_formulario(UsuarioForm())
            self.assertEqual(form.fields['nombre'].label,'Full name')
            self.assertEqual(form.fields['is_active'].label,'Active account')
            self.assertIn('password',form.fields)
            self.assertEqual(gettext('fundacion'),'Foundation')

    def test_custom_resource_name_and_organization_name_are_preserved(self):
        resource=Recurso.objects.get(codigo='usuarios')
        resource.nombre='Directorio especial Little Paws';resource.save(update_fields=['nombre'])
        page=self.english().get('/panel/usuarios/')
        self.assertContains(page,'Directorio especial Little Paws')
        with override('en'):
            self.assertEqual(rol_ui('Ciudadano · Fundación Ana'),'Citizen · Fundación Ana')

    def test_public_login_contains_inline_catalog_without_external_scripts(self):
        c=Client();c.cookies['lpn_language']='en';page=c.get('/panel/login/')
        self.assertContains(page,'Sign in')
        self.assertContains(page,'Preference applied')
        self.assertNotContains(page,'<script src=')

    def test_translated_choice_retains_domain_value_and_errors_are_readable(self):
        class OrganizationForm(forms.Form):
            tipo=forms.ChoiceField(choices=[('fundacion','fundacion'),('tienda','tienda')])
        with override('en'):
            form=traducir_formulario(OrganizationForm({'tipo':'fundacion'}))
            self.assertEqual(list(form.fields['tipo'].choices)[0],('fundacion','Foundation'))
            self.assertTrue(form.is_valid())
            self.assertEqual(form.cleaned_data['tipo'],'fundacion')
            error={'detalle':[ErrorDetail('Selecciona una opción',code='invalid')]}
            self.assertEqual(texto_error(error),'Select an option')
            self.assertEqual(error['detalle'][0].code,'invalid')
