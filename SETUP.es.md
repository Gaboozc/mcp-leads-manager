[🇬🇧 English](SETUP.md) · 🇪🇸 Español

# Cómo arrancar la app, paso a paso

Esta guía tiene 4 partes:

1. [Preparar todo (una sola vez)](#parte-1--preparar-todo-una-sola-vez)
2. [Arrancar la app](#parte-2--arrancar-la-app)
3. [Entrar](#parte-3--entrar)
4. [Conectar el asistente de IA](#parte-4--conectar-el-asistente-de-ia)

Si algo falla, ve a [Si algo sale mal](#si-algo-sale-mal).

> **¿Qué significa esta palabra?**
> - **Terminal:** una ventana donde escribes comandos. En Windows se llama **PowerShell**. En Mac se llama **Terminal**.
> - **API:** la parte de la app que guarda los datos y las reglas. No la ves; la pantalla habla con ella.
> - **Pantalla:** la parte que ves en el navegador.

---

## Parte 1 — Preparar todo (una sola vez)

### Paso 1. Instala tres programas

| Programa | Dónde conseguirlo | Cómo comprobar que funciona |
|---|---|---|
| Python 3.11 o más nuevo | https://www.python.org/downloads/ | escribe `python --version` |
| Node.js 20 o más nuevo | https://nodejs.org/ | escribe `node --version` |
| Git | https://git-scm.com/ | escribe `git --version` |

En Windows, al instalar Python, marca la casilla **"Add Python to PATH"**.

**Lo que verás:** cada comprobación muestra un número de versión, como `Python 3.12.4`.

### Paso 2. Descarga el proyecto

Abre una terminal y escribe:

```bash
git clone https://github.com/gaboozc/mcp-leads-manager.git
cd mcp-leads-manager
```

**Lo que verás:** una carpeta nueva llamada `mcp-leads-manager`. A partir de ahora, trabaja siempre dentro de ella.

### Paso 3. Prepara Python

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Mac:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Lo que verás:** la línea empieza con `(.venv)` y la instalación termina con `Successfully installed ...`.

Si Windows dice que los scripts están deshabilitados, escribe esto una vez y vuelve a intentarlo:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### Paso 4. Prepara la pantalla

```bash
cd frontend
npm install
cd ..
```

**Lo que verás:** tarda uno o dos minutos. Los avisos en amarillo son normales.

---

## Parte 2 — Arrancar la app

Necesitas **dos terminales abiertas a la vez**: una para la API y otra para la pantalla.

### Paso 5. Terminal 1: arranca la API

Dentro de la carpeta del proyecto:

**Windows:** `.venv\Scripts\Activate.ps1` · **Mac:** `source .venv/bin/activate`

Luego:

```bash
python -m backend.app
```

**Lo que verás:** `Running on http://127.0.0.1:5050`.

La primera vez, la app crea sola los datos de ejemplo: 1 usuario, 3 cursos y 15 leads.

**Deja esta ventana abierta.** Si la cierras, la app se apaga.

### Paso 6. Terminal 2: arranca la pantalla

Abre una terminal **nueva**, ve a la carpeta del proyecto y escribe:

```bash
cd frontend
npm run dev
```

**Lo que verás:** `Local: http://localhost:5173/`.

**Deja esta ventana abierta también.**

---

## Parte 3 — Entrar

### Paso 7. Abre la app

Abre **http://localhost:5173** en tu navegador.

### Paso 8. Escribe el usuario de prueba

| Email | Contraseña |
|---|---|
| `operator@school.test` | `demo1234` |

Pulsa **Sign in** (entrar).

**Lo que verás:** la bandeja, con "15 to contact today" (15 por contactar hoy).

### ¿Qué puede pasar al entrar?

| Ves | Qué significa | Qué hacer |
|---|---|---|
| La bandeja | Funcionó 🎉 | Empieza a trabajar |
| *Wrong email or password.* | Hay un error al escribir | Escríbelos otra vez, exactamente como arriba |
| *Can't reach the API…* | La terminal 1 no está corriendo | Arráncala otra vez (paso 5) |
| *Your session expired. Sign in again.* | Pasaron más de 8 horas, o la API se reinició | Entra otra vez |

**Bueno saber:**

- La sesión dura 8 horas, aunque recargues la página.
- Para salir, pulsa **Sign out** (arriba a la derecha).
- No hay página para registrarse. Es una herramienta interna: las cuentas las crea quien la administra. Para la prueba hay un solo usuario.

---

## Parte 4 — Conectar el asistente de IA

El asistente (Claude Desktop o Cursor) arranca solo nuestro programa ayudante. Solo tienes que decirle dónde está.

### Paso 9. Copia la ruta de la carpeta

**Windows:** `(Get-Location).Path` · **Mac:** `pwd`

**Lo que verás:** algo como `C:\Users\tu-usuario\mcp-leads-manager` o `/Users/tu-usuario/mcp-leads-manager`. Cópialo.

### Paso 10a. Con Claude Desktop

1. Abre Claude Desktop → **Settings** → **Developer** → **Edit Config**.
2. Se abre un archivo llamado `claude_desktop_config.json`. Ábrelo con el Bloc de notas (Windows) o TextEdit (Mac).
3. Agrega este bloque **arriba, justo después de la primera `{`**. No borres nada de lo que ya tenga. Cambia `tu-usuario` por tu carpeta real.

**Windows:**

```json
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
  },
```

**Mac:**

```json
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
  },
```

Si el archivo estaba vacío, pon `{` antes del bloque y `}` después, y quita la última coma.

4. Guarda. Puedes pegar todo el archivo en https://jsonlint.com para comprobar que dice **"Valid JSON"**.
5. **Cierra Claude Desktop por completo.** En Windows: flechita junto al reloj → clic derecho en Claude → **Quit**. Luego ábrelo otra vez.
6. Ve a **Settings → Developer**.

**Lo que verás:** **leads-inbox** con la palabra **Running** (funcionando).

### Paso 10b. Con Cursor

Crea una carpeta `.cursor` dentro del proyecto y, dentro, un archivo `mcp.json`. Pon el mismo bloque, entre `{ }`. Luego ve a **Cursor Settings → MCP**.

**Lo que verás:** **leads-inbox** con un punto verde y 3 herramientas.

### Paso 11. Pruébalo

En un **chat nuevo**, escribe: *"Who should I contact first today?"* (¿A quién debo contactar primero hoy?)

Cuando pida permiso para usar la herramienta, pulsa **Allow** (permitir).

**Lo que verás:** el asistente responde con la lista de hoy, empezando por Ana Lopez.

**Consejos:**

- Abre un **chat nuevo** para cada prueba. En un chat viejo, el asistente recuerda respuestas viejas.
- El asistente pide permiso antes de guardar algo. Pulsa **Allow** rápido, o la petición vence.
- Mientras usas el asistente, no escribas en la pestaña del navegador de la app. Ahí los números `1` a `5` son atajos y guardarían resultados.

---

## Tareas de todos los días

**Empezar otra vez con datos de ejemplo nuevos** (útil si pasaron días):

1. Detén la API (`Ctrl + C` en la terminal 1).
2. Escribe `python -m backend.seed --reset`
3. Arranca la API otra vez (paso 5).

**Traer la última versión del proyecto:**

1. `git pull`
2. Reinicia la API (`Ctrl + C` y luego `python -m backend.app`).
3. Reinicia la pantalla (`Ctrl + C` y luego `npm run dev`) y recarga el navegador con `Ctrl + F5`.

**Correr las pruebas automáticas:** `pytest -q backend/tests`. Deberías ver `34 passed`.

---

## Si algo sale mal

| Lo que ves | Por qué | Cómo arreglarlo |
|---|---|---|
| `python no se reconoce` | Falta Python, o no está en el PATH | Instálalo (paso 1) y marca "Add Python to PATH" |
| `No module named 'flask'` | El `(.venv)` no está activo | Actívalo (paso 3) |
| `No time zone found with key America/New_York` | A Windows le faltan los datos de zonas horarias | Ejecuta otra vez `pip install -r requirements.txt` |
| `Address already in use` | Otro programa usa el puerto 5050 | Ciérralo, o usa otro puerto: `API_PORT=5051` antes de los dos comandos (Windows: `$env:API_PORT=5051`) |
| La página queda toda en blanco | El navegador guardó una copia vieja | Detén la pantalla, borra la carpeta `frontend/node_modules/.vite`, ejecuta `npm run dev` y recarga con `Ctrl + F5` |
| *Can't reach the API…* | La terminal 1 no está corriendo | Arráncala (paso 5) |
| Claude/Cursor muestra leads-inbox en rojo | Una ruta de la configuración está mal | Revisa las 3 rutas, y que `command` apunte al Python dentro de `.venv` |
| El asistente no ve lo que guardaste | `DATABASE_URL` apunta a otro archivo | Debe ser el `backend/leads.db` de este proyecto |
| Los leads de "hoy" se ven viejos | Los datos de ejemplo se crearon hace días | Empieza otra vez con datos nuevos (ver Tareas de todos los días) |
