# Bibliotech — prototipo en Google Apps Script

Reemplaza el conector `streamlit-gsheets` (que fallaba con `HTTP 400`) por un
script **bound** a la propia Google Sheet: corre con el login de Google de
quien accede a la app (dentro del dominio del colegio), así que no hay
cuenta de servicio, JSON de credenciales ni `secrets.toml`, y el login sirve
también para identificar a cada persona. El HTML lo servís vos, con control
total del diseño.

## Archivos

- `appsscript.json` — manifiesto del proyecto (config del web app).
- `Code.js` — lógica de servidor: perfiles y roles, catálogo, ciclo de
  préstamo completo (`Solicitado → Entregado → Devuelto`) con acciones de
  staff, y `LockService` para evitar que dos personas se lleven el último
  ejemplar al mismo tiempo.
- `Index.html` — estructura del frontend (catálogo + formulario), sin frameworks.
- `Stylesheet.html` / `JavaScript.html` — CSS y JS del frontend, separados de
  `Index.html` e inyectados con `include()` (patrón recomendado por Google
  para proyectos de Apps Script — evita un único archivo HTML gigante).

## Estructura esperada de la Sheet

- Pestaña **Libros**: columnas `Id_Libro | Titulo | Autor | Cantidad_Total | Disponibles | Prestado`
  (fila 1 = encabezados). `Disponibles` se calcula como `Cantidad_Total − Prestado` —
  el script escribe ese valor para que se vea reflejado en la sheet, pero la fuente
  de verdad es `Prestado` (nunca se lee `Disponibles` para decidir stock).
- Pestaña **Prestamos**: columnas `Id_Prestamo | Fecha | Email | Nombre | Curso |
  Id_Libro | Libro | Estado | Fecha_Entrega | Fecha_Devolucion` (fila 1 =
  encabezados). `appendRow` escribe por posición de columna, no por nombre —
  respetar ese orden exacto. `Estado` recorre `Solicitado → Entregado →
  Devuelto`; el stock de `Libros` se descuenta al Solicitar (no al Entregar)
  y se repone al confirmar la Devolución — así el último ejemplar queda sin
  stock apenas alguien lo pide, sin esperar a que pase por el mostrador.
- Pestaña **Perfiles**: columnas `Email | Nombre | Curso | Rol | FechaAlta`
  (fila 1 = encabezados). Se completa sola la primera vez que cada persona
  entra a la app (formulario de alta única). `Rol` nace en `member`; para
  dar de alta a alguien de staff se edita esa celda a mano, poniendo
  `staff`.

## Acceso y login

`appsscript.json` tiene `webapp.access: "DOMAIN"` y `webapp.executeAs:
"USER_ACCESSING"`: el web app exige login de Google del mismo dominio del
colegio antes de servir la página, y el servidor corre con la identidad de
quien está mirando la página (no con la del dueño del script). Eso es lo
que le permite a `Session.getActiveUser().getEmail()` identificar quién pide
cada préstamo, sin ningún código de autenticación propio.

**Para probarlo hace falta una cuenta del mismo Workspace** que el script
(no funciona con cuentas @gmail.com sueltas) — desplegar bajo el Workspace
real del colegio, o uno de prueba.

## Cómo probarlo (sin tener todavía el Workspace del colegio)

Hay dos niveles de prueba, según qué querés validar:

**A) Iteración rápida de la lógica (catálogo, pedir préstamo, ciclo de
estados, vista de staff)** — no requiere Workspace, sirve con tu cuenta
personal:

1. Cambiá `webapp.access` en `appsscript.json` de `"DOMAIN"` a `"MYSELF"`
   (solo vos vas a poder abrirlo — no hace falta dominio para eso). Es un
   cambio temporal, solo para probar; no lo commitees así.
2. Seguí los pasos de setup de más abajo (`clasp create`/`clone`, `clasp
   push`, `clasp deploy`) y abrí la URL que te da `clasp deploy`.
3. Vas a entrar siempre como vos mismo/a. Para ver la vista de `member`
   completá tu perfil normal. Para ver la vista de `staff`, andá a la
   pestaña `Perfiles` de la Sheet y cambiá a mano tu propia fila a
   `Rol: staff`, recargá la página.
4. Esto **no** prueba el gate de dominio en sí (`access: DOMAIN`) ni que
   dos cuentas distintas se vean como dos perfiles distintos — para eso
   hace falta B.

**B) Validación completa antes de llevarlo a una escuela real** — sí
requiere un dominio Workspace, pero no hace falta que sea el del colegio
todavía: [Google Workspace tiene un trial gratis de 14 días](https://workspace.google.com/)
que alcanza para esto. Con esa cuenta de administrador creás 2 usuarios de
prueba (uno para hacer de `member`, otro para promover a `staff`), volvés
`webapp.access` a `"DOMAIN"`, desplegás, y probás el flujo end a end de la
sección "Verificación" del plan (login bloqueado para cuentas de afuera,
alta de perfil, pedido, confirmación de entrega/devolución con la cuenta
staff).

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

1. Vos armás una Google Sheet "plantilla" con las pestañas `Libros`,
   `Prestamos` y `Perfiles` (headers ya cargados), con el script ya pegado
   adentro (vía `Extensiones > Apps Script`) y ya desplegado como web app.
2. Cada escuela hace **Archivo → Hacer una copia** de esa Sheet plantilla. La
   copia incluye el script.
3. Alguien de la escuela entra a `Extensiones > Apps Script > Implementar >
   Nueva implementación` una vez, y comparte esa URL con el resto.
4. Esa misma persona entra a la URL con su cuenta del colegio (queda de alta
   como `member`), y después edita a mano su propia fila en `Perfiles` para
   poner `Rol: staff` — es el único paso manual en Sheets que hace falta
   para arrancar; de ahí en más, promover a más staff se hace igual.

Sin GitHub, sin terminal, sin credenciales — clonar una Sheet en vez de
clonar un repo.
