# Bibliotech — prototipo en Google Apps Script

Reemplaza el conector `streamlit-gsheets` (que fallaba con `HTTP 400`) por un
script **bound** a la propia Google Sheet: corre con el login de Google del
dueño de la planilla, así que no hay cuenta de servicio, JSON de credenciales
ni `secrets.toml`. El HTML lo servís vos, con control total del diseño.

## Archivos

- `appsscript.json` — manifiesto del proyecto (config del web app).
- `Code.js` — lógica de servidor: lee el catálogo, valida y registra
  préstamos, decrementa el stock con `LockService` para evitar que dos
  alumnos se lleven el último ejemplar al mismo tiempo.
- `Index.html` — estructura del frontend (catálogo + formulario), sin frameworks.
- `Stylesheet.html` / `JavaScript.html` — CSS y JS del frontend, separados de
  `Index.html` e inyectados con `include()` (patrón recomendado por Google
  para proyectos de Apps Script — evita un único archivo HTML gigante).

## Estructura esperada de la Sheet

- Pestaña **Libros**: columnas `Id_Libro | Titulo | Autor | Cantidad_Total | Disponibles | Prestado`
  (fila 1 = encabezados). `Disponibles` se calcula como `Cantidad_Total − Prestado` —
  el script escribe ese valor para que se vea reflejado en la sheet, pero la fuente
  de verdad es `Prestado` (nunca se lee `Disponibles` para decidir stock).
- Pestaña **Prestamos**: columnas `Fecha | Nombre | Curso | Id_Libro | Libro`
  (fila 1 = encabezados). `appendRow` escribe por posición de columna, no por
  nombre — respetar ese orden exacto.

## Cómo versionarlo en git: `clasp`

Apps Script normalmente vive solo en el editor web de Google (script.google.com),
sin git. **`clasp`** (`@google/clasp`, CLI oficial de Google) resuelve eso:
mantiene los archivos como `.js`/`.html`/`.json` locales — como cualquier
proyecto — y los sincroniza contra el proyecto de Apps Script en la nube.

### Setup (una vez, vos como desarrollador)

```bash
npm install -g @google/clasp
clasp login                       # abre el navegador, autoriza tu cuenta de Google
```

### Vincular esta carpeta a un proyecto de Apps Script

Dos caminos:

**A) Crear el proyecto bound desde acá** (requiere el ID de la Spreadsheet de prueba):
```bash
cd apps-script
clasp create --type sheets --title "Bibliotech" --parentId <ID_DE_LA_SPREADSHEET>
```

**B) Vincular un proyecto que ya creaste a mano** (Extensiones → Apps Script en la Sheet):
```bash
cd apps-script
clasp clone <SCRIPT_ID>          # el Script ID está en Configuración del proyecto
```

Ambos comandos generan `.clasp.json` (contiene el `scriptId`, es específico de
cada Sheet/despliegue — **no** se sube a git, ver `.gitignore`).

### Flujo de trabajo diario

```bash
clasp push      # sube Code.js / Index.html / appsscript.json a la nube
clasp open      # abre el editor web para probar
clasp deploy    # publica una versión del web app (genera la URL pública)
```

El código fuente de verdad queda en este repo; `clasp push` es solo el paso
de "subir la última versión", igual que un deploy.

## Cómo lo usaría una escuela sin conocimiento técnico

Ahí **no** hace falta clasp — es una herramienta para vos como desarrollador,
no para quien administra la biblioteca en cada escuela. El flujo pensado es:

1. Vos armás una Google Sheet "plantilla" con las pestañas `Libros` y
   `Prestamos`, con el script ya pegado adentro (vía `Extensiones > Apps Script`)
   y ya desplegado como web app.
2. Cada escuela hace **Archivo → Hacer una copia** de esa Sheet plantilla. La
   copia incluye el script.
3. Alguien de la escuela entra a `Extensiones > Apps Script > Implementar >
   Nueva implementación` una vez, y comparte esa URL con el resto.

Sin GitHub, sin terminal, sin credenciales — clonar una Sheet en vez de
clonar un repo.
