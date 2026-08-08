// Bibliotech — lógica de servidor (Google Apps Script, bound a la Spreadsheet)
// Corre con el login de Google de quien accede (webapp.executeAs: USER_ACCESSING,
// webapp.access: DOMAIN en appsscript.json): no requiere cuenta de servicio,
// JSON de credenciales, ni secrets.toml — el gate de acceso lo hace Google.

const SHEET_LIBROS = 'Libros';
const SHEET_PRESTAMOS = 'Prestamos';
const SHEET_PERFILES = 'Perfiles';

const ROL_STAFF = 'staff';
const ROL_MEMBER = 'member';

const ESTADO_SOLICITADO = 'Solicitado';
const ESTADO_ENTREGADO = 'Entregado';
const ESTADO_DEVUELTO = 'Devuelto';

function doGet() {
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle('Bibliotech')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/** Inyecta Stylesheet.html / JavaScript.html dentro de Index.html. */
function include(filename) {
  return HtmlService.createHtmlOutputFromFile(filename).getContent();
}

/** Lee una sheet completa y devuelve encabezados + filas (sin la fila de encabezado). */
function leerSheet_(nombre) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(nombre);
  const data = sheet.getDataRange().getValues();
  const headers = data.shift();
  return { sheet, headers, rows: data };
}

/**
 * Perfil (Email/Nombre/Curso/Rol) de quien está usando la app, o null si
 * todavía no completó el alta (primera visita). El email sale de la sesión
 * de Google, nunca del cliente.
 */
function obtenerPerfilActual() {
  const email = Session.getActiveUser().getEmail();
  const { headers, rows } = leerSheet_(SHEET_PERFILES);
  const idxEmail = headers.indexOf('Email');
  const idxNombre = headers.indexOf('Nombre');
  const idxCurso = headers.indexOf('Curso');
  const idxRol = headers.indexOf('Rol');

  const fila = rows.find(row => row[idxEmail] === email);
  if (!fila) return null;

  return {
    email,
    nombre: fila[idxNombre],
    curso: fila[idxCurso],
    rol: fila[idxRol] || ROL_MEMBER
  };
}

/**
 * Da de alta el perfil de quien está usando la app. El rol siempre se fija
 * en 'member' del lado del servidor (nunca se toma del cliente); para
 * promover a alguien a 'staff' se edita la columna Rol directamente en la
 * pestaña Perfiles.
 */
function crearPerfil(datos) {
  const existente = obtenerPerfilActual();
  if (existente) {
    return { ok: true, perfil: existente };
  }

  const email = Session.getActiveUser().getEmail();
  const nombre = (datos.nombre || '').trim();
  const curso = (datos.curso || '').trim();

  if (!nombre || !curso) {
    return { ok: false, error: 'Completá todos los campos.' };
  }

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_PERFILES);
  sheet.appendRow([email, nombre, curso, ROL_MEMBER, new Date()]);

  return { ok: true, perfil: { email, nombre, curso, rol: ROL_MEMBER } };
}

/** Lanza si quien está usando la app no tiene perfil o no es staff. */
function requerirStaff_() {
  const perfil = obtenerPerfilActual();
  if (!perfil || perfil.rol !== ROL_STAFF) {
    throw new Error('No autorizado.');
  }
  return perfil;
}

/**
 * Devuelve el catálogo con stock > 0.
 * Encabezados esperados en la fila 1 de "Libros":
 * Id_Libro | Titulo | Autor | Cantidad_Total | Disponibles | Prestado
 *
 * Disponibles se calcula como Cantidad_Total − Prestado (no se lee la
 * columna Disponibles directamente: queda como reflejo visual, la fuente
 * de verdad es Cantidad_Total/Prestado).
 */
function getCatalogo() {
  const { headers, rows } = leerSheet_(SHEET_LIBROS);
  const idxTitulo = headers.indexOf('Titulo');
  const idxAutor = headers.indexOf('Autor');
  const idxCantidadTotal = headers.indexOf('Cantidad_Total');
  const idxPrestado = headers.indexOf('Prestado');

  return rows
    .map(row => {
      const cantidadTotal = Number(row[idxCantidadTotal]) || 0;
      const prestado = Number(row[idxPrestado]) || 0;
      return {
        titulo: row[idxTitulo],
        autor: row[idxAutor],
        disponibles: cantidadTotal - prestado
      };
    })
    .filter(libro => libro.disponibles > 0);
}

