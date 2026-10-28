"""Genera el despliegue UML real de desarrollo de Little Paws Net.

No representa una instalación pública: el repositorio solo incluye el backend
y su configuración documentada usa Django runserver y MySQL locales.
"""

from html import unescape
from pathlib import Path
from xml.etree import ElementTree as ET


SALIDA = Path(__file__).with_name("Little Paws Net - Despliegue UML.drawio")


class Diagrama:
    def __init__(self):
        self.raiz = ET.Element(
            "mxfile", host="app.diagrams.net", modified="2026-10-13T00:00:00.000Z",
            agent="Codex", version="24.7.17", type="device",
        )
        self.pagina = ET.SubElement(self.raiz, "diagram", id="despliegue-local", name="Despliegue actual (local)")
        self.modelo = ET.SubElement(
            self.pagina, "mxGraphModel", dx="1800", dy="1060", grid="1", gridSize="10",
            guides="1", tooltips="1", connect="1", arrows="1", fold="1",
            page="1", pageScale="1", pageWidth="1800", pageHeight="1060",
            math="0", shadow="0",
        )
        self.celdas = ET.SubElement(self.modelo, "root")
        ET.SubElement(self.celdas, "mxCell", id="0")
        ET.SubElement(self.celdas, "mxCell", id="1", parent="0")
        self.contador = 1

    def id(self, prefijo):
        self.contador += 1
        return f"{prefijo}-{self.contador}"

    def caja(self, prefijo, texto, x, y, ancho, alto, estilo):
        ident = self.id(prefijo)
        celda = ET.SubElement(
            self.celdas, "mxCell", id=ident, value=unescape(texto),
            style=estilo, vertex="1", parent="1",
        )
        ET.SubElement(celda, "mxGeometry", x=str(x), y=str(y), width=str(ancho),
                      height=str(alto), attrib={"as": "geometry"})
        return ident

    def asociacion(self, prefijo, origen, destino, etiqueta, estilo, puntos=None):
        ident = self.id(prefijo)
        celda = ET.SubElement(
            self.celdas, "mxCell", id=ident, value=etiqueta, style=estilo,
            edge="1", parent="1", source=origen, target=destino,
        )
        geo = ET.SubElement(celda, "mxGeometry", relative="1", attrib={"as": "geometry"})
        if puntos:
            lista = ET.SubElement(geo, "Array", attrib={"as": "points"})
            for x, y in puntos:
                ET.SubElement(lista, "mxPoint", x=str(x), y=str(y))
        return ident


TITULO = "text;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;fontSize=27;fontStyle=1;fontColor=#143C5B;strokeColor=none;fillColor=none;"
TEXTO = "text;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;fontSize=14;fontColor=#456276;strokeColor=none;fillColor=none;"
DISPOSITIVO = "rounded=0;html=1;whiteSpace=wrap;align=left;verticalAlign=top;spacingTop=19;spacingLeft=20;fontSize=19;fontStyle=1;fontColor=#193D56;fillColor=#EAF2FA;strokeColor=#376A91;strokeWidth=3;shadow=1;"
ENTORNO = "rounded=0;html=1;whiteSpace=wrap;align=left;verticalAlign=top;spacingTop=15;spacingLeft=15;fontSize=16;fontStyle=1;fontColor=#244B62;fillColor=#F6FAFF;strokeColor=#7197B7;strokeWidth=2;"
ARTEFACTO = "shape=note;size=16;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;spacingLeft=17;spacingRight=15;fontSize=14;fontColor=#254457;fillColor=#FFFFFF;strokeColor=#52809C;strokeWidth=2;"
BASE = "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=18;fillColor=#EEE9F8;strokeColor=#765BA4;strokeWidth=2;fontSize=16;fontColor=#3E3155;"
EXTERNO = "rounded=0;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;spacingLeft=18;fontSize=16;fontColor=#524B70;fillColor=#F3EFFB;strokeColor=#8774A6;strokeWidth=2;"
NOTA = "rounded=1;arcSize=5;html=1;whiteSpace=wrap;align=left;verticalAlign=middle;spacing=14;fontSize=14;fontColor=#655025;fillColor=#FFF7E5;strokeColor=#C8A24C;strokeWidth=1;"
RED = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#247292;strokeWidth=2.5;endArrow=none;fontSize=13;fontColor=#174962;labelBackgroundColor=#FFFFFF;"
GESTION = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;jettySize=auto;orthogonalLoop=1;strokeColor=#8065A6;strokeWidth=2;dashed=1;dashPattern=7 5;endArrow=open;endFill=0;fontSize=13;fontColor=#62467F;labelBackgroundColor=#FFFFFF;"


