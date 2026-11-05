import os
import subprocess
import sys


def test_failfast_con_demo_seed_y_secret_default():
    env = dict(os.environ)
    env["JWT_SECRET"] = "dev-secret"
    # Forzar que no haya .env interfiriendo: correr en el cwd del proyecto.
    res = subprocess.run(
        [sys.executable, "-c", "import app.infra.token"],
        cwd="/home/lucioamarilla/tfinder_final/App_Final",
        env=env,
        capture_output=True,
        text=True,
    )
    assert res.returncode != 0, res.stdout + res.stderr
    assert "JWT_SECRET no puede ser el valor por defecto" in (res.stdout + res.stderr)


def test_arranque_ok_con_secret_valido():
    env = dict(os.environ)
    env["DEMO_SEED_ENABLED"] = "true"
    env["JWT_SECRET"] = "un-secret-seguro-para-tests"
    res = subprocess.run(
        [sys.executable, "-c", "import app.infra.token"],
        cwd="/home/lucioamarilla/tfinder_final/App_Final",
        env=env,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, res.stdout + res.stderr