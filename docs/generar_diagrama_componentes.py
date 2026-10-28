"""Genera un diagrama UML de componentes editable en diagrams.net.

La estructura se deriva del backend Django real; la interfaz móvil se marca
explícitamente como diseño, no como una implementación existente.
"""

from pathlib import Path
from html import unescape
from xml.etree import ElementTree as ET


DESTINO = Path(__file__).with_name("Little Paws Net - Componentes UML.drawio")


class Pagina:
    def __init__(self, nombre, ancho=1700, alto=1120):
        self.diagram = ET.Element("diagram", id=nombre.lower().replace(" ", "-"), name=nombre)
        self.model = ET.SubElement(
            self.diagram,
            "mxGraphModel",
            dx="1700", dy="1120", grid="1", gridSize="10", guides="1",
            tooltips="1", connect="1", arrows="1", fold="1", page="1",
            pageScale="1", pageWidth=str(ancho), pageHeight=str(alto), math="0", shadow="0",
        )
        self.root = ET.SubElement(self.model, "root")
        ET.SubElement(self.root, "mxCell", id="0")
        ET.SubElement(self.root, "mxCell", id="1", parent="0")
        self.n = 1

    def nuevo_id(self, prefijo):
        self.n += 1
        return f"{prefijo}-{self.n}"

    def vertice(self, nombre, texto, x, y, w, h, estilo):
        ident = self.nuevo_id(nombre)
        celda = ET.SubElement(self.root, "mxCell", id=ident, value=unescape(texto),
                               style=estilo, vertex="1", parent="1")
        ET.SubElement(celda, "mxGeometry", x=str(x), y=str(y), width=str(w),
                      height=str(h), attrib={"as": "geometry"})
        return ident

    def linea(self, nombre, origen, destino, etiqueta="", estilo="", puntos=None):
        ident = self.nuevo_id(nombre)
        celda = ET.SubElement(self.root, "mxCell", id=ident, value=etiqueta,
                               style=estilo, edge="1", parent="1",
                               source=origen, target=destino)
        geom = ET.SubElement(celda, "mxGeometry", relative="1", attrib={"as": "geometry"})
        if puntos:
            arr = ET.SubElement(geom, "Array", attrib={"as": "points"})
            for x, y in puntos:
                ET.SubElement(arr, "mxPoint", x=str(x), y=str(y))
        return ident


TITULO = "text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=26;fontStyle=1;fontColor=#17324D;strokeColor=none;fillColor=none;"
SUBTITULO = "text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=13;fontColor=#4C6072;strokeColor=none;fillColor=none;"
CONTENEDOR = "rounded=1;arcSize=2;html=1;whiteSpace=wrap;verticalAlign=top;align=left;spacingTop=16;spacingLeft=18;fontSize=19;fontStyle=1;fontColor=#24486A;fillColor=#F5F9FE;strokeColor=#7D9DBB;strokeWidth=2;dashed=1;dashPattern=7 5;"
COMP_BASE = "shape=component;html=1;whiteSpace=wrap;rounded=0;align=left;verticalAlign=middle;spacingLeft=46;spacingRight=10;fontSize=15;fontColor=#17324D;strokeWidth=2;shadow=0;"
NOTA = "rounded=1;arcSize=6;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;spacing=12;fontSize=13;fontColor=#5F4B20;fillColor=#FFF8E6;strokeColor=#D9B85A;strokeWidth=1;"
INTERFAZ = "ellipse;aspect=fixed;html=1;whiteSpace=wrap;fillColor=#FFFFFF;strokeColor=#1B698B;strokeWidth=2;"
ETIQUETA = "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=13;fontColor=#1B536A;strokeColor=none;fillColor=none;"
CONEXION = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#457B9D;strokeWidth=2;endArrow=none;"
DEPENDENCIA = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#875CB1;strokeWidth=2;dashed=1;dashPattern=7 5;endArrow=open;endFill=0;fontSize=12;fontColor=#694089;labelBackgroundColor=#FFFFFF;"


def componente(pagina, clave, titulo, detalle, x, y, w=250, h=140, color="#FFFFFF", borde="#3978A3"):
    valor = f"&lt;b&gt;{titulo}&lt;/b&gt;&lt;br&gt;&lt;font style='font-size:12px;color:#405B70'&gt;{detalle}&lt;/font&gt;"
    return pagina.vertice(clave, valor, x, y, w, h,
                          COMP_BASE + f"fillColor={color};strokeColor={borde};")


def interfaz(pagina, clave, nombre, cx, cy):
    circulo = pagina.vertice(clave, "", cx - 11, cy - 11, 22, 22, INTERFAZ)
    pagina.vertice(f"etiqueta-{clave}", nombre, cx - 93, cy - 43, 186, 28, ETIQUETA)
    return circulo


