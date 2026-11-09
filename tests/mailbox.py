"""Bandeja en memoria de los correos "enviados" por la suite (stub del mailer).

Estado compartido en un módulo propio de tests y NO en conftest.py: pytest
carga conftest como plugin (`conftest`) mientras los suites lo importan como
`tests.conftest`; módulo duplicado = lista duplicada. Al vivir acá, todas las
vías de import (`import conftest`, `import tests.conftest`, `tests/…`) apuntan
al mismo objeto y el stub del mailer es visible para los helpers.
"""

import re

inbox: list[dict] = []


def agregar(destino: str, asunto: str, texto: str, html: str):
    inbox.append({"destino": destino, "asunto": asunto, "texto": texto, "html": html})


def limpiar():
    inbox.clear()


def codigo_del_ultimo_mail(destino=None):
    """Extrae el código de 6 dígitos del último mail capturado (stub)."""
    assert inbox, "el flujo no generó ningún mail"
    correo = inbox[-1]
    if destino is not None:
        assert correo["destino"] == destino, (
            f"el último mail fue para {correo['destino']}, no para {destino}"
        )
    match = re.search(r"\b(\d{6})\b", correo["texto"])
    assert match, "el mail no tiene un código de 6 dígitos"
    return match.group(1)
