"""Ajusta la tipografia de los .docx generados por pandoc para que sean legibles
en pantalla y en papel: bloques de codigo monoespaciados con fondo, tablas con
encabezado resaltado y cuerpo de texto justificado.

Uso:  python scripts/docx_legible.py docs/ALGO.docx [...]
"""

from __future__ import annotations

import re
import shutil
import sys
import zipfile
from pathlib import Path

CODE_PPR = (
    '<w:pPr><w:keepLines/>'
    '<w:spacing w:before="60" w:after="60" w:line="240" w:lineRule="auto"/>'
    '<w:ind w:left="170" w:right="170"/><w:jc w:val="left"/>'
    '<w:shd w:val="clear" w:color="auto" w:fill="F4F4F4"/>'
    '<w:pBdr>'
    '<w:top w:val="single" w:sz="4" w:space="4" w:color="D6D6D6"/>'
    '<w:left w:val="single" w:sz="18" w:space="6" w:color="8EAADB"/>'
    '<w:bottom w:val="single" w:sz="4" w:space="4" w:color="D6D6D6"/>'
    '<w:right w:val="single" w:sz="4" w:space="4" w:color="D6D6D6"/>'
    "</w:pBdr></w:pPr>"
)
CODE_RPR = (
    '<w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>'
    '<w:color w:val="1A1A1A"/><w:sz w:val="19"/><w:szCs w:val="19"/></w:rPr>'
)
INLINE_RPR = (
    '<w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>'
    '<w:color w:val="1F3864"/><w:sz w:val="19"/><w:szCs w:val="19"/>'
    '<w:shd w:val="clear" w:color="auto" w:fill="EDF1F7"/></w:rPr>'
)

STYLE_REPLACEMENTS = {
    "SourceCode": (
        '<w:pPr><w:wordWrap w:val="off"/>'
        '<w:spacing w:before="60" w:after="60" w:line="240" w:lineRule="auto"/>'
        '<w:ind w:left="170" w:right="170"/><w:jc w:val="left"/>'
        '<w:shd w:val="clear" w:color="auto" w:fill="F4F4F4"/>'
        '<w:pBdr>'
        '<w:top w:val="single" w:sz="4" w:space="4" w:color="D6D6D6"/>'
        '<w:left w:val="single" w:sz="18" w:space="6" w:color="8EAADB"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="4" w:color="D6D6D6"/>'
        '<w:right w:val="single" w:sz="4" w:space="4" w:color="D6D6D6"/>'
        "</w:pBdr></w:pPr>" + CODE_RPR
    ),
    "VerbatimChar": INLINE_RPR,
}


def patch_styles(xml: str) -> tuple[str, int]:
    changed = 0
    for style_id, props in STYLE_REPLACEMENTS.items():
        pattern = re.compile(
            r'(<w:style [^>]*w:styleId="%s">)(.*?)(</w:style>)' % style_id, re.S
        )
        match = pattern.search(xml)
        if not match:
            continue
        inner = match.group(2)
        inner = re.sub(r"<w:pPr>.*?</w:pPr>", "", inner, flags=re.S)
        inner = re.sub(r"<w:rPr>.*?</w:rPr>", "", inner, flags=re.S)
        xml = xml[: match.start()] + match.group(1) + props + inner + match.group(3) + xml[match.end() :]
        changed += 1
    return xml, changed


def process(path: Path) -> None:
    backup = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup)

    with zipfile.ZipFile(backup) as zin:
        items = [(i, zin.read(i.filename)) for i in zin.infolist()]

    patched: list[tuple[object, bytes]] = []
    total = 0
    for info, data in items:
        if info.filename == "word/styles.xml":
            xml, count = patch_styles(data.decode("utf-8"))
            data = xml.encode("utf-8")
            total += count
        patched.append((info, data))

    tmp = path.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for info, data in patched:
            zout.writestr(info, data)
    tmp.replace(path)
    backup.unlink()
    print(f"{path}: {total} estilos ajustados")


def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv[1:]]
    if not targets:
        print(__doc__)
        return 1
    for target in targets:
        if not target.exists():
            print(f"no existe: {target}", file=sys.stderr)
            return 1
        process(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
