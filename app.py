"""
Formulario Clínico - Aplicación Flask
=====================================
Backend para registrar consultas médicas: datos del paciente,
antecedentes, signos vitales y motivo de consulta.
Persistencia en SQLite (archivo local, sin servidor externo).
"""

import sqlite3
from datetime import datetime, date
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, g, jsonify

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "clinic.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "cambia-esta-clave-en-produccion"  # usar variable de entorno en prod


# ---------------------------------------------------------------------------
# Conexión y esquema de la base de datos
# ---------------------------------------------------------------------------

def get_db():
    """Devuelve una conexión SQLite reutilizable dentro del contexto de la request."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS consultas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Datos del paciente
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    tipo_documento TEXT NOT NULL,
    numero_documento TEXT NOT NULL,
    fecha_nacimiento TEXT NOT NULL,
    sexo TEXT NOT NULL,
    telefono TEXT,
    email TEXT,
    direccion TEXT,

    -- Antecedentes
    antecedentes_personales TEXT,
    antecedentes_familiares TEXT,
    alergias TEXT,
    medicamentos_actuales TEXT,
    antecedentes_quirurgicos TEXT,

    -- Signos vitales
    presion_sistolica INTEGER,
    presion_diastolica INTEGER,
    frecuencia_cardiaca INTEGER,
    frecuencia_respiratoria INTEGER,
    temperatura REAL,
    saturacion_oxigeno INTEGER,
    peso REAL,
    talla REAL,

    -- Motivo de consulta
    motivo_consulta TEXT NOT NULL,
    enfermedad_actual TEXT,
    observaciones TEXT,

    -- Metadatos
    medico_responsable TEXT,
    fecha_registro TEXT NOT NULL
);
"""


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Helpers de validación / cálculo
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "nombres", "apellidos", "tipo_documento", "numero_documento",
    "fecha_nacimiento", "sexo", "motivo_consulta",
]

INT_FIELDS = ["presion_sistolica", "presion_diastolica", "frecuencia_cardiaca",
              "frecuencia_respiratoria", "saturacion_oxigeno"]
FLOAT_FIELDS = ["temperatura", "peso", "talla"]

RANGES = {
    # campo: (min, max) -> fuera de rango se marca pero no bloquea el guardado
    "presion_sistolica": (90, 140),
    "presion_diastolica": (60, 90),
    "frecuencia_cardiaca": (60, 100),
    "frecuencia_respiratoria": (12, 20),
    "temperatura": (36.0, 37.5),
    "saturacion_oxigeno": (95, 100),
}


def validate_form(form):
    """Valida los datos recibidos. Devuelve (errores: dict, datos_limpios: dict)."""
    errors = {}
    data = {}

    for field in REQUIRED_FIELDS:
        value = (form.get(field) or "").strip()
        if not value:
            errors[field] = "Este campo es obligatorio."
        data[field] = value

    # Fecha de nacimiento válida y no futura
    fn = data.get("fecha_nacimiento")
    if fn:
        try:
            parsed = datetime.strptime(fn, "%Y-%m-%d").date()
            if parsed > date.today():
                errors["fecha_nacimiento"] = "La fecha de nacimiento no puede ser futura."
        except ValueError:
            errors["fecha_nacimiento"] = "Formato de fecha inválido."

    # Documento: solo alfanumérico
    doc = data.get("numero_documento")
    if doc and not doc.replace(".", "").replace("-", "").isalnum():
        errors["numero_documento"] = "El número de documento no es válido."

    # Campos de texto opcionales
    for field in ["telefono", "email", "direccion", "antecedentes_personales",
                  "antecedentes_familiares", "alergias", "medicamentos_actuales",
                  "antecedentes_quirurgicos", "enfermedad_actual", "observaciones",
                  "medico_responsable"]:
        data[field] = (form.get(field) or "").strip()

    if data.get("email"):
        if "@" not in data["email"] or "." not in data["email"].split("@")[-1]:
            errors["email"] = "El correo electrónico no es válido."

    # Numéricos enteros
    for field in INT_FIELDS:
        raw = (form.get(field) or "").strip()
        if raw == "":
            data[field] = None
            continue
        try:
            val = int(raw)
            if val < 0 or val > 300:
                errors[field] = "Valor fuera de rango razonable."
            data[field] = val
        except ValueError:
            errors[field] = "Debe ser un número entero."
            data[field] = None

    # Numéricos decimales
    for field in FLOAT_FIELDS:
        raw = (form.get(field) or "").strip()
        if raw == "":
            data[field] = None
            continue
        try:
            val = float(raw)
            if val < 0 or val > 500:
                errors[field] = "Valor fuera de rango razonable."
            data[field] = val
        except ValueError:
            errors[field] = "Debe ser un número válido."
            data[field] = None

    data["sexo"] = form.get("sexo", "").strip()
    data["tipo_documento"] = form.get("tipo_documento", "").strip()

    return errors, data


