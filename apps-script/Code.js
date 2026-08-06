// Bibliotech — lógica de servidor (Google Apps Script, bound a la Spreadsheet)
// Corre con el mismo login de Google del dueño de la planilla: no requiere
// cuenta de servicio, JSON de credenciales, ni secrets.toml.

const SHEET_LIBROS = 'Libros';
const SHEET_PRESTAMOS = 'Prestamos';

function doGet() {
  return HtmlService.createTemplateFromFile('Index')
    .evaluate()
    .setTitle('Bibliotech')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
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
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_LIBROS);
  const data = sheet.getDataRange().getValues();
  const headers = data.shift();
  const idxTitulo = headers.indexOf('Titulo');
  const idxAutor = headers.indexOf('Autor');
  const idxCantidadTotal = headers.indexOf('Cantidad_Total');
  const idxPrestado = headers.indexOf('Prestado');

  return data
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
 * Registra un préstamo: valida stock, incrementa "Prestado" (y refleja el
 * nuevo "Disponibles" calculado) y agrega la fila en "Prestamos". Usa
 * LockService para evitar que dos envíos simultáneos reserven el mismo
 * último ejemplar (el bug que tenía la versión Streamlit).
 */
function registrarPrestamo(datos) {
  const nombre = (datos.nombre || '').trim();
  const curso = datos.curso;
  const libro = datos.libro;

  if (!nombre || !curso || !libro) {
    return { ok: false, error: 'Completá todos los campos.' };
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
    prestamos.appendRow([new Date(), nombre, curso, idLibro, libro]);

    return { ok: true };
  } catch (err) {
    return { ok: false, error: err.message };
  } finally {
    lock.releaseLock();
  }
}
