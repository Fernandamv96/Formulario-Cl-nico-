# MediForm — Formulario Clínico (Flask + SQLite)

Aplicación web para registrar consultas médicas: datos del paciente,
antecedentes, signos vitales y motivo de consulta. Incluye listado y
vista de detalle de los registros guardados.

## Estructura del proyecto

```
clinical-form-app/
├── app.py                  # Backend Flask (rutas, validación, SQLite)
├── requirements.txt
├── clinic.db                # Se crea automáticamente al ejecutar (no se versiona)
├── templates/
│   ├── base.html            # Layout base (header, nav, mensajes flash)
│   ├── form.html            # Formulario de nueva consulta
│   ├── list.html             # Listado de consultas con búsqueda
│   └── detail.html           # Detalle de una consulta
└── static/
    ├── css/style.css         # Diseño (tarjetas, tira de signos vitales, responsive)
    └── js/validation.js      # Validación en vivo del lado del cliente
```

## Instalación y ejecución local

1. Crear un entorno virtual (recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate      # En Windows: venv\Scripts\activate
   ```

2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Ejecutar la aplicación:

   ```bash
   python app.py
   ```

4. Abrir en el navegador: [http://localhost:5000](http://localhost:5000)

La base de datos SQLite (`clinic.db`) se crea automáticamente en la
primera ejecución, junto con la tabla `consultas`.

## Funcionalidades

- **Formulario de consulta** dividido en 4 secciones tipo tarjeta:
  datos del paciente, antecedentes, signos vitales y motivo de consulta.
- **Validación doble**: en el cliente (JavaScript, feedback inmediato)
  y en el servidor (Python, fuente de verdad — nunca confíes solo en el
  cliente).
- **Signos vitales** con una tira de captura estilo monitor (fuente
  monoespaciada) y detección de valores fuera de rango normal.
- **Listado de registros** con buscador por nombre, apellido o número
  de documento.
- **Vista de detalle** de cada consulta, con cálculo automático de edad
  e IMC, y opción de eliminar el registro.
- **API JSON** de solo lectura en `/api/consultas` para integraciones
  futuras.
- **Diseño responsive**: se adapta a escritorio, tablet y móvil.

## Rutas principales

| Método | Ruta                              | Descripción                          |
|--------|------------------------------------|---------------------------------------|
| GET    | `/`                                 | Formulario de nueva consulta          |
| POST   | `/guardar`                          | Guarda la consulta en SQLite          |
| GET    | `/consultas`                        | Listado (acepta `?q=` para buscar)    |
| GET    | `/consultas/<id>`                   | Detalle de una consulta               |
| POST   | `/consultas/<id>/eliminar`          | Elimina una consulta                  |
| GET    | `/api/consultas`                    | Listado en formato JSON               |

## Notas para producción

- Cambia `app.config["SECRET_KEY"]` por un valor secreto real, cargado
  desde una variable de entorno.
- Ejecuta con un servidor WSGI de producción (ej. `gunicorn app:app`),
  no con `app.run(debug=True)`.
- Si vas a manejar datos clínicos reales, evalúa requisitos de
  cifrado en reposo, control de acceso y cumplimiento normativo local
  (ej. Ley 19.628 en Chile, HIPAA en EE.UU., etc.) antes de usarlo en
  un entorno real.
- SQLite es adecuado para uso individual o de bajo volumen; para
  múltiples usuarios concurrentes, considera migrar a PostgreSQL.

## Próximos pasos sugeridos

- Autenticación de usuarios (login para el personal médico).
- Exportar consultas a PDF.
- Editar un registro existente (actualmente solo se puede ver/eliminar).
- Paginación en el listado para grandes volúmenes de registros.
