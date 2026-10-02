[🇬🇧 English](TECHNICAL.md) · 🇪🇸 Español

# Anexo técnico

Esta página es para desarrolladores. Para una explicación sencilla, lee el [README](../README.es.md). Para arrancar la app, lee [SETUP.es.md](../SETUP.es.md).

## Cómo está hecho

```
Pantalla React (Vite) ──HTTP + JWT──► Rutas Flask ──┐
                                                    ├──► backend/services/leads.py ──► SQLite
Asistente de IA (Cursor / Claude) ──stdio──► Servidor MCP ┘   (todas las reglas)
```

- **Un solo lugar para las reglas:** `backend/services/leads.py`. Las rutas de Flask y el servidor MCP solo llaman a sus funciones. Mismas validaciones, mismos mensajes, mismo efecto en la base de datos.
- **El servidor MCP no llama a la API por HTTP.** Importa `backend.services` y abre el mismo archivo SQLite (`DATABASE_URL`).
- **"Hoy" es siempre el hoy de Miami** (`APP_TZ=America/New_York`), nunca la zona horaria del reloj del servidor. Toda la lógica de fechas pasa por `backend/timeutil.py`.
- **SQLite en modo WAL**, para que la API y el servidor MCP puedan leer mientras el otro escribe.

| Capa | Tecnología |
|---|---|
| API | Flask 3, Flask-JWT-Extended, flask-cors |
| Datos | SQLAlchemy 2, SQLite (WAL) |
| MCP | SDK oficial de Python `mcp` 2.x (`MCPServer`), transporte stdio |
| Pantalla | React 19, Vite, Tailwind CSS 4, React Router |
| Pruebas | pytest |

## Carpetas

```
backend/
  app.py              App Flask, JWT, manejo de errores (puerto API_PORT, por defecto 5050)
  config.py           Ajustes compartidos por API y MCP (variables de entorno)
  db.py               Motor y sesiones (SQLite WAL, claves foráneas)
  models.py           Tablas
  seed.py             Datos del día 1, usuario de prueba, actualización de columnas en sitio
  timeutil.py         Hoy, días hábiles, etiquetas — siempre en APP_TZ
  services/leads.py   Cola, lista de contactados, detalle, log_contact, undo_contact, alta de leads
  services/courses.py Cursos con conteo de leads abiertos
  services/users.py   Comprobación de inicio de sesión
  routes/             Envoltorios REST finos (auth, courses, leads)
  tests/              pytest
mcp_server/server.py  Servidor MCP: list_leads, get_lead, log_contact
frontend/src/         Pantallas: SignIn, Inbox (pestañas, filas, botones de resultado, filtros, panel), Courses
```

## API REST

Todas las rutas salvo el login necesitan `Authorization: Bearer <token>`. Los errores siempre vuelven como `{"error": "<mensaje claro>"}`.

| Método | Ruta | Qué hace |
|---|---|---|
| `POST` | `/api/auth/login` | `{email, password}` → `{token, user}` (el token dura `JWT_HOURS`, por defecto 8) |
| `GET` | `/api/auth/me` | Usuario actual |
| `GET` | `/api/courses` | Cursos con estado y leads abiertos |
| `GET` | `/api/leads` | Cola de hoy, ordenada, más `contacted_today` y `next_return_label` |
| `GET` | `/api/leads?scope=contacted&from=AAAA-MM-DD&to=AAAA-MM-DD&by=contact\|arrival` | Leads con al menos un intento, filtrados por día del último contacto o día de llegada |
| `GET` | `/api/leads/{id}` | Un lead con sus intentos (el más nuevo primero) y "también preguntó por" |
| `POST` | `/api/leads/{id}/contacts` | **Log contact** — `{outcome, channel?, note?, follow_up_on?}` → `{lead, attempt, message}` |
| `DELETE` | `/api/leads/{id}/contacts/{attempt_id}` | Deshace el último intento del lead (dentro de 10 minutos) |
| `POST` | `/api/leads` | Alta que sustituye al formulario de la landing; los cursos en borrador rechazan leads nuevos |

## Herramientas MCP