/**
 * Registra un préstamo para quien está usando la app: valida perfil y
 * stock, incrementa "Prestado" y agrega la fila en "Prestamos" con Estado
 * "Solicitado". Usa LockService para evitar que dos envíos simultáneos
 * reserven el mismo último ejemplar (el bug que tenía la versión Streamlit).
 * El stock se descuenta acá mismo, no al confirmar la entrega — así un
 * segundo pedido del último ejemplar ya lo ve sin stock aunque el libro
 * todavía esté "Solicitado" y no haya pasado por el mostrador.
 */
function registrarPrestamo(datos) {
  const perfil = obtenerPerfilActual();
  if (!perfil) {
    return { ok: false, error: 'Completá tu perfil antes de pedir un préstamo.' };
  }

  const libro = datos.libro;
  if (!libro) {
    return { ok: false, error: 'Elegí un libro.' };
  }

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const libros = ss.getSheetByName(SHEET_LIBROS);
    const data = libros.getDataRange().getValues();
    const headers = data[0];
    const idxIdLibro = headers.indexOf('Id_Libro');
    const idxTitulo = headers.indexOf('Titulo');
    const idxCantidadTotal = headers.indexOf('Cantidad_Total');
    const idxDisponibles = headers.indexOf('Disponibles');
    const idxPrestado = headers.indexOf('Prestado');

    let rowIndex = -1;
    let idLibro = null;
    let cantidadTotal = 0;
    let prestado = 0;
    for (let i = 1; i < data.length; i++) {
      if (data[i][idxTitulo] === libro) {
        rowIndex = i + 1; // 1-based para getRange, +1 por la fila de encabezado
        idLibro = data[i][idxIdLibro];
        cantidadTotal = Number(data[i][idxCantidadTotal]) || 0;
        prestado = Number(data[i][idxPrestado]) || 0;
        break;
      }
    }

    if (rowIndex === -1) {
      return { ok: false, error: 'El libro no existe en el catálogo.' };
    }

    const disponibles = cantidadTotal - prestado;
    if (disponibles <= 0) {
      return { ok: false, error: 'Ese libro ya no tiene stock disponible.' };
    }

    const nuevoPrestado = prestado + 1;
    libros.getRange(rowIndex, idxPrestado + 1).setValue(nuevoPrestado);
    libros.getRange(rowIndex, idxDisponibles + 1).setValue(cantidadTotal - nuevoPrestado);

    const prestamos = ss.getSheetByName(SHEET_PRESTAMOS);
    prestamos.appendRow([
      Utilities.getUuid(),
      new Date(),
      perfil.email,
      perfil.nombre,
      perfil.curso,
      idLibro,
      libro,
      ESTADO_SOLICITADO,
      '',
      ''
    ]);

    return { ok: true };
  } catch (err) {
    return { ok: false, error: err.message };
  } finally {
    lock.releaseLock();
  }
}

/** Préstamos de quien está usando la app, más recientes primero. */
function getMisPrestamos() {
  const email = Session.getActiveUser().getEmail();
  const { headers, rows } = leerSheet_(SHEET_PRESTAMOS);
  const idxEmail = headers.indexOf('Email');
  const idxLibro = headers.indexOf('Libro');
  const idxEstado = headers.indexOf('Estado');
  const idxFecha = headers.indexOf('Fecha');

  return rows
    .filter(row => row[idxEmail] === email)
    .map(row => ({
      libro: row[idxLibro],
      estado: row[idxEstado],
      fecha: row[idxFecha]
    }))
    .reverse();
}

function mapPrestamoRow_(row, headers) {
  const idx = name => headers.indexOf(name);
  return {
    id: row[idx('Id_Prestamo')],
    libro: row[idx('Libro')],
    nombre: row[idx('Nombre')],
    curso: row[idx('Curso')],
    estado: row[idx('Estado')],
    fecha: row[idx('Fecha')]
  };
}

