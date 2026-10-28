"""Sincroniza recursos del acceso sin sobrescribir formularios ni traducciones Django.

El HTML y entrada.js del backend son la fuente de verdad del acceso real.
La demo conserva un formulario ficticio y nunca reemplaza esos archivos.
"""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[2]
source = Path(__file__).resolve().parent
target = root / "backend-panel/seguridad/static/acceso"
assets = root / "demos/panel-editorial/static/acceso"
target.mkdir(parents=True, exist_ok=True)
for name in ["logo.svg", "fondo-escritorio.svg", "fondo-movil.svg"] + [f"nube-{i}.svg" for i in range(1, 7)]:
    shutil.copy2(assets / name, target / name)
css = (source / "acceso.css").read_text(encoding="utf-8").rstrip()
css += "\n.captcha-help{display:block;margin:8px 0 16px;color:#695541}.login-card .feedback{margin-bottom:20px}.label-row>a{font-size:13px}\n"
(target / "acceso.css").write_text(css, encoding="utf-8")
for name in ("JetBrainsMono.ttf", "JetBrainsMono-OFL.txt"):
    shutil.copy2(root / "demos/panel-editorial/static/seguridad/fonts" / name,
                 root / "backend-panel/seguridad/static/seguridad/fonts" / name)
assert (root / "backend-panel/seguridad/templates/seguridad/web/login.html").is_file()
assert (target / "entrada.js").is_file()
print("Recursos del acceso sincronizados; formulario, idiomas y preferencias conservados.")
