# Guía para levantar el proyecto paso a paso

Esta guía explica cómo poner en marcha las tres piezas del proyecto en tu computadora:

1. **La API** (Flask + SQLite): guarda y sirve los datos.
2. **Las pantallas** (React): lo que usa el operador en el navegador.
3. **El servidor MCP**: lo que usa el asistente de IA en Cursor (u otro cliente MCP).

Las tres usan **la misma base de datos**, así que lo que hace una lo ven las otras.

---

## Paso 0 — Requisitos

Necesitas tener instalado:

| Programa | Versión | Cómo comprobarlo | Dónde descargarlo |
|---|---|---|---|
| Python | 3.11 o superior | `python3 --version` (Windows: `python --version`) | https://www.python.org/downloads/ |
| Node.js | 20 o superior | `node --version` | https://nodejs.org/ |
| Git | cualquiera | `git --version` | https://git-scm.com/ |

> **Windows:** al instalar Python marca la casilla **«Add Python to PATH»**.

---

## Paso 1 — Descargar el proyecto

```bash
git clone https://github.com/gaboozc/mcp-leads-manager.git
cd mcp-leads-manager
```

Todos los comandos siguientes se ejecutan **desde esta carpeta** (la raíz del proyecto), salvo cuando se indique lo contrario.

---

## Paso 2 — Preparar Python (una sola vez)

Crea un entorno virtual. Es una carpeta `.venv` con un Python propio del proyecto, para no mezclar librerías con las de tu sistema.

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Sabrás que el entorno está activo porque la terminal muestra `(.venv)` al principio de la línea.

> **Windows:** si PowerShell dice que no puede ejecutar scripts, ejecuta una vez
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a activar.

---

## Paso 3 — Levantar la API

Con el entorno activo:

```bash
python -m backend.app
```

Deberías ver algo así:

```
 * Running on http://127.0.0.1:5000
```

La primera vez, la API **crea sola la base de datos** (`backend/leads.db`) y carga los datos de ejemplo: el usuario de prueba, 3 cursos y 15 leads.

**Comprobación:** abre http://127.0.0.1:5000/api/leads en el navegador. Debe responder `{"error": "Sign in to continue."}`. Eso significa que la API funciona y que pide iniciar sesión.

**Deja esta terminal abierta.** Si la cierras, la API se apaga.

---

## Paso 4 — Levantar las pantallas

Abre **una segunda terminal** en la carpeta del proyecto:

```bash
cd frontend
npm install        # solo la primera vez
npm run dev
```

Deberías ver:

```
  ➜  Local:   http://localhost:5173/
```

Abre **http://localhost:5173** en el navegador.

> Las pantallas envían las peticiones `/api/...` a la API del paso 3. Por eso la API tiene que estar encendida al mismo tiempo.

---

## Paso 5 — Entrar

| Email | Contraseña |
|---|---|
| `operator@school.test` | `demo1234` |

Verás la bandeja con los leads de hoy. Para probar rápido:

- `↑` / `↓` cambian de lead.
- `1` a `5` registran el resultado del contacto (No answer, Call back, Interested, Not interested, Wrong number).
- `Enter` llama o abre el correo del lead seleccionado.
- `C` cambia entre teléfono y email cuando el lead tiene los dos.

---

## Paso 6 — Conectar el servidor MCP a Cursor

El servidor MCP **no se arranca a mano**: lo arranca Cursor cuando lo necesita. Solo hay que decirle dónde está.

### 6.1 Averigua la ruta absoluta del proyecto

**macOS / Linux**
```bash
pwd
```

**Windows (PowerShell)**
```powershell
(Get-Location).Path
```

Copia el resultado. En los ejemplos aparece como `/Users/tu-usuario/mcp-leads-manager`.

### 6.2 Crea el archivo de configuración

Crea la carpeta `.cursor` en la raíz del proyecto y, dentro, el archivo `mcp.json`. Reemplaza la ruta de ejemplo por la tuya en las **tres** líneas donde aparece.

**macOS / Linux**
```json
{
  "mcpServers": {
    "leads-inbox": {
      "command": "/Users/tu-usuario/mcp-leads-manager/.venv/bin/python",
      "args": ["/Users/tu-usuario/mcp-leads-manager/mcp_server/server.py"],
      "env": {
        "DATABASE_URL": "sqlite:////Users/tu-usuario/mcp-leads-manager/backend/leads.db",
        "APP_TZ": "America/New_York",
        "OPERATOR_EMAIL": "operator@school.test"
      }
    }
  }
}
```

**Windows**
```json
{
  "mcpServers": {
    "leads-inbox": {
      "command": "C:\\Users\\tu-usuario\\mcp-leads-manager\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\tu-usuario\\mcp-leads-manager\\mcp_server\\server.py"],
      "env": {
        "DATABASE_URL": "sqlite:///C:/Users/tu-usuario/mcp-leads-manager/backend/leads.db",
        "APP_TZ": "America/New_York",
        "OPERATOR_EMAIL": "operator@school.test"
      }
    }
  }
}
```

