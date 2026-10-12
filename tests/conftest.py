import os
import sys
from pathlib import Path

import pytest

# Configuración mínima antes de importar la app (SECRET_KEY es obligatorio fuera de debug).
os.environ.setdefault("SECRET_KEY", "clave-solo-para-tests")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app as mediform  # noqa: E402

VALID_FORM = {
    "nombres": "Ana",
    "apellidos": "Pérez",
    "tipo_documento": "RUT",
    "numero_documento": "12.345.678-5",
    "fecha_nacimiento": "1990-05-10",
    "sexo": "F",
    "motivo_consulta": "Control anual",
    "presion_sistolica": "120",
    "temperatura": "36.6",
}


@pytest.fixture
def app(tmp_path):
    mediform.app.config.update(TESTING=True, DATABASE=str(tmp_path / "test.db"))
    mediform.init_db()
    yield mediform.app


@pytest.fixture
def client(app):
    """Cliente con CSRF desactivado para probar la lógica de negocio."""
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c
    app.config["WTF_CSRF_ENABLED"] = True


@pytest.fixture
def csrf_client(app):
    """Cliente con CSRF activo (comportamiento de producción)."""
    app.config["WTF_CSRF_ENABLED"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def valid_form():
    return dict(VALID_FORM)