d = Diagrama()
d.caja("titulo", "Little Paws Net · Diagrama de despliegue UML", 45, 28, 1520, 42, TITULO)
d.caja("subtitulo", "Estado comprobado: desarrollo local por integrante; no representa un servidor público", 45, 73, 1600, 31, TEXTO)

# Repositorio remoto: distribución de artefactos, nunca nodo de ejecución.
github = d.caja(
    "github", "&lt;b&gt;«external» GitHub&lt;/b&gt;&lt;br&gt;Repositorio de código y migraciones&lt;br&gt;&lt;font style='font-size:12px'&gt;No ejecuta la API&lt;/font&gt;",
    55, 178, 270, 160, EXTERNO,
)

# Cada integrante reproduce esta misma topología en su propia estación.
pc = d.caja(
    "estacion", "«device» Estación de desarrollo · Windows&lt;br&gt;&lt;font style='font-size:12px;font-weight:normal'&gt;Topología local reproducible en el PC de cada integrante; CPU/RAM no documentadas&lt;/font&gt;",
    395, 140, 1340, 725, DISPOSITIVO,
)
navegador = d.caja(
    "navegador", "«executionEnvironment» Navegador", 445, 260, 315, 185, ENTORNO,
)
cliente = d.caja(
    "cliente", "«artifact» Cliente de prueba&lt;br&gt;Solicitudes HTTP y respuesta JSON&lt;br&gt;JWT · Accept-Language: es/en",
    475, 323, 255, 88, ARTEFACTO,
)

python = d.caja(
    "python", "«executionEnvironment» Python 3 + .venv&lt;br&gt;&lt;font style='font-size:12px;font-weight:normal'&gt;manage.py runserver · solo desarrollo&lt;/font&gt;",
    810, 230, 425, 540, ENTORNO,
)
backend = d.caja(
    "backend", "«artifact» Backend Django 5.2.18&lt;br&gt;DRF 3.18.3 · Simple JWT 5.5.1&lt;br&gt;config + accounts + core + rescue&lt;br&gt;animals + adoptions + funds + commerce",
    845, 335, 352, 175, ARTEFACTO,
)
env = d.caja(
    "env", "«artifact» backend-panel/.env (local)&lt;br&gt;Secretos, conexión MySQL y clave Fernet",
    845, 565, 352, 80, ARTEFACTO,
)
migraciones = d.caja(
    "migraciones", "«artifact» apps/*/migrations&lt;br&gt;Esquema aplicado con manage.py migrate",
    845, 680, 352, 70, ARTEFACTO,
)

mysql = d.caja(
    "mysql", "«executionEnvironment» MySQL Server 8&lt;br&gt;&lt;font style='font-size:12px;font-weight:normal'&gt;Servicio instalado localmente&lt;/font&gt;",
    1280, 260, 385, 340, ENTORNO,
)
datos = d.caja(
    "datos", "«database» little_paws_net_equipo&lt;br&gt;Tablas creadas por migraciones Django",
    1320, 355, 305, 135, BASE,
)

# Asociaciones de comunicación sólidas: el tráfico es loopback en la estación.
d.asociacion("github-pc", github, pc, "git clone / pull / push (HTTPS)", GESTION)
d.asociacion("browser-api", cliente, backend, "HTTP · 127.0.0.1:8000 · /api/", RED)
d.asociacion("api-db", backend, datos, "TCP · 127.0.0.1:3306 · mysqlclient 2.3.0", RED)
d.asociacion("env-api", backend, env, "lee configuración", GESTION)
d.asociacion("migraciones-db", migraciones, datos, "DDL al migrar", GESTION)

d.caja(
    "nota-estado",
    "&lt;b&gt;Límite del despliegue actual&lt;/b&gt;&lt;br&gt;No hay frontend móvil/web implementado, servidor de producción, dominio público ni pasarela de pagos. El navegador prueba la API; la interfaz Figma es un diseño. Para exponer el sistema fuera del PC harían falta un cliente real, servidor de aplicación, HTTPS, configuración de seguridad y operación de la base.",
    55, 900, 1665, 105, NOTA,
)

# Verificación estructural de todas las asociaciones y del formato draw.io.
ids = {c.get("id") for c in d.celdas.findall("mxCell")}
for enlace in d.celdas.findall("mxCell[@edge='1']"):
    assert enlace.get("source") in ids and enlace.get("target") in ids, enlace.get("id")
ET.indent(d.raiz, space="  ")
ET.ElementTree(d.raiz).write(SALIDA, encoding="utf-8", xml_declaration=True)
assert ET.parse(SALIDA).getroot().tag == "mxfile"
print(SALIDA)
