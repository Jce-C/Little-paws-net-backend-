"""Catálogo de formularios de negocio; delega en las mismas vistas/API validadas."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Operacion:
    area:str
    nombre:str
    url:str
    serializer:str=''
    permiso:str=''
    metodo:str='post'
    registro:bool=False

    @property
    def icono(self):
        if 'responsable' in self.nombre:return 'shield-check'
        if 'transferencia' in self.nombre:return 'heart-handshake'
        if 'verificación' in self.nombre:return 'clipboard-check'
        if 'cobertura' in self.nombre:return 'landmark'
        return {'organizaciones':'building-2','mascotas':'paw-print','reportes':'clipboard-check','adopciones':'heart-handshake','catalogo':'package','pedidos':'shopping-bag','fondos':'hand-coins','expedientes':'stethoscope'}.get(self.area,'settings')

F='seguridad.flujos_serializers.'
S='seguridad.serializers.'
N='seguridad.negocio_api.'
OPERACIONES={
'registrar-rescatada':Operacion('rescates','Registrar mascota rescatada','/api/seguridad/casos/{pk}/mascota/',F+'MascotaEntrada','caso.registrar_mascota',registro=True),
'publicar-adopcion':Operacion('mascotas','Disponibilidad para adopción','/api/seguridad/mascotas-administrar/{pk}/disponibilidad/',N+'PublicarAdopcionEntrada','mascotas.publicar_adopcion',registro=True),
'cobertura-ciudad':Operacion('organizaciones','Configurar cobertura por ciudad','/api/seguridad/organizaciones/{entidad}/cobertura/',N+'CoberturaEntrada','caso.cobertura'),
'crear-organizacion':Operacion('organizaciones','Registrar organización','/api/seguridad/organizaciones/',N+'OrganizacionEntrada','entidades.crear'),
'editar-organizacion':Operacion('organizaciones','Editar organización','/api/seguridad/organizaciones/{pk}/',N+'EditarOrganizacionEntrada','entidades.editar','patch',True),
'incorporar-miembro':Operacion('organizaciones','Incorporar o retirar integrante','/api/seguridad/entidades/{entidad}/miembros/',S+'MiembroEntrada','miembros.gestionar'),
'asignar-rol-equipo':Operacion('organizaciones','Asignar o retirar un cargo del equipo','/api/seguridad/entidades/{entidad}/roles/',S+'RolEntidadEntrada','miembros.roles'),
'designar-principal':Operacion('organizaciones','Designar responsable principal','/api/seguridad/entidades/{entidad}/principal/',S+'PrincipalEntrada','principal.designar'),
'transferir-principal':Operacion('organizaciones','Proponer transferencia de responsabilidad','/api/seguridad/entidades/{entidad}/transferencias/',S+'TransferenciaEntrada','principal.transferir'),
'resolver-transferencia':Operacion('organizaciones','Aceptar o rechazar transferencia','/api/seguridad/transferencias/{pk}/resolver/',S+'ResolucionTransferenciaEntrada','',registro=True),
'pedir-verificacion':Operacion('organizaciones','Solicitar verificación','/api/seguridad/operaciones/entidades/{entidad}/verificaciones/'),
'delegar-cuenta':Operacion('organizaciones','Delegar preparación de cuenta','/api/seguridad/operaciones/entidades/{entidad}/delegacion-cuentas/',F+'DelegacionEntrada','cuenta.delegar'),
'proponer-cuenta':Operacion('organizaciones','Preparar cuenta receptora','/api/seguridad/operaciones/entidades/{entidad}/propuestas-cuenta/',F+'CuentaEntrada','cuenta.preparar'),
'aprobar-cuenta':Operacion('organizaciones','Revisar propuesta de cuenta','/api/seguridad/operaciones/propuestas-cuenta/{pk}/',F+'Decision','cuenta.aprobar',registro=True),
'declarar-mascota':Operacion('mascotas','Registrar mi mascota','/api/seguridad/operaciones/mascotas-propias/',F+'MascotaEntrada'),
'crear-ficha':Operacion('mascotas','Crear ficha de mascota','/api/seguridad/mascotas-administrar/',F+'MascotaEntrada','mascotas.crear'),
'editar-mascota':Operacion('mascotas','Editar ficha de mascota','/api/seguridad/mascotas-administrar/{pk}/',N+'MascotaEditarEntrada','mascotas.editar','patch',True),
'crear-reporte':Operacion('reportes','Reportar una situación','/api/reportes/','rescue.serializers.ReporteCrearSerializer'),
'aceptar-reporte':Operacion('reportes','Aceptar reporte para rescate','/api/reportes/{pk}/aceptar/','rescue.serializers.AceptarSerializer','caso.aceptar',registro=True),
'proponer-correccion':Operacion('reportes','Solicitar corrección de reporte','/api/seguridad/operaciones/reportes/{pk}/correcciones/',F+'CorreccionEntrada',registro=True),
'resolver-correccion':Operacion('reportes','Resolver corrección','/api/seguridad/operaciones/correcciones/{pk}/resolver/',F+'Decision','caso.ver',registro=True),
'estado-rescate':Operacion('rescates','Actualizar estado de rescate','/api/seguridad/operaciones/casos/{pk}/estado/',F+'EstadoEntrada','caso.cambiar_estado',registro=True),
'solicitar-adopcion':Operacion('adopciones','Solicitar adopción','/api/adopcion/solicitudes/','adoption.api.SolicitudCrearSerializer'),
'resolver-adopcion':Operacion('adopciones','Resolver solicitud de adopción','/api/adopcion/solicitudes/{pk}/resolver/','adoption.api.SolicitudResolverSerializer','adopcion.resolver',registro=True),
'respuestas-adopcion':Operacion('adopciones','Completar mis respuestas','/api/seguridad/operaciones/adopciones/{pk}/respuestas/',F+'RespuestasEntrada',registro=True),
'retirar-adopcion':Operacion('adopciones','Retirar mi solicitud','/api/seguridad/operaciones/adopciones/{pk}/retirar/',F+'RetirarEntrada',registro=True),
'seguimiento-adopcion':Operacion('adopciones','Registrar seguimiento posterior','/api/seguridad/seguimientos/{pk}/',N+'SeguimientoEntrada','adopcion.seguimiento',registro=True),
'comprometer-aporte':Operacion('aportes','Registrar compromiso de aporte','/api/apadrinamientos/','rescue.serializers.CompromisoSerializer'),
'declarar-aporte':Operacion('aportes','Declarar transferencia realizada','/api/apadrinamientos/{pk}/declaraciones/','rescue.serializers.DeclaracionSerializer',registro=True),
'confirmar-aporte':Operacion('aportes','Confirmar recepción del aporte','/api/apadrinamientos/{pk}/confirmaciones/','rescue.serializers.ConfirmacionSerializer','aporte.confirmar',registro=True),
'crear-fondo':Operacion('fondos','Registrar fondo externo','/api/seguridad/fondos-administrar/',N+'FondoEntrada','fondo.crear'),
'donar-fondo':Operacion('fondos','Registrar compromiso con un fondo','/api/fondos/donaciones/','funds.api.DonacionSerializer'),
'pedir-emergencia':Operacion('fondos','Solicitar apoyo de emergencia','/api/fundaciones/{entidad}/emergencias/','funds.api.EmergenciaSerializer','fondo.solicitar'),
'distribuir-fondo':Operacion('fondos','Registrar distribución reportada','/api/fondos/{pk}/distribuciones/','funds.api.DistribucionSerializer','fondo.reportar_distribucion',registro=True),
'asignar-fondo':Operacion('fondos','Asignar o retirar gestor de un fondo','/api/seguridad/fondos/{pk}/asignar/',S+'FondoEntrada','fondo.asignar',registro=True),
'crear-producto':Operacion('catalogo','Añadir producto al catálogo','/api/seguridad/operaciones/entidades/{entidad}/productos/',F+'ProductoEntrada','producto.gestionar'),
'editar-producto':Operacion('catalogo','Editar producto y existencias','/api/seguridad/operaciones/productos/{pk}/',F+'ProductoEntrada','producto.gestionar','patch',True),
'crear-pedido':Operacion('pedidos','Crear pedido','/api/pedidos/','commerce.api.PedidoCrearSerializer'),
'estado-pedido':Operacion('pedidos','Actualizar estado del pedido','/api/seguridad/operaciones/pedidos/{pk}/estado/',F+'EstadoEntrada','pedido.gestionar',registro=True),
'autorizar-atencion':Operacion('expedientes','Autorizar atención veterinaria','/api/mascotas/{pk}/autorizaciones/','animals.serializers.AutorizarSerializer','',registro=True),
'generar-qr':Operacion('expedientes','Generar nuevo acceso QR','/api/mascotas/{pk}/qr/','',registro=True),
'registrar-atencion':Operacion('expedientes','Registrar atención veterinaria','/api/qr/{token}/atenciones/','animals.serializers.AtencionSerializer','expediente.escribir'),
'enmendar-atencion':Operacion('expedientes','Añadir enmienda clínica','/api/seguridad/operaciones/historiales/{pk}/enmiendas/',F+'EnmiendaEntrada','expediente.escribir',registro=True),
'revocar-autorizacion':Operacion('expedientes','Revocar autorización clínica','/api/seguridad/operaciones/autorizaciones/{pk}/revocar/',S+'MotivoEntrada',registro=True),
'crear-anuncio':Operacion('publicidad','Enviar anuncio a revisión','/api/seguridad/operaciones/entidades/{entidad}/anuncios/',F+'VersionEntrada','publicidad.gestionar'),
'versionar-anuncio':Operacion('publicidad','Crear nueva versión de anuncio','/api/seguridad/operaciones/anuncios/{pk}/versiones/',F+'VersionEntrada','publicidad.gestionar',registro=True),
'revisar-anuncio':Operacion('revision-publicidad','Revisar versión de anuncio','/api/seguridad/operaciones/versiones-anuncio/{pk}/revisar/',F+'Accion','publicidad.revisar',registro=True),
'resolver-verificacion':Operacion('verificaciones','Resolver verificación','/api/seguridad/operaciones/verificaciones/{pk}/resolver/',F+'Accion','entidad.validar',registro=True),
'reclamar-mascota':Operacion('reclamaciones','Presentar reclamación','/api/seguridad/operaciones/reclamaciones/',F+'ReclamarEntrada'),
'resolver-reclamacion':Operacion('reclamaciones','Resolver reclamación','/api/seguridad/operaciones/reclamaciones/{pk}/resolver/',F+'Decision','reclamacion.resolver',registro=True),
'ejecutar-titularidad':Operacion('reclamaciones','Ejecutar titularidad aprobada','/api/seguridad/operaciones/reclamaciones/{pk}/ejecutar-titularidad/',F+'TitularidadEntrada','reclamacion.ejecutar',registro=True),
'moderar-reporte':Operacion('reportes','Moderar un reporte','/api/seguridad/operaciones/reportes/{pk}/moderacion/',F+'Accion','reporte.moderar',registro=True),
}

for area,recurso in [('adopciones','adopcion'),('aportes','aporte'),('pedidos','pedido'),('verificaciones','verificacion')]:
    OPERACIONES['tomar-'+recurso]=Operacion(area,'Tomar registro para revisión',f'/api/seguridad/asignaciones/{recurso}/{{pk}}/tomar/','',recurso+'.tomar',registro=True)
    OPERACIONES['devolver-'+recurso]=Operacion(area,'Devolver registro a la cola',f'/api/seguridad/asignaciones/{recurso}/{{pk}}/devolver/',S+'MotivoEntrada',recurso+'.ver',registro=True)

OPERACIONES['editar-fondo']=Operacion('fondos','Editar fondo externo','/api/seguridad/fondos-administrar/{pk}/',N+'FondoEntrada','fondo.editar','patch',True)
OPERACIONES['tomar-reclamacion']=Operacion('reclamaciones','Tomar reclamación para revisión','/api/seguridad/operaciones/reclamaciones/{pk}/tomar/','','reclamacion.tomar',registro=True)
for area,recurso in [('adopciones','adopcion'),('aportes','aporte'),('pedidos','pedido'),('verificaciones','verificacion'),('expedientes','expediente'),('reclamaciones','reclamacion')]:
    OPERACIONES['adjuntar-'+area]=Operacion(area,'Adjuntar documento privado',f'/api/seguridad/operaciones/documentos/{recurso}/{{pk}}/cargar/',N+'DocumentoEntrada',registro=True)

from dataclasses import replace
for key in ('autorizar-atencion','generar-qr','revocar-autorizacion'):
 OPERACIONES[key+'-mascota']=replace(OPERACIONES[key],area='mascotas')
for key,permiso in {'declarar-mascota':'mascotas.participar','crear-reporte':'reportes.participar','solicitar-adopcion':'adopcion.participar','respuestas-adopcion':'adopcion.participar','retirar-adopcion':'adopcion.participar','comprometer-aporte':'aporte.participar','declarar-aporte':'aporte.participar','donar-fondo':'fondo.participar','crear-pedido':'pedido.participar','reclamar-mascota':'reclamacion.presentar'}.items():
 OPERACIONES[key]=replace(OPERACIONES[key],permiso=permiso)
