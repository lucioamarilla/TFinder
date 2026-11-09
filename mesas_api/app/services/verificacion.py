"""Verificación de correo por código de 6 dígitos + recuperación de contraseña.

Objetivo (pedido del dueño): que no entren a la BD correos que no sirven.
  * Registro: los datos quedan en Redis (TTL 15 min) hasta confirmar el código;
    la fila de `usuarios` se crea recién en la verificación. Un correo sin
    confirmar simplemente expira y desaparece.
  * Recupero: sólo existe para usuarios YA registrados; el endpoint nunca
    revela si el correo existe (mismo 202 genérico).

Claves Redis (patrón de sesiones: prefijo TTL fijo):
    registro:{email}       JSON {nombre, rol, hash, codigo_sha, intentos, generada}
    registro:cool:{email}  cooldown de reenvío (cooldown de 60 s)
    recupero:{uid}         JSON {codigo_sha, intentos}
    recupero:cool:{uid}    cooldown de reenvío (60 s)

Seguridad: el código NUNCA se guarda en claro en Redis (sha256); la
comparación es en tiempo constante (hmac.compare_digest); máx. intentos;
cooldown contra flood; los mensajes no revelan existencia de cuentas.
"""

import hashlib
import hmac
import json
import secrets
import time

from app.infra import mailer
from app.infra.redis import get_redis
from mesas_api.app.models.auth_model import (
    actualizar_password_hash,
    crear_token,
    crear_usuario_con_hash,
    decodificar_token,
    guardar_sesion,
    guardar_sesion_familia,
    obtener_usuario_por_email,
    revocar_todas_las_sesiones,
)

TTL_CODIGO = 900          # 15 minutos de vida del código
COOLDOWN = 60             # segundos entre reenvíos
MAX_INTENTOS_REGISTRO = 5
MAX_INTENTOS_RECUPERO = 3

K_REGISTRO = "registro:{email}"
K_REGISTRO_COOL = "registro:cool:{email}"
K_RECUPERO = "recupero:{uid}"
K_RECUPERO_COOL = "recupero:cool:{uid}"

MSG = {
    "emailRegistrado": "El email ya está registrado",
    "sinSolicitud": "No hay una solicitud de registro pendiente para ese correo. Registrate de nuevo.",
    "codigo": "El código no es correcto.",
    "expirado": "El código no es válido o venció. Volvé a pedir uno nuevo.",
    "reinyentes": "Demasiados intentos inválidos. Volvé a pedir el código.",
    "cooldown": "Ya te enviamos un código hace poco. Esperá un minuto y volvé a pedirlo.",
    "mailRechazado": "El servidor de correo rechazó la dirección. Revisá el email ingresado.",
    "mailSinConfig": "El envío de correos no está configurado en el servidor (faltan SMTP_* en .env).",
    "mailFallo": "No se pudo enviar el correo ahora. Probá de nuevo en un momento.",
}

MENSAJE_RECUPERO = "Si el correo existe, te enviamos un código para restablecer la contraseña."


def _error(status: int, mensaje: str):
    from fastapi import HTTPException

    return HTTPException(status_code=status, detail=mensaje)


def _sha(codigo: str) -> str:
    return hashlib.sha256(codigo.encode()).hexdigest()


def _comparar(recibido: str, guardado: str) -> bool:
    return hmac.compare_digest(_sha(recibido.strip()), guardado)


def _r():
    """Devuelve el cliente Redis o 503 si la infra no está disponible."""
    try:
        return get_redis()
    except Exception as exc:  # pragma: no cover - depende del entorno
        raise _error(503, "No hay Redis disponible para la verificación.") from exc


def _leer_json(clave: str):
    valor = _r().get(clave)
    if valor is None:
        return None
    if isinstance(valor, bytes):
        valor = valor.decode()
    return json.loads(valor)