def calcular_edad(fecha_nacimiento):
    try:
        nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
    hoy = date.today()
    return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))


def calcular_imc(peso, talla):
    """talla en metros, peso en kg."""
    if not peso or not talla:
        return None
    try:
        return round(peso / (talla ** 2), 1)
    except ZeroDivisionError:
        return None


def vital_status(value, field):
    """Devuelve 'normal', 'warning' o None si no hay rango definido / valor vacío.
    Firma (value, field) para poder usarse como filtro Jinja: {{ valor|vital_status('campo') }}
    """
    if value is None or field not in RANGES:
        return None
    lo, hi = RANGES[field]
    return "normal" if lo <= value <= hi else "warning"


app.jinja_env.filters["edad"] = calcular_edad
app.jinja_env.filters["imc"] = calcular_imc
app.jinja_env.filters["vital_status"] = vital_status


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Formulario de nueva consulta."""
    return render_template("form.html", errors={}, data={}, today=date.today().isoformat())


@app.route("/guardar", methods=["POST"])
def guardar():
    errors, data = validate_form(request.form)

    if errors:
        flash("Revisa los campos marcados en rojo antes de guardar.", "error")
        return render_template("form.html", errors=errors, data=data,
                                today=date.today().isoformat()), 400

    data["fecha_registro"] = datetime.now().isoformat(timespec="seconds")

    columns = [
        "nombres", "apellidos", "tipo_documento", "numero_documento",
        "fecha_nacimiento", "sexo", "telefono", "email", "direccion",
        "antecedentes_personales", "antecedentes_familiares", "alergias",
        "medicamentos_actuales", "antecedentes_quirurgicos",
        "presion_sistolica", "presion_diastolica", "frecuencia_cardiaca",
        "frecuencia_respiratoria", "temperatura", "saturacion_oxigeno",
        "peso", "talla", "motivo_consulta", "enfermedad_actual",
        "observaciones", "medico_responsable", "fecha_registro",
    ]
    placeholders = ", ".join("?" for _ in columns)
    values = [data.get(c) for c in columns]

    db = get_db()
    db.execute(
        f"INSERT INTO consultas ({', '.join(columns)}) VALUES ({placeholders})",
        values,
    )
    db.commit()

    flash("Consulta registrada correctamente.", "success")
    return redirect(url_for("listado"))


@app.route("/consultas")
def listado():
    """Listado con búsqueda por nombre o documento."""
    query = request.args.get("q", "").strip()
    db = get_db()

    if query:
        like = f"%{query}%"
        rows = db.execute(
            """SELECT * FROM consultas
               WHERE nombres LIKE ? OR apellidos LIKE ? OR numero_documento LIKE ?
               ORDER BY fecha_registro DESC""",
            (like, like, like),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM consultas ORDER BY fecha_registro DESC").fetchall()

    return render_template("list.html", consultas=rows, query=query)


@app.route("/consultas/<int:consulta_id>")
def detalle(consulta_id):
    db = get_db()
    consulta = db.execute("SELECT * FROM consultas WHERE id = ?", (consulta_id,)).fetchone()
    if consulta is None:
        flash("No se encontró la consulta solicitada.", "error")
        return redirect(url_for("listado"))
    return render_template("detail.html", c=consulta)


@app.route("/consultas/<int:consulta_id>/eliminar", methods=["POST"])
def eliminar(consulta_id):
    db = get_db()
    db.execute("DELETE FROM consultas WHERE id = ?", (consulta_id,))
    db.commit()
    flash("Registro eliminado.", "success")
    return redirect(url_for("listado"))


@app.route("/api/consultas")
def api_consultas():
    """Endpoint JSON simple, útil para integraciones futuras."""
    db = get_db()
    rows = db.execute("SELECT * FROM consultas ORDER BY fecha_registro DESC").fetchall()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
else:
    # Asegura que la BD exista también cuando se importa (ej. gunicorn)
    init_db()