/** Solicitudes pendientes de entrega. Solo staff. */
function getSolicitudesPendientes() {
  requerirStaff_();
  const { headers, rows } = leerSheet_(SHEET_PRESTAMOS);
  const idxEstado = headers.indexOf('Estado');
  return rows
    .filter(row => row[idxEstado] === ESTADO_SOLICITADO)
    .map(row => mapPrestamoRow_(row, headers));
}

/** Préstamos entregados y todavía no devueltos. Solo staff. */
function getPrestamosActivos() {
  requerirStaff_();
  const { headers, rows } = leerSheet_(SHEET_PRESTAMOS);
  const idxEstado = headers.indexOf('Estado');
  return rows
    .filter(row => row[idxEstado] === ESTADO_ENTREGADO)
    .map(row => mapPrestamoRow_(row, headers));
}

/** Fila (1-based, con offset de encabezado) de un préstamo por su Id_Prestamo. */
function encontrarFilaPrestamo_(sheet, headers, idPrestamo) {
  const idxId = headers.indexOf('Id_Prestamo');
  const data = sheet.getDataRange().getValues();
  for (let i = 1; i < data.length; i++) {
    if (data[i][idxId] === idPrestamo) {
      return i + 1;
    }
  }
  return -1;
}

/** Confirma que el libro fue entregado en mano. Solo staff. No toca stock. */
function confirmarEntrega(idPrestamo) {
  requerirStaff_();
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_PRESTAMOS);
  const headers = sheet.getDataRange().getValues()[0];
  const rowIndex = encontrarFilaPrestamo_(sheet, headers, idPrestamo);
  if (rowIndex === -1) return { ok: false, error: 'Préstamo no encontrado.' };

  const idxEstado = headers.indexOf('Estado');
  const idxFechaEntrega = headers.indexOf('Fecha_Entrega');
  sheet.getRange(rowIndex, idxEstado + 1).setValue(ESTADO_ENTREGADO);
  sheet.getRange(rowIndex, idxFechaEntrega + 1).setValue(new Date());

  return { ok: true };
}

/**
 * Confirma la devolución física y repone el stock (único paso del ciclo que
 * devuelve stock: se descontó al Solicitar, no al Entregar). Solo staff.
 */
function confirmarDevolucion(idPrestamo) {
  requerirStaff_();
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const prestamos = ss.getSheetByName(SHEET_PRESTAMOS);
    const headersPrestamos = prestamos.getDataRange().getValues()[0];
    const rowIndex = encontrarFilaPrestamo_(prestamos, headersPrestamos, idPrestamo);
    if (rowIndex === -1) return { ok: false, error: 'Préstamo no encontrado.' };

    const idxEstado = headersPrestamos.indexOf('Estado');
    const idxFechaDevolucion = headersPrestamos.indexOf('Fecha_Devolucion');
    const idxIdLibro = headersPrestamos.indexOf('Id_Libro');
    const idLibro = prestamos.getRange(rowIndex, idxIdLibro + 1).getValue();

    prestamos.getRange(rowIndex, idxEstado + 1).setValue(ESTADO_DEVUELTO);
    prestamos.getRange(rowIndex, idxFechaDevolucion + 1).setValue(new Date());

    const libros = ss.getSheetByName(SHEET_LIBROS);
    const dataLibros = libros.getDataRange().getValues();
    const headersLibros = dataLibros[0];
    const idxIdLibroLibros = headersLibros.indexOf('Id_Libro');
    const idxCantidadTotal = headersLibros.indexOf('Cantidad_Total');
    const idxDisponibles = headersLibros.indexOf('Disponibles');
    const idxPrestado = headersLibros.indexOf('Prestado');

    for (let i = 1; i < dataLibros.length; i++) {
      if (dataLibros[i][idxIdLibroLibros] === idLibro) {
        const libroRow = i + 1;
        const cantidadTotal = Number(dataLibros[i][idxCantidadTotal]) || 0;
        const prestado = Number(dataLibros[i][idxPrestado]) || 0;
        const nuevoPrestado = Math.max(0, prestado - 1);
        libros.getRange(libroRow, idxPrestado + 1).setValue(nuevoPrestado);
        libros.getRange(libroRow, idxDisponibles + 1).setValue(cantidadTotal - nuevoPrestado);
        break;
      }
    }

    return { ok: true };
  } catch (err) {
    return { ok: false, error: err.message };
  } finally {
    lock.releaseLock();
  }
}
