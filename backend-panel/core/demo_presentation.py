"""Contenido ficticio de presentación; sin contactos ni organizaciones reales."""

PET_NAMES = (
    'Bruno', 'Luna', 'Simón', 'Nala', 'Toby', 'Mía', 'Rocky', 'Kira',
    'Coco', 'Milo', 'Canela', 'Oliver', 'Sol', 'Frida', 'Leo',
)
PEOPLE_NAMES = (
    'Valeria Ríos', 'Andrés Duarte', 'Camila Vega', 'Daniel Montes',
    'Lucía Torres', 'Mateo Salas', 'Sara Pineda', 'Nicolás León',
    'Elena Marín', 'Tomás Rojas', 'Paula Acosta', 'Gabriel Vidal',
    'Emma Sierra', 'Samuel Mora', 'Julia Campos', 'Martín Lozano',
    'Isabel Peña', 'David Solano', 'Antonia Gil', 'Alex Rivera',
)
PRODUCT_NAMES = (
    'Alimento seco para perro adulto, 2 kg', 'Alimento para cachorro, 1 kg',
    'Alimento seco para gato adulto, 1 kg', 'Alimento húmedo para gato, 85 g',
    'Alimento húmedo para perro, 100 g', 'Alimento para perro pequeño, 1 kg',
    'Alimento para perro adulto, 5 kg', 'Alimento para gato esterilizado, 1 kg',
    'Alimento para cachorro, 3 kg', 'Alimento para gato joven, 1 kg',
    'Alimento para perro mayor, 2 kg', 'Alimento húmedo para gato, 12 unidades',
    'Alimento para perro adulto, 1 kg', 'Alimento para gato adulto, 3 kg',
    'Alimento húmedo para perro, 6 unidades',
)
ENTITY_NAMES = {
    'Fundación demo 1': 'Huellas del Caribe (demostración)',
    'Fundación demo 2': 'Refugio Segunda Oportunidad (demostración)',
    'Administradora fondo demo': 'Red Solidaria Animal (demostración)',
    'Tienda aliada demo': 'Despensa Animal (demostración)',
    'Veterinaria demo': 'Consulta Animal (demostración)',
    'Clínica veterinaria demo': 'Centro de Atención Animal (demostración)',
    'Anunciante demo': 'Comunidad Aliada (demostración)',
}


def separate_pending_applications():
    """Dejar cinco animales solicitables y otros cinco para revisar solicitudes."""
    from animals.models import Mascota, CustodiaMascota
    from adoption.models import SolicitudAdopcion
    from django.utils import timezone
    for original_name, reserved_name in zip(PET_NAMES[10:], ('Duna', 'Bongo', 'Lola', 'Rocco', 'Alma')):
        original = Mascota.objects.get(nombre=original_name)
        pending = SolicitudAdopcion.objects.filter(mascota=original, estado_adopcion__nombre='Pendiente')
        if not pending.exists():
            continue
        custody = CustodiaMascota.objects.get(mascota=original, fecha_fin__isnull=True)
        reserved = Mascota.objects.create(nombre=reserved_name, raza=original.raza, estado_mascota=original.estado_mascota)
        CustodiaMascota.objects.create(mascota=reserved, fundacion=custody.fundacion, usuario_registrador=custody.usuario_registrador, fecha_inicio=timezone.now())
        pending.update(mascota=reserved)


def presentation_name(original):
    if original.startswith('Mascota demo '):
        return PET_NAMES[int(original.rsplit(' ', 1)[1]) - 1]
    if original.startswith('Producto demo '):
        return PRODUCT_NAMES[int(original.rsplit(' ', 1)[1]) - 1]
    if original.startswith('Reporte sintético de rescate '):
        number = int(original.rsplit(' ', 1)[1])
        situations = (
            'Perro sin acompañante cerca del parque; se solicita valoración del caso.',
            'Gato refugiado junto a una vivienda; se requiere apoyo para revisar su estado.',
            'Animal encontrado en zona peatonal; la comunidad solicita acompañamiento.',
            'Perro con dificultad para caminar; se solicita valoración profesional.',
            'Cachorro sin cuidador identificado; se solicita apoyo de un refugio.',
        )
        return f'{situations[(number - 1) % 5]} Caso {number:02d} (simulado).'
    return ENTITY_NAMES.get(original, original)