| Herramienta | Parámetros | Devuelve |
|---|---|---|
| `list_leads` | — | Cola de hoy en orden de trabajo: id, nombre, curso, contacto, estado, llegada |
| `get_lead` | `lead_id` | Contactos, curso, estado, si está en la cola de hoy, intentos, otros cursos del mismo email |
| `log_contact` | `lead_id`, `outcome`, `channel?`, `note?`, `follow_up_on?` | Confirmación en texto claro + el nuevo detalle del lead |

Los errores se lanzan como `ToolError` con el mismo mensaje claro que muestra la pantalla. Los logs van solo a stderr (stdout es el canal JSON-RPC).

## Las reglas de «Log contact»

| Resultado | Etiqueta teléfono | Etiqueta email | Necesita | Efecto |
|---|---|---|---|---|
| `no_response` | No answer | Sent, no reply | — | Siguiente día hábil; el 3.er `no_response` → cerrado `no_response` |
| `follow_up` | Call back | Follow up | `follow_up_on` (mañana … +30 días) | Sigue abierto, vuelve ese día |
| `interested` | Interested | Interested | `note` | Cerrado `interested` (éxito) |
| `not_interested` | Not interested | Not interested | — | Cerrado `not_interested` |
| `bad_contact` | Wrong number | Bounced | — | Marca ese canal como inválido; si queda otro canal válido → sigue abierto, para hoy; si no → cerrado `unreachable` |

**Validaciones** (iguales en REST y MCP): el lead debe existir, estar abierto y tener válido el canal elegido; el resultado debe ser uno de los cinco; nota de 280 caracteres como máximo.

**Cola de hoy:** `status = open` y (`next_contact_on` vacío o ≤ hoy). Orden: seguimientos prometidos que vencen → leads nuevos (el más nuevo primero) → reintentos (menos intentos primero). Los leads sin teléfono se trabajan por email en el mismo orden.

**Deshacer:** cada intento guarda `prev_state` (estado, próxima fecha, motivo de cierre y marcas de canal del lead antes del intento). Deshacer borra el intento y restaura ese estado. Solo el último intento del lead, dentro de 10 minutos.

**Alta de leads:** un curso en borrador rechaza leads nuevos (`«…» is a draft and is not accepting new leads.`).

## Modelo de datos

**Base (del brief):**

- `users(id, email, name, password_hash)`
- `courses(id, name, slug UNIQUE, area, status: published|draft)`
- `leads(id, name, email, phone NULL, course_id, created_at)`

**Lo que agrega la funcionalidad inventada:**

- En `leads`: `status` (open|closed), `next_contact_on`, `closed_reason` (interested|not_interested|no_response|unreachable), `phone_invalid`, `email_invalid`
- Tabla nueva `contact_attempts(id, lead_id, user_id, channel, outcome, note, follow_up_on, created_at, prev_state)`

Las fechas se guardan en UTC y se muestran en `APP_TZ`. A las bases de datos creadas antes de Deshacer se les agrega la columna `prev_state` automáticamente al arrancar.

## Variables de entorno

| Variable | La usa | Por defecto | Para qué |
|---|---|---|---|
| `DATABASE_URL` | API + MCP | `sqlite:///backend/leads.db` | Las dos deben apuntar al mismo archivo |
| `APP_TZ` | API + MCP | `America/New_York` | Qué significa "hoy" |
| `API_PORT` | API + pantalla | `5050` | Puerto de la API (se evita el 5000: macOS lo usa) |
| `JWT_SECRET_KEY` | API | valor de desarrollo | Cámbiala en producción |
| `JWT_HOURS` | API | `8` | Duración de la sesión |
| `OPERATOR_EMAIL` | MCP | `operator@school.test` | A nombre de quién quedan los intentos registrados por el asistente |

## Pruebas

```bash
pytest -q backend/tests     # 34 passed
```

Cubren los datos del día 1, cada regla y mensaje de «Log contact», el orden de la cola, la lista de contactados y sus filtros, deshacer, la API y las herramientas MCP (mismo efecto en la base de datos que la pantalla).

## Más

- [docs/WORKFLOW.md](WORKFLOW.md) — notas completas de diseño (en inglés): flujos paso a paso y comparación con Close, Folk, Attio y LeadSquared.
