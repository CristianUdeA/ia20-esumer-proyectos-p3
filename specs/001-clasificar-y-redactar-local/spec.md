# Feature Specification: Clasificación y redacción local de PQRS

**Feature Branch**: `001-clasificar-y-redactar-local`

**Created**: 2026-11-22

**Status**: Approved

**Input**: User description: "Módulo local que recibe texto libre de una PQRS (Petición, Queja, Reclamo o Sugerencia); extrae a JSON estructurado cliente, contrato, tipo, categoría, urgencia, resumen, nivel de confianza y motivo; marca para revisión manual si la confianza es baja o faltan datos; genera borrador empático con citas a fuentes oficiales (contrato, tarifas o normativa) vía RAG, y cuando no hay fuente lo marca como `sin fundamento` y envía a revisión; protege contra inyección de prompt tratando texto del cliente como dato/no instrucciones; valida con 40 PQRS sintéticas, >=85% de precisión de clasificación y cero borradores sin fundamento enviados sin revisión. Los datos personales de PQRS no se guardan en índice RAG ni registros de texto."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Clasificar una PQRS localmente (Priority: P1)

Una persona operadora entrega el texto libre de una PQRS al módulo local y recibe una extracción estructurada que facilita comprender y enrutar el caso sin volver a transcribir sus datos.

**Why this priority**: La clasificación y extracción son el resultado base que permite revisar y gestionar el caso.

**Independent Test**: Procesar PQRS sintéticas representativas de Petición, Queja, Reclamo y Sugerencia; comprobar que cada resultado es JSON válido con los campos definidos y que la clasificación alcanza el umbral medido en los 40 casos de evaluación.

**Acceptance Scenarios**:

1. **Given** una PQRS sintética con información suficiente, **When** la persona operadora solicita su clasificación, **Then** el módulo devuelve JSON válido con cliente, contrato, tipo, categoría, urgencia, resumen, nivel de confianza y motivo.
2. **Given** una PQRS con datos de cliente o contrato ausentes, **When** se extraen sus campos, **Then** el módulo representa los datos no disponibles como ausentes/nulos, no los inventa y marca el caso para revisión manual.
3. **Given** una PQRS cuyo nivel de confianza está por debajo del umbral definido, **When** se completa la clasificación, **Then** el resultado indica baja confianza y queda marcado para revisión manual antes de cualquier decisión o respuesta.

### User Story 2 - Preparar un borrador con respaldo verificable (Priority: P1)

Una persona operadora recibe un borrador de respuesta empático que puede contrastar con fuentes oficiales pertinentes antes de decidir si lo aprueba.

**Why this priority**: Un borrador útil debe ayudar a responder al cliente sin presentar como cierto algo que no esté respaldado.

**Independent Test**: Usar PQRS sintéticas y un conjunto de fuentes aprobadas; comprobar que las afirmaciones pertinentes se acompañan de citas trazables y que la ausencia de evidencia fuerza la revisión.

**Acceptance Scenarios**:

1. **Given** que hay una fuente aprobada y pertinente sobre el contrato, una tarifa o una norma aplicable, **When** se genera un borrador, **Then** el texto mantiene un tono empático e incluye referencias verificables a las fuentes que respaldan sus afirmaciones.
2. **Given** que no se recupera una fuente aprobada y pertinente, **When** se intenta preparar una respuesta, **Then** el resultado se marca exactamente como `sin fundamento`, se envía a revisión humana y no puede liberarse al cliente.
3. **Given** un borrador con citas, **When** una persona revisora lo evalúa, **Then** puede identificar las fuentes y contrastar que respaldan las afirmaciones antes de aprobar el texto final.

### User Story 3 - Mantener límites de seguridad y privacidad (Priority: P1)

La persona operadora puede procesar una PQRS sin que instrucciones maliciosas incluidas en el texto cambien las reglas del módulo ni que su contenido personal se filtre al índice de recuperación o a registros de texto.

**Why this priority**: La entrada contiene datos personales y no confiables; protegerlos y mantener el control humano son condiciones previas para usar la clasificación y los borradores.

**Independent Test**: Procesar entradas sintéticas con instrucciones de inyección, datos personales ficticios y fallos de recuperación; verificar el tratamiento como dato, la ausencia de texto personal en RAG y logs, y la ruta de revisión segura.

**Acceptance Scenarios**:

1. **Given** que el texto de una PQRS incluye instrucciones que pretenden anular reglas o solicitar una acción, **When** el módulo lo procesa, **Then** trata ese contenido exclusivamente como dato del caso, no obedece esas instrucciones y conserva las reglas de clasificación, privacidad y aprobación.
2. **Given** que se procesa una PQRS con datos personales, **When** se consulta la base de conocimiento o se generan registros operativos, **Then** los datos personales y el texto de la PQRS no se incorporan al índice RAG ni a registros de texto.
3. **Given** una respuesta que aún no tiene aprobación humana registrada, **When** se solicita liberarla al cliente, **Then** la operación se bloquea; solo puede liberarse con `aprobado_por` válido asociado al texto final exacto.