principal = Pagina("1. Componentes e interfaces", 1700, 1200)
principal.vertice("titulo", "Little Paws Net · Diagrama de componentes UML", 45, 20, 1400, 45, TITULO)
principal.vertice("subtitulo", "Arquitectura del backend Django implementado y frontera de consumo prevista", 45, 66, 1450, 30, SUBTITULO)
principal.vertice("backend", "Backend Django + Django REST Framework", 330, 105, 1320, 970, CONTENEDOR)

cliente = componente(principal, "cliente", "Cliente móvil / web", "Prototipo de interfaz en Figma&lt;br&gt;Aún no implementado", 40, 195, 248, 145, "#FFF8E7", "#C29A39")
api = componente(principal, "api", "Enrutador API REST", "config/urls.py · JSON · JWT&lt;br&gt;health, idiomas y rutas por módulo", 485, 170, 975, 105, "#DDEFFC", "#28688F")
irest = interfaz(principal, "irest", "IAPI REST · /api/", 385, 224)
principal.linea("cliente-api", cliente, irest, "HTTP(S)/JSON*", CONEXION)
principal.linea("interfaz-api", irest, api, "", CONEXION)

modulos = [
    ("auth", "Identidad y sesión", "accounts · registro, perfil,&lt;br&gt;tokens JWT", 370, 395, "IAuth · /api/auth/", "#EDF5FF"),
    ("core", "Núcleo compartido", "core · RBAC, entidades,&lt;br&gt;catálogos, i18n, archivos", 685, 395, "ICore · /api/catalogos/", "#EAF7F0"),
    ("rescue", "Reportes y rescate", "rescue · reportes, casos,&lt;br&gt;apadrinamientos", 1000, 395, "IRescate · /api/reportes/", "#EFF6FF"),
    ("animals", "Mascotas y expediente", "animals · mascota, custodia,&lt;br&gt;QR y registros médicos", 1315, 395, "IExpediente · /api/expedientes/", "#EFF6FF"),
    ("adoptions", "Adopciones", "adoptions · solicitudes,&lt;br&gt;resolución e historial", 370, 685, "IAdopción · /api/adopciones/", "#EFF6FF"),
    ("funds", "Fondos y donaciones", "funds · fondo externo,&lt;br&gt;donación, distribución", 685, 685, "IFondos · /api/fondos/", "#EFF6FF"),
    ("commerce", "Comercio", "commerce · productos, pedidos,&lt;br&gt;publicidad, tarifas", 1000, 685, "IComercio · /api/productos/", "#EFF6FF"),
]
ids = {}
for clave, nombre, detalle, x, y, contrato, color in modulos:
    ids[clave] = componente(principal, clave, nombre, detalle, x, y, 250, 145, color)
    cara = interfaz(principal, f"i-{clave}", contrato, x + 125, y - 20)
    ruta = None
    if clave == "adoptions":
        ruta = [(344, 315), (344, 646), (495, 646)]
    elif clave == "funds":
        ruta = [(344, 315), (344, 628), (810, 628)]
    elif clave == "commerce":
        ruta = [(1614, 315), (1614, 640), (1125, 640)]
    principal.linea(f"api-{clave}", api, cara, "", CONEXION, ruta)
    principal.linea(f"puerto-{clave}", cara, ids[clave], "", CONEXION)

orm = componente(principal, "orm", "ORM y migraciones", "Django Models · migrations&lt;br&gt;Persistencia transaccional", 1315, 685, 250, 145, "#F3F0FF", "#7657A2")
mysql = principal.vertice("mysql", "MySQL 8&lt;br&gt;&lt;font style='font-size:12px'&gt;Base local por entorno&lt;/font&gt;", 1335, 940, 210, 92,
                           "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#EDEAF8;strokeColor=#7657A2;strokeWidth=2;fontSize=16;fontColor=#32244B;")
principal.linea("orm-db", orm, mysql, "SQL", CONEXION)
admin = componente(principal, "admin", "Django Admin", "Herramienta interna opcional&lt;br&gt;/admin/ · no es la app final", 370, 925, 250, 105, "#F5F5F5", "#7B8791")
principal.linea("api-admin", api, admin, "ruta /admin/", CONEXION, [(344, 315), (344, 910), (495, 910)])
principal.vertice("nota", "* El cliente es un consumidor previsto. El repositorio actual contiene el backend, no una aplicación móvil ni una pasarela de pagos.", 38, 1090, 1190, 58, NOTA)
principal.vertice("nota2", "Línea continua: interfaz ofrecida/consumida. La pestaña 2 detalla las dependencias internas y la persistencia.", 40, 1152, 1190, 35, SUBTITULO)


