[🇬🇧 English](README.md) · 🇪🇸 Español

# Leads Inbox (Bandeja de leads)

## ¿Qué es esto?

Una escuela vende cursos cortos. Las personas que quieren un curso dejan su nombre y su teléfono en una página web.

Cada mañana, una persona de marketing tiene que llamarlas. A esa persona la llamamos **el operador**.

Esta app es la lista de tareas del operador para esas llamadas. También trae un ayudante con el que puedes chatear (un **asistente de IA**) que ve la misma lista.

> **¿Qué significa esta palabra?**
> - **Lead:** una persona que preguntó por un curso. "Ana preguntó por Enfermería" es un lead.
> - **Cola:** la lista de leads para llamar hoy, en orden.
> - **Asistente de IA:** un programa de chat (como Claude o Cursor) que puede leer y actualizar la lista por ti.

**Para instalarla y arrancarla, lee [SETUP.es.md](SETUP.es.md).** Si eres desarrollador, todos los detalles técnicos están en [docs/TECNICO.md](docs/TECNICO.md).

> La pantalla de la app está en inglés. Aquí te explicamos cada botón en español.

---

## ¿Cómo es una mañana?

Son las 9:00. Hay 40 personas para llamar y una hora.

1. El operador abre la app y entra con su usuario.
2. La lista muestra a quién llamar primero. La app ya las puso en orden.
3. El operador llama a la primera persona.
4. Después de la llamada, pulsa un botón para decir qué pasó.
5. Esa persona sale de la lista de hoy y la siguiente queda lista.
6. Se repite hasta que la lista queda vacía. 🎉

---

## ¿Qué hay en la pantalla?

![La bandeja](docs/img/inbox-outcome-bar.png)

**Arriba hay dos pestañas:**

- **To contact** (por contactar): las personas para llamar hoy. El número dice cuántas quedan.
- **Contacted** (contactados): las personas con las que ya hablaste. Las que nadie ha llamado todavía nunca aparecen aquí.

**Cada persona de la lista muestra:**

- su nombre y el curso que le interesa
- cuándo preguntó ("2 h ago" = hace 2 horas)
- su teléfono, o su email si no tiene teléfono

Haz clic en el teléfono para llamar. Haz clic en el email para escribirle.

**A la derecha** ves todo sobre la persona seleccionada, incluidas todas las llamadas que se le han hecho.

### Los cinco botones

Después de una llamada, pulsa el botón de lo que pasó. También puedes pulsar la tecla del número.

| Tecla | Botón | Color | Qué pasa después |
|---|---|---|---|
| `1` | **No answer** (no contesta) | gris | La persona vuelve a la lista el siguiente día hábil. Después de 3 intentos sin respuesta, paramos. |
| `2` | **Call back** (volver a llamar) | amarillo | Pidió que la llames otro día. Tú eliges el día. |
| `3` | **Interested** (interesado) | verde | 🎉 Quiere el curso. Escribes una nota corta. ¡Listo! |
| `4` | **Not interested** (no le interesa) | rojo | Dijo que no. Listo. |
| `5` | **Wrong number** (número equivocado) | negro | Ese número está mal. Si tenemos su email, probamos por email. |

Si la persona no tiene teléfono, los botones dicen "Sent, no reply" (enviado, sin respuesta), "Follow up" (dar seguimiento) y "Bounced" (el email rebotó), porque la contactas por email.

**Los colores siempre son los mismos.** Amarillo siempre es "volver a llamar", verde siempre es "interesado", y así con todos. Así entiendes lo que pasó con solo mirar.

### ¿Te equivocaste? Pulsa Undo

Al pulsar un botón aparece un mensaje verde con un botón **Undo** (deshacer). Púlsalo (o `Ctrl + Z`) y todo vuelve a como estaba.

![Guardado, con Undo](docs/img/saved-undo.png)