def _restar_intentos(clave: str, datos: dict, maximo: int, mensaje: str):
    """Escribe el objeto actualizado y decide la sanción por intentos."""
    datos["intentos"] = int(datos.get("intentos", 0)) + 1
    ttl = _r().ttl(clave)
    if ttl < 1:
        # Expiró en plena carrera: se limpia y se pide nuevo código.
        _r().delete(clave)
        raise _error(400, MSG["sinSolicitud"] if "registro:" in clave else MSG["codigo"])
    if datos["intentos"] >= maximo:
        _r().delete(clave)
        raise _error(400, mensaje)
    _r().setex(clave, ttl, json.dumps(datos))
    raise _error(400, MSG["codigo"])


def _code_error(exc: Exception):
    """Traduce los errores del mailer a HTTP con mensaje claro para el usuario."""
    if isinstance(exc, mailer.MailNoConfigurado):
        return _error(503, MSG["mailSinConfig"])
    if isinstance(exc, mailer.MailRechazado):
        return _error(400, MSG["mailRechazado"])
    if isinstance(exc, RuntimeError):
        return _error(503, MSG["mailFallo"])
    return _error(503, MSG["mailFallo"])


def _mandar(destino: str, codigo: str, registro: bool):
    try:
        mailer.enviar_codigo(destino, codigo, registro)
    except Exception as exc:
        raise _code_error(exc) from None


def _emitir_tokens(usuario):
    """Mismo shape que login: el usuario queda adentro al confirmar el código."""
    claims = {"sub": str(usuario["id"]), "rol": usuario["rol"], "email": usuario["email"]}
    access = crear_token(claims, tipo="access")
    refresh = crear_token(claims, tipo="refresh")
    guardar_sesion(decodificar_token(access)["jti"], usuario["id"])
    guardar_sesion(decodificar_token(refresh)["jti"], usuario["id"])
    guardar_sesion_familia(decodificar_token(access)["jti"], usuario["id"])
    guardar_sesion_familia(decodificar_token(refresh)["jti"], usuario["id"])
    return {
        "access_token": access,
        "refresh_token": refresh,
        "rol": usuario["rol"],
        "perfil": {
            "id": usuario["id"],
            "email": usuario["email"],
            "nombre": usuario.get("nombre") or "",
            "rol": usuario["rol"],
        },
    }


# ---------------------------------------------------------------------------
# Registro: solicitar código (no crea usuario) → verificar → ahí sí existe.
# ---------------------------------------------------------------------------

def registrar(email: str, password_hash: str, nombre: str, rol: str):
    email = email.strip().lower()
    r = _r()

    if obtener_usuario_por_email(email):
        raise _error(400, MSG["emailRegistrado"])

    # El primer envío también respeta cooldown: evita flood de mails por
    # re-POST del mismo endpoint (el reenvío y el registro comparten el tope).
    cool = K_REGISTRO_COOL.format(email=email)
    if r.exists(cool):
        raise _error(409, MSG["cooldown"])

    codigo = f"{secrets.randbelow(1_000_000):06d}"
    datos = {
        "nombre": nombre,
        "rol": rol,
        "hash": password_hash,
        "codigo_sha": _sha(codigo),
        "intentos": 0,
        "generada": time.time(),
    }
    r.setex(K_REGISTRO.format(email=email), TTL_CODIGO, json.dumps(datos))
    r.setex(cool, COOLDOWN, "1")
    _mandar(email, codigo, registro=True)
    return {"pendiente": True, "email": email}


