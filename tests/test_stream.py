import asyncio
import json

import pytest

from notif_api.app.services.stream import StreamHub


@pytest.fixture
def hub():
    return StreamHub()


def test_suscribir_y_desuscribir(hub):
    s = hub.suscribir(usuario_id=1)
    assert s in hub._suscriptores
    hub.desuscribir(s)
    assert s not in hub._suscriptores


def test_desuscribir_inexistente_no_falla(hub):
    s = hub.suscribir(usuario_id=1)
    hub.desuscribir(s)
    hub.desuscribir(s)


def test_publicar_filtra_por_usuario(hub):
    hub._redis = None  # forzar camino en memoria para determinismo
    async def run():
        s1 = hub.suscribir(usuario_id=1)
        s2 = hub.suscribir(usuario_id=2)
        s_all = hub.suscribir(usuario_id=None)
        loop = asyncio.get_event_loop()
        s1.loop = loop
        s1.cola = asyncio.Queue(maxsize=200)
        s2.loop = loop
        s2.cola = asyncio.Queue(maxsize=200)
        s_all.loop = loop
        s_all.cola = asyncio.Queue(maxsize=200)

        hub.publicar(1, {"titulo": "hola"})
        await asyncio.sleep(0)
        assert not s1.cola.empty()
        assert not s_all.cola.empty()
        assert s2.cola.empty()

    asyncio.run(run())


def test_publicar_sin_suscriptores_no_falla(hub):
    hub.publicar(999, {"titulo": "nadie"})
    assert hub._suscriptores == []


def test_iterar_entrega_data_publicada(hub):
    async def run():
        s = hub.suscribir(usuario_id=1)
        loop = asyncio.get_event_loop()
        s.loop = loop

        agen = hub.iterar(s)
        task = asyncio.ensure_future(agen.__anext__())
        await asyncio.sleep(0)
        assert s.cola is not None
        s.cola.put_nowait({"usuario_id": 1, "data": json.dumps({"x": 1})})
        primer = await task
        assert primer.startswith("data: ")
        await agen.aclose()

    asyncio.run(run())