También puedes deshacer desde la pestaña **Contacted**. Deshacer funciona durante 10 minutos, y solo con lo último que hiciste con esa persona.

### La pestaña «Contacted»

Aquí ves a todas las personas con las que ya hablaste, con el color de lo que pasó.

![Pestaña Contacted](docs/img/contacted-tab.png)

Puedes buscar por fecha: **Today** (hoy), **Yesterday** (ayer), **Last 7 days** (últimos 7 días), **All time** (todo), o elegir un día. Puedes elegir buscar por el día en que la contactaste o por el día en que preguntó por el curso.

---

## La funcionalidad que inventé

### ¿Qué problema resuelve?

A las 9:00 hay 40 personas y una hora. Por cada persona, el operador tiene que acordarse de tres cosas:

- ¿La pude contactar?
- ¿Qué me dijo?
- ¿Cuándo vuelvo a intentarlo?

Sin ayuda, eso queda en papel. A algunas personas se las llama dos veces. Se olvidan las promesas de volver a llamar. Las personas sin teléfono se quedan sin contactar.

### ¿Qué hace?

Se llama **Log contact** (registrar contacto). Después de cada llamada o email, el operador pulsa uno de los cinco botones. La app decide sola el siguiente paso:

- **No contesta:** se reintenta el siguiente día hábil. Se para después de 3 intentos.
- **Volver a llamar:** vuelve el día que eligió el operador.
- **Interesado:** se cierra como éxito, con una nota.
- **No le interesa:** se cierra.
- **Número equivocado:** si hay email, la persona se queda y se pasa a email. Si no hay otra forma de contactarla, se cierra.

**La regla es simple: mientras haya una forma de contactar a alguien, seguimos intentando.**

Cada llamada se guarda. Si recargas la página, todo sigue ahí.

### El asistente de IA también puede hacerlo

El asistente tiene tres herramientas:

- **list_leads** muestra la lista de hoy.
- **get_lead** muestra una persona.
- **log_contact** hace lo mismo que los cinco botones.

Las reglas viven en **un solo lugar** del servidor. La pantalla y el asistente usan ese mismo lugar. Por eso siempre coinciden.

### ¿Qué otra cosa pensé?

Pensé en un **paso de ordenar por la mañana**: antes de llamar, el operador clasifica cada lead en "alta", "normal", "después" o "basura".

No lo elegí por tres razones:

1. Necesita una segunda pantalla, y la tarea pedía un solo trabajo dentro de la bandeja.
2. Sobre todo cambia el orden de la lista, y la tarea dice que eso no alcanza.
3. No responde "¿qué pasó con la llamada?".

Me quedé con su mejor idea: **la app ordena la lista por ti**. Primero las personas a las que prometiste llamar, luego las más nuevas y después los reintentos.

### ¿Por qué esta?

Porque es la que más pasos ahorra a las 9:00. Una tecla por persona, en vez de abrir una página, escribir una nota y poner un recordatorio. Y nadie se pierde solo porque un teléfono estaba mal.

### Comprobación 1: de la pantalla al asistente

1. En la pantalla, sobre **Ana Lopez** (Enfermería), pulsé **No answer**. Salió de la lista de hoy.
2. Luego le pregunté al asistente: *"How is Ana Lopez doing? The nursing lead."* (¿Cómo va Ana Lopez, la de enfermería?)

**Lo que el asistente respondió de verdad** (en inglés, tal cual):

