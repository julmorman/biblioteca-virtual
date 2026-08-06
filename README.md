# Bibliotech

Sistema de catálogo y préstamos para bibliotecas escolares, pensado para
escuelas sin soporte técnico dedicado (muchas veces, sin siquiera
bibliotecaria). Corre como un Google Apps Script *bound* a una Google Sheets
que actúa de base de datos — sin servidores propios, sin credenciales que
gestionar, sin hosting que mantener.

## Cómo funciona

- La "base de datos" es una Google Sheet con dos pestañas: `Libros`
  (catálogo + stock) y `Prestamos` (registro de solicitudes).
- El código (`apps-script/`) corre bound a esa Sheet, con el login de Google
  de quien la administra — no requiere cuentas de servicio ni claves de API.
- Sirve una página web propia (HTML/CSS/JS) para que los alumnos vean el
  catálogo y pidan préstamos; el stock se valida y descuenta en el momento,
  protegido contra que dos alumnos se lleven el mismo último ejemplar a la vez.

## Instalación (para quien administra la biblioteca de una escuela)

Ver [`apps-script/README.md`](apps-script/README.md) — no requiere terminal
ni conocimientos de programación: alcanza con copiar una Google Sheet
plantilla y un par de clicks en "Implementar" dentro del editor de Apps
Script.

## Desarrollo

Si vas a tocar el código fuente, `apps-script/README.md` también documenta
cómo versionarlo con `clasp` (la CLI oficial de Google para Apps Script)
para poder trabajar con git como con cualquier otro proyecto.
