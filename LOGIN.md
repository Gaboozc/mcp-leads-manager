# Iniciar sesión

## Credenciales de prueba

| Email | Contraseña |
|---|---|
| `operator@school.test` | `demo1234` |

Este usuario se crea automáticamente la primera vez que arranca la API. No hay que registrarse: es una herramienta interna y el enunciado pide un usuario de prueba creado al arrancar.

---

## Paso a paso

1. Levanta la API y las pantallas (ver [`SETUP.md`](SETUP.md), pasos 3 y 4).
2. Abre **http://localhost:5173** en el navegador.
3. Si no tienes sesión, la app te lleva a la pantalla **Sign in**.
4. Escribe el email y la contraseña de la tabla de arriba.
5. Pulsa **Sign in**.
6. Entras a la **bandeja** (*Inbox*), con los leads por contactar hoy.

---

## Qué puede pasar al iniciar sesión

| Lo que ves | Qué significa | Qué hacer |
|---|---|---|
| Entras a la bandeja | Todo bien | Empieza a trabajar los leads |
| *Wrong email or password.* | El email o la contraseña no coinciden | Revisa que sean exactamente los de la tabla |
| *Can't reach the server. Check that the API is running.* | La API no está encendida | Levántala con `python -m backend.app` |
| *Your session expired. Sign in again.* | Pasaron más de 8 horas o la API se reinició | Vuelve a iniciar sesión |

---

## Cómo funciona la sesión

- **Duración:** 8 horas, una jornada de trabajo.
- **Recargar la página** no cierra la sesión.
- **Cerrar sesión:** botón **Sign out**, arriba a la derecha.
- **Al caducar**, la app te devuelve a *Sign in* con un aviso.

### Por dentro (para desarrolladores)

```
Pantalla Sign in ──POST /api/auth/login {email, password}──► API Flask
                                                              │ verifica la contraseña contra el hash
                ◄──────────────── { token JWT } ─────────────┘
El token se guarda en el navegador (localStorage)
Cada petición siguiente envía:  Authorization: Bearer <token>
```

- Las contraseñas se guardan como **hash**, nunca en texto plano.
- Todas las rutas de la API, salvo el login, exigen el token.

| Archivo | Qué hace |
|---|---|
| `frontend/src/pages/SignIn.jsx` | Formulario de inicio de sesión |
| `frontend/src/auth.jsx` | Guarda el token y redirige |
| `frontend/src/api.js` | Añade el token a cada petición y detecta la sesión caducada |
| `backend/routes/auth.py` | Ruta `POST /api/auth/login` |
| `backend/services/users.py` | Verifica email y contraseña |
| `backend/seed.py` | Crea el usuario de prueba |
| `backend/config.py` | Email y contraseña de prueba, duración del token (`JWT_HOURS`) |

---

## Asistente (MCP)

El servidor MCP no pide login: lo arranca el cliente (Cursor, Claude Desktop…) en tu propia computadora. Las acciones que registra el asistente quedan a nombre del usuario indicado en la variable `OPERATOR_EMAIL` (por defecto `operator@school.test`). Ver [`SETUP.md`](SETUP.md), paso 6.

---

## Fuera de alcance

No hay registro de usuarios, recuperación de contraseña ni gestión de usuarios desde la pantalla. Hay un solo operador, creado al arrancar.