dependencias = Pagina("2. Dependencias internas", 1700, 1120)
dependencias.vertice("titulo", "Dependencias internas de los componentes", 45, 20, 1450, 45, TITULO)
dependencias.vertice("subtitulo", "Flecha discontinua = componente que requiere al componente señalado (según imports, modelos y servicios)", 45, 66, 1520, 32, SUBTITULO)

a2 = componente(dependencias, "accounts", "accounts", "Usuario, registro, perfil y JWT", 90, 150, 260, 120, "#EDF5FF")
c2 = componente(dependencias, "core", "core", "RBAC, entidades, catálogos,&lt;br&gt;i18n y archivos", 700, 145, 280, 130, "#EAF7F0", "#399471")
r2 = componente(dependencias, "rescue", "rescue", "Reporte, CasoRescate,&lt;br&gt;apadrinamiento", 75, 410, 265, 125)
m2 = componente(dependencias, "animals", "animals", "Mascota, custodia,&lt;br&gt;expediente/QR", 440, 410, 265, 125)
d2 = componente(dependencias, "adoptions", "adoptions", "SolicitudAdopcion&lt;br&gt;y su historial", 830, 410, 265, 125)
f2 = componente(dependencias, "funds", "funds", "Fondos, donaciones&lt;br&gt;y distribuciones", 75, 705, 265, 125)
co2 = componente(dependencias, "commerce", "commerce", "Productos, pedidos,&lt;br&gt;publicidad y tarifas", 440, 705, 265, 125)
orm2 = componente(dependencias, "orm", "Django ORM", "Models + migraciones&lt;br&gt;de todas las apps", 1190, 600, 260, 120, "#F3F0FF", "#7657A2")
db2 = dependencias.vertice("mysql", "MySQL 8", 1215, 845, 210, 95,
                            "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#EDEAF8;strokeColor=#7657A2;strokeWidth=2;fontSize=16;fontColor=#32244B;")

for nombre, origen, destino, etiqueta in [
    ("core-usuario", c2, a2, "AUTH_USER_MODEL"),
    ("accounts-core", a2, c2, "i18n"),
    ("rescue-core", r2, c2, "catálogos / entidades"),
    ("animals-core", m2, c2, "veterinario / archivos"),
    ("adoptions-core", d2, c2, "RBAC / estados"),
    ("funds-core", f2, c2, "fundaciones / estados"),
    ("commerce-core", co2, c2, "tiendas / estados"),
    ("animals-rescue", m2, r2, "casos / permisos"),
    ("rescue-animals", r2, m2, "mascotas"),
    ("adoptions-animals", d2, m2, "mascota / custodia"),
]:
    dependencias.linea(nombre, origen, destino, etiqueta, DEPENDENCIA)

dependencias.linea("core-orm", c2, orm2, "models", DEPENDENCIA)
dependencias.linea("rescue-orm", r2, orm2, "models", DEPENDENCIA)
dependencias.linea("animals-orm", m2, orm2, "models", DEPENDENCIA)
dependencias.linea("adoptions-orm", d2, orm2, "models", DEPENDENCIA)
dependencias.linea("funds-orm", f2, orm2, "models", DEPENDENCIA)
dependencias.linea("commerce-orm", co2, orm2, "models", DEPENDENCIA)
dependencias.linea("accounts-orm", a2, orm2, "models", DEPENDENCIA)
dependencias.linea("orm-mysql", orm2, db2, "persistencia SQL", CONEXION)

dependencias.vertice("capas", "Dentro de cada app API: urls → views (DRF) → serializers / servicios → models → ORM. Las vistas devuelven JSON; los serializers validan entradas y salidas. La autorización se comprueba en permisos y servicios, no en el cliente.",
                    75, 960, 1450, 85, NOTA)

raiz = ET.Element("mxfile", host="app.diagrams.net", modified="2026-10-13T00:00:00.000Z",
                agent="Codex", version="24.7.17", type="device")
raiz.append(principal.diagram)
raiz.append(dependencias.diagram)
for pagina in (principal, dependencias):
    celdas = {c.get("id") for c in pagina.root.findall("mxCell")}
    for arista in pagina.root.findall("mxCell[@edge='1']"):
        assert arista.get("source") in celdas and arista.get("target") in celdas, arista.get("id")
ET.indent(raiz, space="  ")
ET.ElementTree(raiz).write(DESTINO, encoding="utf-8", xml_declaration=True)
assert len(ET.parse(DESTINO).getroot().findall("diagram")) == 2
print(DESTINO)