### Edge Cases

- La entrada está vacía, es ilegible o no permite identificar una PQRS: no se inventan campos y se solicita revisión manual.
- El texto contiene datos contradictorios sobre cliente, contrato, tipo o urgencia: se conserva la incertidumbre en el motivo y se escala a revisión.
- La clasificación devuelve JSON inválido, campos fuera de las opciones permitidas o una confianza faltante: no se usa como resultado confiable y se marca para revisión.
- La fuente recuperada no es aprobada, no corresponde al caso, está incompleta o no permite verificar la cita: se trata como fuente no disponible y el borrador se marca `sin fundamento`.
- La recuperación o el servicio de generación no está disponible o devuelve un resultado vacío: no se envía respuesta; se ofrece revisión manual.
- El texto intenta cambiar el nivel de confianza, forzar una categoría, extraer instrucciones internas o solicitar el envío de una respuesta: se trata como contenido no confiable y no altera los controles.
- No hay datos suficientes para redactar una respuesta específica: no se agregan hechos ni compromisos; se solicita revisión.
- Una aprobación falta, no identifica a una persona o no está asociada con el contenido exacto que se enviaría: se bloquea la liberación.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El módulo MUST aceptar texto libre correspondiente a una PQRS para procesarlo localmente.
- **FR-002**: El módulo MUST producir un objeto JSON válido con los campos `cliente`, `contrato`, `tipo`, `categoria`, `urgencia`, `resumen`, `nivel_confianza` y `motivo`. Los campos no identificables MUST representarse como ausentes o nulos, nunca completarse mediante invención.
- **FR-003**: El módulo MUST asignar tipo entre Petición, Queja, Reclamo y Sugerencia, y MUST identificar categoría y urgencia usando las opciones definidas para el servicio.
- **FR-004**: El nivel de confianza MUST expresar tanto un nivel interpretable como su motivo. Una confianza inferior a 0,70 en una escala de 0 a 1 MUST considerarse baja; los casos de baja confianza o con datos requeridos ausentes MUST quedar identificados para revisión manual.
- **FR-005**: El módulo MUST generar borradores en tono empático y solo fundamentar afirmaciones con fuentes aprobadas, pertinentes y verificables del contrato, tarifas o normativa aplicable.
- **FR-006**: Cada borrador MUST identificar sus fuentes de respaldo de forma que la persona revisora pueda verificarlas. Si no se encuentra fuente aprobada y pertinente para fundamentarlo, MUST marcarse exactamente como `sin fundamento`, enviarse a revisión humana y quedar bloqueado para liberación.
- **FR-007**: El texto de PQRS MUST tratarse como dato no confiable, nunca como instrucción capaz de reemplazar reglas, cambiar controles o autorizar acciones. Instrucciones contenidas en él MUST NOT ejecutar acciones ni alterar los criterios de clasificación o respuesta.
- **FR-008**: El texto de PQRS y sus datos personales MUST NOT incorporarse al índice RAG ni a registros de texto de la aplicación, modelo, integración o diagnóstico. Los registros operativos MUST limitarse a metadatos mínimos necesarios y no contener el texto de entrada, su resumen, datos personales ni borradores que los reproduzcan.
- **FR-009**: El módulo MUST mantener cualquier dato de caso necesario para revisión separado del índice RAG y de los registros de texto, bajo acceso controlado; los documentos de recuperación MUST ser fuentes aprobadas sin datos personales de PQRS.
- **FR-010**: Un borrador generado MUST ser consultivo y no enviarse automáticamente. Cualquier liberación a un cliente MUST bloquearse a menos que exista un `aprobado_por` válido asociado al texto final exacto que se enviará.
- **FR-011**: Ante salida inválida, datos insuficientes o contradictorios, baja confianza, ausencia de fuentes o indisponibilidad de generación o recuperación, el módulo MUST fallar de forma segura, indicar el motivo y ofrecer revisión manual sin inventar hechos, citas ni compromisos.
- **FR-012**: La evaluación de aceptación MUST usar al menos 40 PQRS sintéticas etiquetadas, cubrir las cuatro clases de tipo y medir la precisión de clasificación sobre sus etiquetas de referencia. Los datos de evaluación MUST ser sintéticos o anonimizados de forma irreversible.

### Constitution Compliance *(mandatory)*

