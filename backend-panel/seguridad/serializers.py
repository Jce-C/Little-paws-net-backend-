from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from accounts.models import Usuario
from core.models import Permiso, Recurso, Rol
from .politicas import POLITICAS, ROLES, SEGURIDAD


class EntradaEstricta:
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("Se requiere un objeto JSON")
        desconocidos = set(data) - set(self.fields)
        protegidos = {k for k in data if k in self.fields and self.fields[k].read_only}
        if desconocidos or protegidos:
            raise serializers.ValidationError({k: "Campo no permitido" for k in desconocidos | protegidos})
        return super().to_internal_value(data)


class UsuarioSerializer(EntradaEstricta, serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False)

    class Meta:
        model = Usuario
        fields = ["id_usuario", "nombre", "email", "telefono", "is_active", "fecha_registro", "password"]
        read_only_fields = ["id_usuario", "fecha_registro"]

    def validate(self, attrs):
        if self.instance is None:
            if not attrs.get("password"):
                raise serializers.ValidationError({"password": "Se requiere una contraseña inicial"})
            try:
                validate_password(attrs["password"], Usuario(nombre=attrs.get("nombre", ""), email=attrs.get("email", "")))
            except DjangoValidationError as exc:
                raise serializers.ValidationError({"password": exc.messages})
        elif "password" in attrs:
            raise serializers.ValidationError("El cambio de contraseña utiliza un proceso separado")
        return attrs

    def validate_email(self, value):
        value = Usuario.objects.normalize_email(value).strip()
        qs = Usuario.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("El correo ya está registrado")
        return value

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)


class RecursoSerializer(EntradaEstricta, serializers.ModelSerializer):
    class Meta:
        model = Recurso
        fields = ["id", "codigo", "nombre", "descripcion", "activo"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if self.instance:
            if attrs.get("codigo", self.instance.codigo) != self.instance.codigo:
                raise serializers.ValidationError("El código es estable; no puede renombrarse")
            if self.instance.codigo in {POLITICAS[c][0] for c in SEGURIDAD} and attrs.get("activo") is False:
                raise serializers.ValidationError("No se puede desactivar un recurso de seguridad esencial")
        return attrs


class PermisoSerializer(EntradaEstricta, serializers.ModelSerializer):
    recurso_codigo = serializers.CharField(source="recurso.codigo", read_only=True)

    class Meta:
        model = Permiso
        fields = ["id_permiso", "codigo", "descripcion", "recurso", "recurso_codigo", "accion", "alcance", "activo"]
        read_only_fields = ["id_permiso", "recurso", "recurso_codigo", "accion", "alcance"]

    def validate(self, attrs):
        codigo = attrs.get("codigo", self.instance.codigo if self.instance else "")
        if codigo not in POLITICAS:
            raise serializers.ValidationError("La acción no está reconocida por el servidor; registrar un permiso no implementa una operación")
        if self.instance and codigo != self.instance.codigo:
            raise serializers.ValidationError("El código del permiso no puede cambiar")
        if codigo in SEGURIDAD and attrs.get("activo") is False:
            raise serializers.ValidationError("No se puede desactivar un permiso de seguridad esencial")
        return attrs

    def create(self, validated_data):
        recurso, accion, alcance = POLITICAS[validated_data["codigo"]]
        validated_data.update(recurso=Recurso.objects.get(codigo=recurso), accion=accion, alcance=alcance)
        return super().create(validated_data)


class RolSerializer(EntradaEstricta, serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ["id_rol", "codigo", "nombre", "descripcion", "ambito", "activo", "delegable", "sistema"]
        read_only_fields = ["id_rol", "sistema"]

    def validate(self, attrs):
        if self.instance:
            for campo in ("codigo", "ambito"):
                if attrs.get(campo, getattr(self.instance, campo)) != getattr(self.instance, campo):
                    raise serializers.ValidationError(f"El {campo} de un rol es estable")
            if self.instance.sistema and attrs.get("delegable", self.instance.delegable) != self.instance.delegable:
                raise serializers.ValidationError("La delegación del rol del sistema está definida por la política")
            if self.instance.codigo in ("ADMIN_SEGURIDAD", "RESPONSABLE_PRINCIPAL", "RESPONSABLE_SECUNDARIO") and attrs.get("activo") is False:
                raise serializers.ValidationError("No se puede desactivar este rol estructural")
            if self.instance.codigo not in ROLES and self.instance.sistema:
                raise serializers.ValidationError("Rol histórico sustituido; no se reactiva desde el panel")
        if attrs.get("delegable", getattr(self.instance, "delegable", False)) and attrs.get("ambito", getattr(self.instance, "ambito", None)) != "ENTIDAD":
            raise serializers.ValidationError("Un rol global no puede delegarse desde una entidad")
        return attrs


class RolGlobalEntrada(EntradaEstricta, serializers.Serializer):
    rol_id = serializers.IntegerField(min_value=1)
    revocar = serializers.BooleanField(default=False)
    motivo = serializers.CharField(max_length=500, allow_blank=True, required=False, default="")


class MiembroEntrada(EntradaEstricta, serializers.Serializer):
    usuario_id = serializers.IntegerField(min_value=1)
    retirar = serializers.BooleanField(default=False)


class RolEntidadEntrada(EntradaEstricta, serializers.Serializer):
    miembro_id = serializers.IntegerField(min_value=1)
    rol_id = serializers.IntegerField(min_value=1)
    revocar = serializers.BooleanField(default=False)


class PrincipalEntrada(EntradaEstricta, serializers.Serializer):
    usuario_id = serializers.IntegerField(min_value=1)
    recuperar = serializers.BooleanField(default=False)
    motivo = serializers.CharField(max_length=500, required=False, default="", allow_blank=True)


class TransferenciaEntrada(EntradaEstricta, serializers.Serializer):
    sucesor_id = serializers.IntegerField(min_value=1)
    mantener_secundario = serializers.BooleanField(default=False)


class ResolucionTransferenciaEntrada(EntradaEstricta, serializers.Serializer):
    aceptar = serializers.BooleanField()


class PermisosRolEntrada(EntradaEstricta, serializers.Serializer):
    permisos = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=True)

    def validate_permisos(self, ids):
        if len(ids) != len(set(ids)) or Permiso.objects.filter(pk__in=ids, activo=True, recurso__activo=True).count() != len(ids):
            raise serializers.ValidationError("Permisos duplicados, inactivos o inexistentes")
        return ids


class MotivoEntrada(EntradaEstricta, serializers.Serializer):
    motivo = serializers.CharField(max_length=500, allow_blank=False)


class FondoEntrada(EntradaEstricta, serializers.Serializer):
    miembro_id = serializers.IntegerField(min_value=1)
    revocar = serializers.BooleanField(default=False)


class ComprobacionEntrada(EntradaEstricta, serializers.Serializer):
    permiso = serializers.CharField(max_length=80)
    entidad_id = serializers.IntegerField(min_value=1, required=False)
    objeto_id = serializers.IntegerField(min_value=1, required=False)