> Ana Lopez (#1, Certified Nursing Assistant) is scheduled for a retry tomorrow, Friday Oct 2, so she's not in today's queue. Her lead came in about 40 minutes ago, and there's been one attempt so far: a call at 9:17 PM tonight that went unanswered. Her contact details are phone 305-555-0142 and email ana.lopez@mail.com.
>
> There's also a second Ana Lopez entry, #6, for Intro to Python. It uses the same phone number, arrived yesterday, and is still sitting as "New" in today's queue. Lead #1 also notes that she asked about Intro to Python, so #6 is probably the same person. If that's right, calling #6 today would mean contacting her twice: once today and again tomorrow. You might want to merge the two entries or skip #6 and handle both courses in tomorrow's call.

En pocas palabras: Ana tiene un intento sin respuesta, ya no está en la lista de hoy y vuelve el viernes 2 de octubre.

✅ El asistente vio lo que guardé en la pantalla.

### Comprobación 2: del asistente a la pantalla

1. Le dije al asistente: *"I called Luis Perez, he asked me to call him back on Friday, October 9 after 6 pm."* (Llamé a Luis Perez, me pidió que lo llame el viernes 9 de octubre después de las 6 pm.)

**Lo que el asistente respondió de verdad** (en inglés, tal cual):

> Logged. Luis Perez (Intro to Python) is scheduled for a callback on Friday, Oct 9, with a note that he asked for a call after 6 pm, and he's off today's queue.
>
> Next up is Marta Ruiz (#3, Intro to Python). She's email only, at marta.ruiz@mail.com.

En pocas palabras: quedó guardado volver a llamar a Luis el viernes 9, con la nota, y ya no está en la lista de hoy.

2. Recargué la pantalla. Luis ya no estaba en la lista de hoy. Aparecía como **"Scheduled · back on Fri, Oct 9"** (programado, vuelve el viernes 9). Ana aparecía como **"Scheduled · back on Fri, Oct 2"** por la comprobación 1.

![Las dos comprobaciones en la pantalla](docs/img/checks-all-view.png)

*(Esta imagen es de una versión anterior, donde la pestaña se llamaba "All". Hoy es la pestaña **Contacted**.)*

✅ La pantalla mostró lo que guardó el asistente.

---

## ¿Cómo se guarda la información?

**Lo que pedía la tarea (la base):**

- **Usuarios:** email, nombre y contraseña (guardada de forma segura, cifrada).
- **Cursos:** nombre, nombre corto para la web ("slug"), área y estado (publicado o borrador).
- **Leads:** nombre, email, teléfono (puede estar vacío), curso y la fecha en que preguntó.

Dos leads con el mismo email quedan como dos leads separados. La tarea no dice si son la misma persona, así que la app solo muestra un aviso: "Also asked about…" (también preguntó por…).

**Lo que agrega mi funcionalidad:**

- **En cada lead**, cinco datos nuevos:
  - ¿Está abierto o cerrado?
  - ¿Cuándo volvemos a intentar?
  - ¿Por qué se cerró?
  - ¿El teléfono estaba mal?
  - ¿El email estaba mal?
- **Una lista nueva de intentos de contacto.** Una línea por cada llamada o email. Cada línea dice:
  - quién lo hizo, y cuándo
  - qué pasó, y una nota
  - cómo estaba el lead antes (para poder deshacerlo)

---

## ¿Qué quedó fuera?

**De la base:**

- Las páginas web públicas de los cursos. La tarea dijo que no se construyeran.
- Crear más usuarios desde la app. Hay un usuario de prueba.

**De mi funcionalidad:**

- La app no hace llamadas reales ni envía emails. Abre tu app de teléfono o de correo.
- No hay marcado automático.
- Deshacer solo funciona durante 10 minutos, con la última acción de cada persona.
- El asistente no puede deshacer. La tarea permitía una sola herramienta extra.
- No se saltan los feriados de Estados Unidos al contar días hábiles.

---

## Más documentos

| Documento | Para qué sirve |
|---|---|
| [SETUP.es.md](SETUP.es.md) | Instalar, arrancar, entrar y conectar el asistente, paso a paso |
| [docs/TECNICO.md](docs/TECNICO.md) | Para desarrolladores: cómo está hecho, API, reglas, datos, pruebas |
| [docs/WORKFLOW.md](docs/WORKFLOW.md) | Notas completas de diseño, con comparación contra otras herramientas (en inglés) |
