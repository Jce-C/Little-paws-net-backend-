"""Traducciones de valores controlados por el backend.

Los códigos, identificadores y textos aportados por usuarios no se traducen.
"""

from django.utils.translation import get_language


def en_ingles():
    return get_language().startswith("en")


def texto(es, en):
    return en if en_ingles() else es


ETIQUETAS = {
    "Pendiente": "Pending", "Verificada": "Verified", "Rechazada": "Rejected",
    "En atención": "In progress", "Cerrado": "Closed", "Cancelado": "Cancelled",
    "Rescate": "Rescue", "Abandono": "Abandonment", "Maltrato": "Abuse",
    "Mascota perdida": "Lost pet", "En rescate": "In rescue",
    "En recuperación": "Recovering", "En adopción": "Available for adoption",
    "Adoptada": "Adopted", "Hembra": "Female", "Macho": "Male",
    "Desconocido": "Unknown", "Pequeño": "Small", "Mediano": "Medium",
    "Grande": "Large", "Aprobada": "Approved", "Foto": "Photo",
    "Documento": "Document", "Video": "Video", "En espera": "Waiting",
    "Aceptado": "Accepted", "Comprometida": "Pledged",
    "Confirmada": "Confirmed", "Cancelada": "Cancelled", "Reportada": "Reported",
    "Alimentos": "Food", "Accesorios": "Accessories", "Salud": "Health",
    "Alimento seco": "Dry food", "Collar": "Collar", "Otro": "Other",
    "Disponible": "Available", "Inactivo": "Inactive", "Iniciado": "Started",
    "Banner": "Banner", "Mensual": "Monthly", "Pedido iniciado": "Order started",
}


def etiqueta(nombre):
    if nombre is None or not en_ingles():
        return nombre
    return ETIQUETAS.get(nombre, nombre)


ERRORES = {
    # Rescate y apadrinamiento
    "Reporte, fundación o capacidad inexistente": "Report, foundation, or capacity not found",
    "Solo se puede aceptar un reporte pendiente": "Only a pending report can be accepted",
    "Este reporte ya tiene caso": "This report already has a case",
    "La fundación debe estar verificada": "The foundation must be verified",
    "El usuario no puede aceptar casos por esta fundación": "The user cannot accept cases for this foundation",
    "El reporte está fuera de la cobertura de la fundación": "The report is outside the foundation's coverage area",
    "Sin cupos: se requiere justificación de emergencia": "No capacity: an emergency justification is required",
    "Transición de estado no permitida": "State transition not allowed",
    "Caso o capacidad inexistente": "Case or capacity not found",
    "El caso ya no está en atención": "The case is no longer in progress",
    "El usuario no puede cambiar este caso": "The user cannot change this case",
    "El monto debe ser positivo": "The amount must be positive",
    "El reporte no tiene un caso activo": "The report has no active case",
    "Apadrinamiento inexistente": "Sponsorship not found",
    "Solo el padrino puede consultar la cuenta": "Only the sponsor can view the account",
    "El reporte no tiene fundación receptora": "The report has no receiving foundation",
    "La fundación no tiene una cuenta activa": "The foundation has no active account",
    "Solo la fundación receptora puede confirmar": "Only the receiving foundation can confirm",
    "El compromiso no admite confirmaciones": "This pledge does not allow confirmations",
    "La suma confirmada supera el compromiso": "The confirmed total exceeds the pledge",
    # Expediente
    "Caso inexistente": "Case not found",
    "El caso no está activo": "The case is inactive",
    "Sin autorización para esta fundación": "Not authorized for this foundation",
    "El caso ya tiene una mascota identificada": "The case already has an identified pet",
    "La mascota debe tener una sola custodia activa": "The pet must have exactly one active custody",
    "Sin autorización de la fundación custodiante": "Not authorized by the custodian foundation",
    "El caso debe estar activo y tener mascota identificada": "The case must be active and have an identified pet",
    "La mascota ya tiene custodia activa": "The pet already has active custody",
    "Veterinario inexistente": "Veterinarian not found",
    "El veterinario no está verificado": "The veterinarian is not verified",
    "La cuenta profesional está inactiva": "The professional account is inactive",
    "Mascota o veterinario inexistente": "Pet or veterinarian not found",
    "La mascota no tiene custodia única activa": "The pet does not have exactly one active custody",
    "No hay autorización vigente para esta mascota": "There is no current authorization for this pet",
    "Código QR inválido o vencido": "Invalid or expired QR code",
    "Nombre y matrícula profesional son obligatorios": "Professional name and license number are required",
    # Adopción
    "Mascota inexistente": "Pet not found",
    "No puede solicitar adoptar una mascota propia": "You cannot apply to adopt your own pet",
    "La mascota no esta disponible para adopcion": "The pet is unavailable for adoption",
    "La fundación custodiante debe estar verificada": "The custodian foundation must be verified",
    "Ya existe una solicitud pendiente para esta mascota": "A pending application already exists for this pet",
    "La mascota ya tiene una solicitud aprobada": "The pet already has an approved application",
    "La decisión debe ser Aprobada o Rechazada": "The decision must be Approved or Rejected",
    "La resolución requiere una observación": "A decision note is required",
    "Solicitud inexistente": "Application not found",
    "Solo se puede resolver una solicitud pendiente": "Only a pending application can be decided",
    "El solicitante no puede resolver su propia solicitud": "The applicant cannot decide their own application",
    "No tiene permiso para resolver esta solicitud": "You cannot decide this application",
    "La mascota ya no está disponible para adopción": "The pet is no longer available for adoption",
    # Fondo externo
    "No tiene permiso para configurar fondos": "You cannot configure funds",
    "Nombre e instrucciones son obligatorios": "Name and instructions are required",
    "Ya existe un fondo con ese nombre": "A fund with that name already exists",
    "La cuenta del donante no está activa": "The donor account is inactive",
    "El monto comprometido debe ser positivo": "The pledged amount must be positive",
    "No tiene permiso para resolver donaciones": "You cannot decide donations",
    "La decisión debe ser Confirmada o Rechazada": "The decision must be Confirmed or Rejected",
    "La confirmación requiere una referencia externa verificable": "Confirmation requires a verifiable external reference",
    "Donación inexistente": "Donation not found",
    "No puede resolver su propio compromiso": "You cannot decide your own pledge",
    "Solo se puede resolver una donación comprometida": "Only a pledged donation can be decided",
    "No tiene permiso para reportar distribuciones": "You cannot report distributions",
    "La fundación destinataria debe estar verificada": "The receiving foundation must be verified",
    "El monto debe ser positivo y la fecha no puede ser futura": "The amount must be positive and the date cannot be in the future",
    "El criterio es obligatorio": "The criteria are required",
    "La evidencia debe ser privada y pertenecer al usuario reportador": "Evidence must be private and belong to the reporting user",
    "Distribución inexistente": "Distribution not found",
    "No es gestor autorizado de la fundación destinataria": "You are not an authorized manager of the receiving foundation",
    "El reportador no puede confirmar su propio registro": "The reporter cannot confirm their own record",
    "Solo se puede confirmar una distribución reportada": "Only a reported distribution can be confirmed",
    "La confirmación requiere una observación": "Confirmation requires a note",
}


def error(mensaje):
    if not en_ingles():
        return mensaje
    if mensaje.startswith("Falta el catálogo "):
        return "Missing catalog " + mensaje.removeprefix("Falta el catálogo ")
    if mensaje.startswith("Falta el catalogo "):
        return "Missing catalog " + mensaje.removeprefix("Falta el catalogo ")
    return ERRORES.get(mensaje, mensaje)
