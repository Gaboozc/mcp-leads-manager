# Prueba técnica — Bandeja de leads de cursos

## Índice

- [Enunciado](#enunciado)
- [Glosario del modelo de negocio](#glosario-del-modelo-de-negocio)

## Enunciado

**Prueba técnica — Bandeja de leads de cursos**

Tienes 48 horas desde que recibes este enunciado. Está pensada para unas 6–8 horas de trabajo dentro de ese plazo.

A las 24 horas puedes pedir una llamada de 30 minutos si estás bloqueado. Trae una pregunta concreta (algo que no arranca, una duda de alcance, una decisión que no puedes cerrar). En esa llamada se aclara el enunciado y se desbloquea el camino. No se diseña la solución ni se escribe código.

La entrega tiene dos partes. Las dos se califican. La segunda no sustituye a la primera, y la primera sin la segunda queda incompleta.


| Parte                         | Qué es                                                           | Quién la define                   |
| ----------------------------- | ---------------------------------------------------------------- | --------------------------------- |
| 1. La base                    | Login, cursos, bandeja de leads, API y el MCP que lee esos datos | Este enunciado. Está cerrada.     |
| 2. La funcionalidad inventada | Una acción de trabajo que la base no trae                        | Tú. El enunciado no dice cuál es. |


Una escuela de educación continua publica una landing por curso. La gente deja sus datos en un formulario. Quien trabaja marketing abre una herramienta interna cada mañana y decide a quién llamar. Además, usa un asistente de IA conectado a esa misma información.

No construyas el sitio público.

### Parte 1 — La base

Esto es lo pedido. Constrúyelo tal como está escrito. Aquí no se inventa comportamiento.

**Datos que ya existen el día 1**

Tres cursos, con nombre, slug y área (por ejemplo Salud, Tecnología, Negocios). Dos publicados y uno en borrador. El borrador no debería recibir leads nuevos.

Unos 15 leads de ejemplo, repartidos en varios días. Cada lead tiene nombre, email, teléfono opcional, curso de interés y fecha. Incluye a propósito:

- dos leads con el mismo email en cursos distintos
- dos leads sin teléfono
- un lead sobre el curso en borrador (llegó antes de pasarlo a borrador)
- varios leads de hoy y varios de la semana pasada

**Herramienta interna**

1. Un operador entra con email y contraseña. La sesión usa JWT. Hay un usuario de prueba creado al arrancar.
2. Ve la lista de cursos y el estado (publicado o borrador).
3. Ve la bandeja de leads y puede abrir uno.
4. API REST en Flask y base de datos SQL (PostgreSQL o SQLite). Pantallas en React.

**MCP de la base**

Un servidor MCP en Python, transporte stdio, sobre la misma base de datos. Sin OAuth y sin servidor HTTP. Referencia del protocolo: [https://modelcontextprotocol.io](https://modelcontextprotocol.io)

Dos tools de lectura, y nada más en esta parte:

1. **Lista de leads.** Devuelve la bandeja.
2. **Detalle de un lead.** Devuelve un lead.

Cada tool devuelve solo lo que el asistente necesita para seguir. Si algo falla, el mensaje dice qué pasó en lenguaje claro.

En el README, cómo conectar el servidor a Cursor (u otro cliente MCP).

### Parte 2 — La funcionalidad inventada

Esta parte es aparte de la base. La base ya deja al operador entrar, ver cursos y ver leads. Eso no cuenta como invención.

Encima de esa base, inventa una acción de trabajo que este enunciado no describe. Es lo que la persona de marketing puede hacer con uno o mas leads o con la bandeja entera, cuando son las 9:00, hay 40 leads y tiene una hora para llamar. Tú decides cuál es.

En el README, una sección titulada «La funcionalidad que inventé», separada de la base. Ahí escribes qué problema resuelve, qué otra acción consideraste y por qué te quedaste con esta.

Tiene que cumplir:

1. **Se guarda.** Al recargar la página, el resultado sigue ahí. Un filtro o un ordenador de columna se pierden al recargar.
2. **Es un solo trabajo, no un módulo nuevo.** Se empieza en la bandeja y se termina sin abrir otra sección de la herramienta. Nada de menú propio, varias pantallas o un pipeline aparte.

Dentro de ese trabajo puede haber más de un control. Muchos controles no mejoran la calificación, un solo control puede ser suficiente para facilitar el trabajo a un agente de marketing.

«Posponer un lead para el viernes y sacarlo de la lista de hoy» marca el tamaño que no alcanza. Una sola casilla que cambia un estado no cuenta.

Tampoco cuentan el modo oscuro, exportar CSV, un buscador, un gráfico, ni un chat de IA pegado al lado de la bandeja. Esas cosas pueden acompañar la entrega, y siguen sin ser la funcionalidad inventada.

**El mismo trabajo en React y en el MCP**

El trabajo vive una sola vez en el servidor. El frontend y el MCP solo lo llaman. No es una mejora de funcionalidad por un lado y un MCP que sigue tools por el otro.

A las dos tools de la base se suma una tercera, y solo una:

1. **El trabajo.** Ejecuta el mismo trabajo que la pantalla. Mismos campos, mismas validaciones, mismo efecto en la base de datos. Si en la pantalla hay modo, acción y comentario, la tool recibe esos campos. No hace falta una tool por cada botón del recorrido.

Si el operador avanza varios leads, la tool se aplica a un lead cada vez, igual que cada paso de la pantalla. El asistente puede repetirla.

Las dos tools de lectura de la base pasan a mostrar el resultado de ese trabajo. Si el trabajo saca un lead de la lista de hoy, la tool de lista no lo devuelve, y la tool de detalle dice en qué estado quedó.

Compruébalo en los dos sentidos y déjalo escrito en «La funcionalidad que inventé», con la respuesta real del asistente:

- Desde la pantalla, ejecutas la acción y luego pides al asistente el detalle de ese lead: el asistente responde con el resultado ya guardado.
- Desde el asistente, ejecutas la misma acción y refrescas la pantalla: la pantalla muestra el mismo resultado.

**Interfaz: se califica la creatividad**

La interfaz entra en la nota, en la base y en la acción inventada. Quien trabaja marketing tiene que entender qué hace cada cosa con solo ver la pantalla, sin un tutorial y sin que se lo expliques.

Se valora una interfaz limpia, moderna y minimalista: poco texto, poco ruido, y cada elemento con un trabajo claro. Un panel lleno de etiquetas técnicas, bordes y botones iguales no suma, aunque los datos estén bien.

También se califican las herramientas que le facilitan el trabajo. Cuanto más le ahorren pasos a la persona de marketing, mejor. Entran aquí:

- El cursor dice qué se puede hacer: puntero en lo que se pulsa, mano o agarre si algo se arrastra, y un cursor distinto donde no hay acción.
- Lo clickable responde al pasar el cursor (hover) y al pulsar, sin mover el resto de la página.
- Vacío, error de login y lead sin teléfono se leen en la propia pantalla.

**Entrega**

- Repositorio con README partido en dos: cómo arrancar la base (app, MCP, usuario de prueba) y, en otra sección, «La funcionalidad que inventé» con el ejemplo de las dos comprobaciones.
- Decisiones de modelo de datos en pocas frases, diciendo qué campos son de la base y qué campo o tabla agrega la acción inventada.
- Interfaz en lenguaje de operador, limpia y entendible con solo verla. Quien la usa no es un desarrollador.

**Límites**

- Si algo queda fuera, dilo en el README, indicando si falta de la base o de la funcionalidad inventada.
- Puedes usar librerías, incluido un SDK de MCP.
- La interfaz puede estar en español o en inglés.
- Una entrega que solo tiene la Parte 1 está incompleta. Una entrega cuya «funcionalidad inventada» es otro listado de leads también está incompleta.

## Glosario del modelo de negocio

Estas definiciones fijan el negocio de la prueba. No amplían la Parte 1 y no indican cuál es la acción de la Parte 2.


| Término                         | Qué es en este negocio                                                                                                                                                                                                                                                  |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Educación continua              | Escuela que ofrece cursos cortos a adultos: un oficio, un certificado o una actualización. No es una carrera de varios años. Cada curso se publica y se trabaja por separado.                                                                                           |
| Curso                           | La oferta concreta. Tiene nombre, slug y área. Es lo que la persona elige al dejar sus datos. En la herramienta interna se ve si está publicado o en borrador.                                                                                                          |
| Área                            | Familia del catálogo, por ejemplo Salud, Tecnología o Negocios. Sirve para saber de qué tipo es el curso. No es un lead ni un estado.                                                                                                                                   |
| Slug                            | Identificador corto y estable del curso, el que iría en la dirección de su página. Distingue dos cursos aunque el nombre visible se parezca.                                                                                                                            |
| Publicado                       | El curso está a la vista del público y puede recibir leads nuevos.                                                                                                                                                                                                      |
| Borrador                        | El curso no se está ofreciendo. No debería recibir leads nuevos. Puede conservar leads antiguos, de cuando todavía estaba publicado.                                                                                                                                    |
| Landing                         | Página pública de un solo curso, donde vive el formulario. No hay que construirla: los leads de ejemplo ya existen como si esa página hubiera estado en marcha.                                                                                                         |
|                                 |                                                                                                                                                                                                                                                                         |
| Lead                            | Un interés registrado: alguien dejó sus datos por un curso, en una fecha. No es un alumno inscrito ni un pago. Es la unidad de trabajo del operador.                                                                                                                    |
| Curso de interés                | El curso por el que se creó ese lead. Un lead apunta a un curso.                                                                                                                                                                                                        |
| Mismo email en cursos distintos | La misma dirección puede aparecer en más de un lead. En el negocio es interés repetido o interés en ofertas distintas. Los dos registros se guardan. El enunciado no dice si son una sola persona.                                                                      |
|                                 |                                                                                                                                                                                                                                                                         |
| Fecha del lead                  | Cuándo llegó el interés. La bandeja mezcla leads de hoy con leads de días anteriores, porque el operador trabaja una mañana concreta.                                                                                                                                   |
| Bandeja                         | La lista de leads que marketing abre para decidir a quién contactar. Es la herramienta interna, no el sitio público.                                                                                                                                                    |
| Operador                        | La persona de marketing. Entra con email y contraseña y usa la bandeja para trabajar. No es quien desarrolla la herramienta: entiende curso, borrador y a quién llamar, no el nombre interno del sistema.                                                               |
| Asistente                       | El mismo operador también consulta un asistente de IA unido a los mismos cursos y los mismos leads. Lo que la pantalla guarda, el asistente lo ve. Lo que el asistente hace, la pantalla lo muestra al refrescar. No es otro catálogo ni una copia aparte de los datos. |


