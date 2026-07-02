<div align="center">

# 🩺 MediForm

### Formulario clínico digital — Flask + SQLite

Registro de consultas médicas con datos del paciente, antecedentes,
signos vitales y motivo de consulta, en una interfaz moderna y responsive.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](#licencia)

</div>

---

## Índice

- [Funcionalidades](#-funcionalidades)
- [Vista previa](#-vista-previa)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Instalación local](#-instalación-local)
- [Despliegue en producción](#-despliegue-en-producción-render)
- [Rutas de la API](#-rutas-principales)
- [Notas de seguridad](#-notas-para-producción)
- [Roadmap](#-próximos-pasos-sugeridos)

---

## ✨ Funcionalidades

| | |
|---|---|
| 🗂️ **Formulario por secciones** | Datos del paciente, antecedentes, signos vitales y motivo de consulta, organizados en tarjetas |
| ✅ **Validación doble** | En el cliente (feedback inmediato) y en el servidor (fuente de verdad) |
| 💓 **Signos vitales inteligentes** | Detecta y resalta valores fuera de rango normal (presión, FC, FR, temperatura, saturación) |
| 🔍 **Listado con búsqueda** | Filtra por nombre, apellido o número de documento |
| 📋 **Vista de detalle** | Cálculo automático de edad e IMC por paciente |
| 📱 **100% responsive** | Escritorio, tablet y móvil |
| 🔌 **API JSON** | Endpoint de solo lectura para integraciones futuras |

## 🖼️ Vista previa

<div align="center">
<table>
<tr>
<td width="50%">

**Formulario de consulta**
Tarjetas por sección con validación en vivo.

</td>
<td width="50%">

**Signos vitales**
Tira de captura estilo monitor, con alerta visual si un valor se sale de rango.

</td>
</tr>
</table>
</div>

> 💡 Tip: agrega tus propias capturas de pantalla a una carpeta `screenshots/`
> y enlázalas aquí con `![Formulario](screenshots/form.png)` para que el
> README se vea aún mejor en GitHub.

## 📁 Estructura del proyecto

```
clinical-form-app/
├── app.py                   # Backend Flask (rutas, validación, SQLite)
├── requirements.txt
├── Procfile                 # Comando de arranque para despliegue (Render/Railway/Heroku)
├── clinic.db                 # Se crea automáticamente al ejecutar (no se versiona)
├── templates/
│   ├── base.html             # Layout base (header, nav, mensajes flash)
│   ├── form.html             # Formulario de nueva consulta
│   ├── list.html              # Listado de consultas con búsqueda
│   └── detail.html            # Detalle de una consulta
└── static/
    ├── css/style.css          # Diseño (tarjetas, signos vitales, responsive)
    └── js/validation.js       # Validación en vivo del lado del cliente
```

## 🚀 Instalación local

**Requisitos:** Python 3.10 o superior.

```bash
# 1. Clonar el repositorio
git clone https://github.com/Fernandamv96/<nombre-del-repo>.git
cd <nombre-del-repo>

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python app.py
```

Abrir [http://localhost:5000](http://localhost:5000) en el navegador. La base
de datos SQLite (`clinic.db`) se crea automáticamente en la primera ejecución.

## ☁️ Despliegue en producción (Render)

[Render](https://render.com) ofrece un plan gratuito ideal para este proyecto.

1. Sube este repositorio a GitHub (ya lo tienes ✅).
2. Entra a [render.com](https://render.com) y crea una cuenta (puedes usar tu GitHub).
3. Click en **New +** → **Web Service**.
4. Selecciona este repositorio.
5. Configura:
   | Campo | Valor |
   |---|---|
   | **Runtime** | Python 3 |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn app:app` |
6. Click en **Create Web Service** y espera el build (2-3 minutos).
7. Render te entrega una URL pública como `https://mediform.onrender.com`.

> ⚠️ **Importante sobre SQLite en Render (plan gratuito):** el sistema de
> archivos es efímero, es decir, cada vez que la app se reinicia o se
> re-despliega, `clinic.db` vuelve a crearse vacío. Para producción real con
> datos persistentes, usa un **Render Disk** (almacenamiento persistente,
> plan pago) o migra a una base de datos administrada como PostgreSQL. Para
> una demo o portafolio, el comportamiento actual es suficiente.

## 🔌 Rutas principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Formulario de nueva consulta |
| `POST` | `/guardar` | Guarda la consulta en SQLite |
| `GET` | `/consultas` | Listado (acepta `?q=` para buscar) |
| `GET` | `/consultas/<id>` | Detalle de una consulta |
| `POST` | `/consultas/<id>/eliminar` | Elimina una consulta |
| `GET` | `/api/consultas` | Listado en formato JSON |

## 🔒 Notas para producción

- Cambia `app.config["SECRET_KEY"]` en `app.py` por un valor secreto real,
  cargado desde una variable de entorno (`os.environ.get("SECRET_KEY")`).
- Ya se ejecuta con `gunicorn` en producción (ver `Procfile`), en lugar de
  `app.run(debug=True)`.
- Si vas a manejar datos clínicos reales, evalúa requisitos de cifrado en
  reposo, control de acceso y cumplimiento normativo local (ej. Ley 19.628
  en Chile, HIPAA en EE. UU., etc.) antes de usarlo en un entorno real.
- SQLite es adecuado para uso individual o de bajo volumen; para múltiples
  usuarios concurrentes, considera migrar a PostgreSQL.

## 🗺️ Próximos pasos sugeridos

- [ ] Autenticación de usuarios (login para el personal médico)
- [ ] Exportar consultas a PDF
- [ ] Editar un registro existente (hoy solo se puede ver/eliminar)
- [ ] Paginación en el listado para grandes volúmenes de registros
- [ ] Migración a PostgreSQL para despliegues con múltiples usuarios

## Licencia

Este proyecto se entrega sin licencia formal específica; agrega un archivo
`LICENSE` (por ejemplo MIT) si planeas compartirlo o reutilizarlo públicamente.

---

<div align="center">
<sub>MediForm · Registro clínico interno</sub>
</div>
