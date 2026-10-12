import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

import app as mediform

ROOT = Path(__file__).resolve().parent.parent


def count_consultas(app):
    with sqlite3.connect(app.config["DATABASE"]) as db:
        return db.execute("SELECT COUNT(*) FROM consultas").fetchone()[0]


# --- Creación de consulta ---------------------------------------------------


def test_crear_consulta_valida(client, app, valid_form):
    resp = client.post("/guardar", data=valid_form)

    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/consultas")
    assert count_consultas(app) == 1

    listado = client.get("/consultas").get_data(as_text=True)
    assert "Ana" in listado


def test_detalle_muestra_consulta_creada(client, valid_form):
    client.post("/guardar", data=valid_form)
    resp = client.get("/consultas/1")
    assert resp.status_code == 200
    assert "Control anual" in resp.get_data(as_text=True)


# --- Validación de campos obligatorios --------------------------------------


@pytest.mark.parametrize("campo", mediform.REQUIRED_FIELDS)
def test_rechaza_campo_obligatorio_vacio(client, app, valid_form, campo):
    valid_form[campo] = "   "
    resp = client.post("/guardar", data=valid_form)

    assert resp.status_code == 400
    assert "Este campo es obligatorio." in resp.get_data(as_text=True)
    assert count_consultas(app) == 0


def test_rechaza_fecha_nacimiento_futura(client, app, valid_form):
    valid_form["fecha_nacimiento"] = "2999-01-01"
    resp = client.post("/guardar", data=valid_form)
    assert resp.status_code == 400
    assert count_consultas(app) == 0


def test_rechaza_signo_vital_no_numerico(client, app, valid_form):
    valid_form["frecuencia_cardiaca"] = "abc"
    resp = client.post("/guardar", data=valid_form)
    assert resp.status_code == 400
    assert count_consultas(app) == 0


# --- CSRF ---------------------------------------------------------------------


def test_rechaza_post_sin_token_csrf(csrf_client, app, valid_form):
    resp = csrf_client.post("/guardar", data=valid_form)
    assert resp.status_code == 400
    assert count_consultas(app) == 0


def test_rechaza_eliminar_sin_token_csrf(csrf_client):
    resp = csrf_client.post("/consultas/1/eliminar")
    assert resp.status_code == 400


def test_acepta_post_con_token_csrf(csrf_client, app, valid_form):
    html = csrf_client.get("/").get_data(as_text=True)
    token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)

    resp = csrf_client.post("/guardar", data={**valid_form, "csrf_token": token})

    assert resp.status_code == 302
    assert count_consultas(app) == 1


# --- SQL parametrizado ---------------------------------------------------------


def test_busqueda_con_inyeccion_sql_no_rompe_ni_filtra(client, valid_form):
    client.post("/guardar", data=valid_form)
    resp = client.get("/consultas", query_string={"q": "' OR '1'='1"})
    assert resp.status_code == 200
    assert "Ana" not in resp.get_data(as_text=True)


# --- Headers de seguridad -----------------------------------------------------


def test_headers_de_seguridad(client):
    resp = client.get("/")
    assert "default-src 'self'" in resp.headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in resp.headers["Content-Security-Policy"]
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


# --- Configuración segura por defecto ----------------------------------------


def _import_app_with_env(**env):
    full_env = {k: v for k, v in os.environ.items() if k not in {"SECRET_KEY", "FLASK_DEBUG"}}
    full_env.update(env)
    return subprocess.run(
        [sys.executable, "-c", "import app"],
        check=False,
        cwd=ROOT,
        env=full_env,
        capture_output=True,
        text=True,
    )


def test_falla_sin_secret_key_en_produccion(tmp_path):
    result = _import_app_with_env(DATABASE_PATH=str(tmp_path / "x.db"))
    assert result.returncode != 0
    assert "SECRET_KEY no está definido" in result.stderr


def test_arranca_sin_secret_key_en_modo_debug(tmp_path):
    result = _import_app_with_env(FLASK_DEBUG="1", DATABASE_PATH=str(tmp_path / "x.db"))
    assert result.returncode == 0, result.stderr


def test_debug_apagado_por_defecto(monkeypatch):
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    assert mediform.env_flag("FLASK_DEBUG") is False
    monkeypatch.setenv("FLASK_DEBUG", "1")
    assert mediform.env_flag("FLASK_DEBUG") is True