def verificar_registro(email: str, codigo: str):
    email = email.strip().lower()
    clave = K_REGISTRO.format(email=email)
    datos = _leer_json(clave)
    if datos is None:
        raise _error(400, MSG["sinSolicitud"])
    if int(datos.get("intentos", 0)) >= MAX_INTENTOS_REGISTRO:
        _r().delete(clave)
        raise _error(400, MSG["reinyentes"])

    if not _comparar(codigo, datos["codigo_sha"]):
        _restar_intentos(clave, datos, MAX_INTENTOS_REGISTRO, MSG["reinyentes"])

    try:
        usuario = crear_usuario_con_hash(email, datos["hash"], datos["nombre"], datos["rol"])
    except Exception as exc:  # email UNIQUE: carrera entre dos verificaciones
        get_redis().delete(clave)
        nombre_exc = exc.__class__.__name__
        if "unique" in nombre_exc.lower() or "UniqueViolation" in nombre_exc or "23505" in str(exc):
            raise _error(400, MSG["emailRegistrado"]) from None
        raise

    r = _r()
    r.delete(clave)
    r.delete(K_REGISTRO_COOL.format(email=email))
    return _emitir_tokens(usuario)


def reenviar_registro(email: str):
    email = email.strip().lower()
    r = _r()

    if obtener_usuario_por_email(email):
        raise _error(400, MSG["emailRegistrado"])

    clave = K_REGISTRO.format(email=email)
    datos = _leer_json(clave)
    if datos is None:
        raise _error(400, MSG["sinSolicitud"])

    cool = K_REGISTRO_COOL.format(email=email)
    if r.exists(cool):
        raise _error(409, MSG["cooldown"])

    codigo = f"{secrets.randbelow(1_000_000):06d}"
    datos["codigo_sha"] = _sha(codigo)
    datos["intentos"] = 0
    r.setex(clave, TTL_CODIGO, json.dumps(datos))
    r.setex(cool, COOLDOWN, "1")
    _mandar(email, codigo, registro=True)
    return {"reenviado": True}


# ---------------------------------------------------------------------------
# Recupero: pedir código (sólo usuarios reales, respuesta genérica) → confirmar
# con código + nueva contraseña; deja fuera TODAS las sesiones anteriores.
# ---------------------------------------------------------------------------

def solicitar_recupero(email: str):
    usuario = obtener_usuario_por_email(email.strip().lower())
    if usuario is None:
        # No revela existencia: mismo 202, cero mail.
        return {"mensaje": MENSAJE_RECUPERO}

    r = _r()
    cool = K_RECUPERO_COOL.format(uid=usuario["id"])
    if r.exists(cool):
        # Anti mailbomb: no reenvía dentro del cooldown y mantiene el mismo
        # 202 genérico, para no filtrar que esa cuenta existe.
        return {"mensaje": MENSAJE_RECUPERO}

    codigo = f"{secrets.randbelow(1_000_000):06d}"
    r.setex(
        K_RECUPERO.format(uid=usuario["id"]),
        TTL_CODIGO,
        json.dumps({"codigo_sha": _sha(codigo), "intentos": 0}),
    )
    r.setex(cool, COOLDOWN, "1")
    _mandar(usuario["email"], codigo, registro=False)
    return {"mensaje": MENSAJE_RECUPERO}


def confirmar_recupero(email: str, codigo: str, password_hash: str):
    usuario = obtener_usuario_por_email(email.strip().lower())
    if usuario is None:
        raise _error(400, MSG["codigo"])

    clave = K_RECUPERO.format(uid=usuario["id"])
    datos = _leer_json(clave)
    if datos is None:
        # No hay solicitud: venció, la consumieron o banearon los intentos.
        raise _error(400, MSG["expirado"])
    if int(datos.get("intentos", 0)) >= MAX_INTENTOS_RECUPERO:
        _r().delete(clave)
        raise _error(400, MSG["reinyentes"])

    if not _comparar(codigo, datos["codigo_sha"]):
        _restar_intentos(clave, datos, MAX_INTENTOS_RECUPERO, MSG["reinyentes"])

    actualizar_password_hash(usuario["id"], password_hash)
    revocar_todas_las_sesiones(usuario["id"])
    r = _r()
    r.delete(clave)
    r.delete(K_RECUPERO_COOL.format(uid=usuario["id"]))
    return {"mensaje": "Contraseña actualizada. Ya podés entrar con la nueva."}