- **CC-001 — Decisión humana y aprobación**: La clasificación y el borrador son consultivos. Casos de baja confianza, incompletos o sin fundamento requieren revisión humana. Ningún mensaje dirigido al cliente puede liberarse sin `aprobado_por` válido y vinculado al texto final exacto. Se verifica con intentos de liberación sin aprobación, aprobación ambigua y aprobación de una versión distinta; todos deben bloquearse.
- **CC-002 — Fuentes verificables**: Cada borrador respaldado incluye citas trazables a fuentes aprobadas pertinentes. Si no hay fuente verificable, se marca `sin fundamento`, se envía a revisión y no se libera como está. Se verifica con fuentes disponibles, no pertinentes, no aprobadas e inexistentes.
- **CC-003 — Privacidad**: Ningún texto de PQRS ni dato personal se agrega al RAG o a registros de texto. Se verifica con entradas sintéticas que contienen identificadores ficticios, inspeccionando los elementos de recuperación y los registros producidos, sin conservar el contenido de la prueba en dichos registros.
- **CC-004 — Fallo seguro y revisión**: Resultados inválidos, baja confianza, datos faltantes, fuentes o dependencias indisponibles, y entradas contradictorias generan un estado observable y una alternativa manual, sin envío ni afirmaciones sin respaldo.
- **CC-005 — Resistencia a instrucciones del cliente**: Entradas sintéticas que intentan anular reglas, cambiar resultados o pedir el envío de mensajes permanecen datos no confiables; las reglas de privacidad y aprobación siguen aplicándose.

### Key Entities *(include if feature involves data)*

- **PQRS**: Solicitud del cliente en texto libre, con los datos del caso necesarios para su tratamiento controlado; su texto y datos personales no son documentos de recuperación ni contenido de logs.
- **Clasificación**: Extracción estructurada de cliente, contrato, tipo, categoría, urgencia, resumen, nivel de confianza y motivo, con indicación de datos ausentes y necesidad de revisión.
- **Fuente aprobada**: Referencia a una cláusula de contrato, tarifa o disposición normativa que puede respaldar una afirmación del borrador y verificarse por una persona.
- **Borrador de respuesta**: Texto empático consultivo con referencias a fuentes o con el estado `sin fundamento`; no se libera sin aprobación.
- **Revisión y aprobación**: Evaluación humana del caso o borrador. La aprobación identifica a la persona (`aprobado_por`) y se asocia al texto final exacto antes de su eventual liberación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En un conjunto de al menos 40 PQRS sintéticas etiquetadas que incluya Peticiones, Quejas, Reclamos y Sugerencias, la precisión de clasificación global es igual o superior al 85%.
- **SC-002**: El 100% de los casos con confianza inferior a 0,70 o con datos requeridos ausentes queda señalado para revisión manual antes de que se tome una decisión sustantiva o se prepare una respuesta lista para liberar.
- **SC-003**: El 100% de los borradores con fuente aprobada verificable presenta al menos una referencia comprobable pertinente a las afirmaciones respaldadas; el 100% de los casos sin esa fuente queda marcado `sin fundamento` y encaminado a revisión.
- **SC-004**: Cero borradores marcados `sin fundamento` se liberan al cliente sin revisión humana; cero mensajes se liberan sin un `aprobado_por` válido asociado al texto final exacto.
- **SC-005**: En las pruebas de privacidad, cero textos de PQRS o datos personales sintéticos aparecen en el índice RAG o en los registros de texto producidos.
- **SC-006**: El 100% de los casos sintéticos con instrucciones de inyección mantiene el tratamiento del texto del cliente como dato y no elude revisión, privacidad ni aprobación.
- **SC-007**: Al menos el 80% de las personas revisoras califica como empático y claro el borrador fundamentado en una escala de valoración de 1 a 5, con resultados de evaluación documentados sin almacenar texto de PQRS en registros de texto.

## Assumptions

- El módulo se ejecuta localmente y no requiere que el texto de PQRS se envíe a servicios externos para clasificarlo o redactar.
- El valor de confianza se expresa de 0 a 1; para esta especificación, menos de 0,70 significa baja confianza. El umbral podrá ajustarse con evaluación aprobada, manteniendo explícito el criterio vigente.
- Las opciones oficiales de categoría y urgencia serán definidas por las personas responsables del servicio antes de evaluar el módulo; si no existen, el caso se marca para revisión en lugar de inventar opciones.
- La base RAG contiene únicamente versiones aprobadas y vigentes de fuentes oficiales aplicables y no contiene PQRS ni datos personales de clientes.
- La revisión humana precede cualquier decisión o comunicación sustantiva. El módulo prepara borradores y no incluye autorización autónoma para enviarlos.
- Las 40 o más PQRS para evaluación son sintéticas, etiquetadas y representativas de las cuatro clases de tipo; el conjunto permite calcular precisión contra etiquetas de referencia.
- Los datos del caso que sean necesarios para la operación permanecen en un registro de caso con acceso controlado, separado del índice RAG y de los registros de texto.
