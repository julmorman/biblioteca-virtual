# 📖 Biblioteca Virtual - Backend & Frontend

![Estado del Proyecto](https://img.shields.io/badge/status-active-success.svg)
![Versión de Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/framework-Streamlit-ff4b4b.svg)
![Licencia](https://img.shields.io/badge/license-MIT-green.svg)

Una aplicación web robusta y segura diseñada para automatizar la gestión, reserva y control de stock de libros escolares en tiempo real. Este sistema conecta una interfaz de usuario interactiva directamente con Google Sheets actuando como base de datos protegida.

**Despliegue en vivo:** [Visitar la aplicación en Streamlit](https://biblioteca-virtual.streamlit.app/)

---

## Características Principales

* ** Sincronización en Tiempo Real:** Lectura inmediata del catálogo disponible y actualización instantánea del stock tras cada reserva.
* ** Seguridad de Grado Operativo:** Conexión privada mediante Cuentas de Servicio de Google Cloud (GCP) sin exponer la base de datos de forma pública.
* ** Interfaz Optimizada (UX/UI):** Buscador predictivo de libros, validación interactiva de formularios para estudiantes y efectos visuales de confirmación.
* ** Arquitectura Limpia:** Estructura de código modular y manejo avanzado de errores para evitar pantallas caídas.

---

##  Requisitos Previos

Antes de comenzar con la instalación local, asegúrate de tener instalado en tu sistema:

* Python 3.10 o una versión superior.
* Una cuenta activa de Google Cloud Platform (para la gestión de credenciales API).
* Una copia de la plantilla de Google Sheets con las pestañas obligatorias (`Libros` y `Prestamos`).

---

##  Instalación y Configuración Local

Sigue estos pasos detallados para replicar el entorno de desarrollo en tu computadora local:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)
cd tu-repositorio

```

### 2. Crear y activar un entorno virtual (Recomendado)

```bash
# En Windows:
python -m venv venv
.\venv\Scripts\activate

# En macOS/Linux:
python3 -m venv venv
source venv/bin/activate

```

### 3. Instalar las dependencias del proyecto

```bash
pip install -r requirements.txt

```

*(Nota: Si no usas un archivo requirements.txt, puedes instalar manualmente las librerías principales ejecutando `pip install streamlit pandas streamlit-gsheets`)*.

---

##  Configuración de Variables de Entorno (Secrets)

Para que el programa pueda conectarse con la base de datos de manera local sin subir tus claves privadas a GitHub, debes configurar las credenciales locales de Streamlit.

1. Crea una carpeta llamada `.streamlit` en la raíz de tu proyecto.
2. Dentro de esa carpeta, crea un archivo llamado `secrets.toml`.
3. Pega la siguiente estructura rellenando los campos con los datos de tu archivo de Cuenta de Servicio de Google (`.json`):

```toml
[connections.gsheets]
spreadsheet = "TU_URL_DE_GOOGLE_SHEETS"
type = "service_account"
project_id = "TU_PROJECT_ID"
private_key_id = "TU_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\nTU_CLAVE_SUPER_LARGA\n-----END PRIVATE KEY-----\n"
client_email = "TU_MAIL_DE_CUENTA_DE_SERVICIO"
client_id = "TU_CLIENT_ID"
auth_uri = "[https://accounts.google.com/o/oauth2/auth](https://accounts.google.com/o/oauth2/auth)"
token_uri = "[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)"
auth_provider_x509_cert_url = "[https://www.googleapis.com/oauth2/v1/certs](https://www.googleapis.com/oauth2/v1/certs)"
client_x509_cert_url = "TU_CLIENT_X509_CERT_URL"

```

---

##  Ejecutar la Aplicación

Una vez que las credenciales locales estén cargadas en su lugar, inicia el servidor local de desarrollo ejecutando:

```bash
streamlit run app.py

```

La aplicación se abrirá de forma automática en tu navegador web en la dirección local `http://localhost:8501`.

---

##  Contribuciones y Desarrollo

¡Las sugerencias y colaboraciones son bienvenidas! Si encuentras algún error o quieres proponer una mejora en la lógica del sistema:

1. Haz un **Fork** de este repositorio.
2. Crea una rama para tu funcionalidad (`git checkout -b feature/NuevaMejora`).
3. Sube tus cambios (`git commit -m 'Add: descripción de la mejora'`).
4. Haz un **Push** a la rama (`git push origin feature/NuevaMejora`).
5. Abre un **Pull Request** detallando tus modificaciones.

---

##  Licencia

Este proyecto se encuentra bajo la Licencia MIT. Consulta el archivo `LICENSE` para obtener más detalles de manera legal.

---

*Desarrollado de forma académica enfocado en soluciones de software para la gestión escolar.*

```

Copiá este bloque completo, pegalo en el archivo `README.md` del repositorio secundario y te va a quedar impecable con el mismo diseño formal que tenías en el otro.

```
