"""Compila los catálogos revisados; no requiere gettext del sistema operativo."""
from pathlib import Path
import re
import polib


def main():
    for source in sorted((Path(__file__).resolve().parents[1] / "locale").rglob("*.po")):
        catalog = polib.pofile(str(source))
        if catalog.fuzzy_entries() or catalog.untranslated_entries():
            raise SystemExit(f"Catálogo incompleto: {source}")
        for entry in catalog:
            for translated in entry.msgstr_plural.values() if entry.msgid_plural else [entry.msgstr]:
                if set(re.findall(r"%\(\w+\)[sdf]", entry.msgid)) != set(re.findall(r"%\(\w+\)[sdf]", translated)):
                    raise SystemExit(f"Variables de traducción diferentes: {entry.msgid}")
        catalog.save_as_mofile(str(source.with_suffix(".mo")))
        print(source.relative_to(Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    main()
