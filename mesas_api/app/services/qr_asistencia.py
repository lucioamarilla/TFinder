import base64
import hashlib
import hmac
import json
import os
import time
from io import BytesIO

import qrcode

from app.infra.redis import get_redis

SECRET = os.getenv("QR_SECRET", "cambiar-qr-secret")
TTL_QR = 600


def _firma(cuerpo: dict) -> str:
    mensaje = json.dumps(cuerpo, sort_keys=True, separators=(",", ":")).encode()
    return hmac.new(SECRET.encode(), mensaje, hashlib.sha256).hexdigest()[:32]


def generar_sesion_qr(sesion_id: int, usuario_id: int) -> dict:
    exp = int(time.time()) + TTL_QR
    cuerpo = {"sesion": sesion_id, "u": usuario_id, "exp": exp}
    token = {"cuerpo": cuerpo, "firma": _firma(cuerpo)}
    data = base64.urlsafe_b64encode(
        json.dumps(token, separators=(",", ":")).encode()
    ).decode()

    qr = qrcode.QRCode(border=1)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    get_redis().setex(f"qr:sesion:{sesion_id}:{usuario_id}", TTL_QR, data)
    return {
        "qr_data": data,
        "png_base64": base64.b64encode(buffer.getvalue()).decode(),
        "expira_en_seg": TTL_QR,
        "sesion_id": sesion_id,
    }


def validar_sesion_qr(sesion_id: int, usuario_id: int, qr_data: str) -> bool:
    r = get_redis()
    ok = r.getdel(f"qr:sesion:{sesion_id}:{usuario_id}")
    if ok is None or ok.decode() != qr_data:
        raise _Conflict("QR vencido o ya utilizado")

    token = json.loads(base64.urlsafe_b64decode(qr_data.encode() + b"=" * (-len(qr_data) % 4)))
    esperada = _firma(token["cuerpo"])
    if not hmac.compare_digest(esperada, token["firma"]):
        raise _Invalid("QR inválido: firma incorrecta")
    if token["cuerpo"]["exp"] < time.time():
        raise _Conflict("QR vencido")
    return True


class _Conflict(Exception):
    pass


class _Invalid(Exception):
    pass