Detalles que suelen fallar:

- En macOS/Linux, `DATABASE_URL` lleva **cuatro** barras después de `sqlite:` (tres del formato más la `/` con la que empieza la ruta).
- En Windows, dentro del JSON las barras invertidas van **dobles** (`\\`).
- `command` debe apuntar al Python **de `.venv`**, no al del sistema; si no, faltarán las librerías.

### 6.3 Actívalo en Cursor

1. Abre la carpeta del proyecto en Cursor.
2. Ve a **Settings → MCP**, o **Cursor Settings → Tools & Integrations**, según la versión.
3. Debe aparecer **leads-inbox** con un punto verde y **3 tools**: `list_leads`, `get_lead` y `log_contact`.
4. Si está en rojo o gris, pulsa el botón de recargar junto al nombre.

### 6.4 Pruébalo

En el chat de Cursor (modo Agent), pregunta:

- *"Who should I contact first today?"* → usa `list_leads`.
- *"How is Ana Lopez doing?"* → usa `get_lead`.
- *"I called Emily Carter, she wants a call back on Friday"* → usa `log_contact`.

Después refresca la bandeja en el navegador: verás el mismo resultado.

> **Otros clientes MCP:** Claude Desktop y otros usan el mismo bloque `mcpServers` en su propio archivo de configuración.

### 6.5 Probar el MCP sin Cursor (opcional)

Con el **MCP Inspector** puedes invocar las tools a mano desde el navegador:

```bash
npx @modelcontextprotocol/inspector .venv/bin/python mcp_server/server.py
```

En Windows usa `.venv\Scripts\python.exe` en lugar de `.venv/bin/python`.

---

## Paso 7 — Ejecutar los tests (opcional)

Con el entorno de Python activo, desde la raíz:

```bash
pytest -q backend/tests
```

Resultado esperado: `23 passed`.

---

## Tareas frecuentes

### Volver a los datos del día 1

Las fechas de los leads de ejemplo se calculan desde el momento en que se cargan. Si pasan días, o quieres empezar de cero:

1. Detén la API (`Ctrl + C` en su terminal).
2. Ejecuta:
   ```bash
   python -m backend.seed --reset
   ```
3. Vuelve a levantar la API (paso 3).

### Apagar todo

- API: `Ctrl + C` en la terminal 1.
- Pantallas: `Ctrl + C` en la terminal 2.
- MCP: se apaga solo al cerrar Cursor.

### Volver a levantar otro día

```bash
# Terminal 1
cd mcp-leads-manager
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m backend.app

# Terminal 2
cd mcp-leads-manager/frontend
npm run dev
```

---

## Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `python3: command not found` / `python no se reconoce` | Python no está instalado o no está en el PATH | Instálalo (paso 0). En Windows usa `python` en lugar de `python3` |
| `ModuleNotFoundError: No module named 'flask'` | El entorno virtual no está activo | Activa `.venv` (paso 2) y vuelve a ejecutar |
| `Address already in use` en el puerto 5000 | Otro programa usa ese puerto (en macOS suele ser *AirPlay Receiver*) | Desactiva AirPlay Receiver en Ajustes del Sistema → General → AirDrop y Handoff, o cierra el otro programa |
| La pantalla dice *"Can't reach the server"* | La API no está encendida | Levanta la API (paso 3) en otra terminal |
| La pantalla dice *"Your session expired"* | El token caducó (dura 8 h) o la API se reinició con otra clave | Vuelve a iniciar sesión |
| `npm: command not found` | Node.js no está instalado | Instálalo (paso 0) |
| En Cursor, **leads-inbox** aparece en rojo | Ruta incorrecta en `mcp.json` o se usa el Python del sistema | Revisa que las tres rutas sean absolutas y que `command` apunte a `.venv` |
| El asistente no ve los cambios hechos en la pantalla | `DATABASE_URL` en `mcp.json` apunta a otro archivo | Debe ser exactamente `backend/leads.db` de este proyecto |
| `database is locked` | Dos procesos escriben a la vez (poco común) | Repite la acción; si persiste, reinicia la API |
| Los leads de "hoy" aparecen como de hace días | Los datos se cargaron otro día | Reinicia los datos: `python -m backend.seed --reset` |

---

## Resumen rápido

```bash
# Una sola vez
git clone https://github.com/gaboozc/mcp-leads-manager.git && cd mcp-leads-manager
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
(cd frontend && npm install)

# Cada vez
python -m backend.app              # terminal 1 → API en :5000
cd frontend && npm run dev         # terminal 2 → http://localhost:5173

# Entrar con operator@school.test / demo1234
```
