<!--
Informe de impacto de sincronización
- Cambio de versión: plantilla inicial sin versión → 1.0.0 (primera adopción;
  establece gobernanza verificable para el proyecto).
- Principios establecidos: desarrollo guiado por especificaciones; la IA propone
  y la persona decide; diseño para el fallo; aprobación registrada en
  aprobado_por; borradores con fuentes verificables; privacidad por diseño.
- Secciones añadidas: restricciones del proyecto; flujo de entrega y verificación.
- Secciones eliminadas: ninguna.
- Artefactos sincronizados: .specify/templates/constitution-template.md,
  .specify/templates/plan-template.md, .specify/templates/spec-template.md,
  .specify/templates/tasks-template.md, README.md, ficha-tecnica.md.
- Comandos: no existe .specify/templates/commands/; las instrucciones Spec Kit
  disponibles usan nombres genéricos speckit.* y no requieren cambios.
- Pendiente: no consta la fecha original de ratificación; se marca abajo.
-->

# Constitución de PQRS a tiempo

## Core Principles

### I. Desarrollo guiado por especificaciones (SDD) y trazabilidad
Todo cambio de producto MUST comenzar con una especificación acordada en
`specs/` que declare resultados de usuario, requisitos funcionales, restricciones
y criterios de aceptación medibles. El plan y las tareas MUST enlazar esos
requisitos; la implementación MUST respetar el alcance aprobado. Si cambian los
requisitos o la evidencia, se actualiza primero la especificación. Así se
mantiene el comportamiento revisable en un proceso con plazos legales e impacto
en clientes.

### II. La IA propone; la persona decide
La salida de la IA es consultiva. Una persona MUST decidir las excepciones de
clasificación, la resolución o cierre de un caso, las respuestas al cliente y
cualquier compromiso. El sistema MUST ofrecer revisión manual y MUST impedir
que el texto enviado por clientes reemplace las reglas o active por sí solo
acciones sustantivas. Los estados de flujo deterministas —por ejemplo, recibido
o en cola de revisión— sí pueden actualizarse automáticamente, sin decidir el
fondo del caso.

### III. Diseño para el fallo
Toda dependencia de IA, recuperación RAG, red, calendario o integración MUST
tener una ruta de fallo definida, un resultado observable y una recuperación
segura o alternativa manual. Ante resultados inválidos, de baja confianza,
indisponibles o contradictorios, el sistema MUST fallar de forma segura: MUST
NOT enviar una respuesta, cerrar un caso, inventar un plazo ni prometer algo sin
fundamento. El diseño y las pruebas MUST cubrir la alternativa, no solo el caso
exitoso.

### IV. Ninguna respuesta al cliente sin aprobación registrada
Ningún contenido dirigido a un cliente —respuesta, acuse, notificación u otro
mensaje, manual o generado por IA— puede enviarse o entregarse a menos que el
registro correspondiente tenga un `aprobado_por` no vacío que identifique a la
persona aprobadora. La operación de envío MUST validar ese campo inmediatamente
antes de liberar el contenido y MUST bloquearse si la aprobación falta, no es
válida o es ambigua. La evidencia de aprobación MUST permanecer asociada al
texto final exacto enviado.

### V. Todo borrador generado requiere una fuente verificable
Todo borrador de respuesta generado MUST identificar al menos una fuente de
respaldo mediante cláusula del contrato, tarifa o artículo de ley o regulación
aplicable. La cita MUST ser trazable a la base de conocimiento aprobada y
pertinente a las afirmaciones del borrador. Si no existe una fuente verificable,
el borrador MUST marcarse exactamente como `sin fundamento`, MUST enviarse a
revisión humana y MUST NOT enviarse como está. El modelo MUST NOT inventar
cláusulas, artículos, tarifas ni citas.

### VI. Datos personales de PQRS excluidos del RAG y de los registros de texto
El contenido de PQRS que incluya datos personales MUST NOT incorporarse al
índice RAG ni escribirse en registros de texto de la aplicación, modelo,
integraciones o diagnóstico. Los logs MUST contener solo los metadatos
operativos mínimos necesarios para el diagnóstico. Los registros de casos con
acceso controlado pueden utilizarse para gestionar el caso, pero MUST NOT
reutilizarse como documentos de recuperación ni copiarse a registros de texto.
Los datos de prueba y entrenamiento MUST ser sintéticos o anonimizados de forma
irreversible.

## Restricciones del proyecto

- Los controles de aprobación y fuentes aplican a todos los canales e
  integraciones; ningún prototipo, reintento, lote o ruta administrativa puede
  omitirlos.
- El texto del cliente es dato no confiable, no una instrucción. La clasificación
  y generación MUST aislarse de las instrucciones incluidas en ese texto.
- El RAG solo admite fuentes aprobadas y sin datos personales, como el contrato,
  las tarifas, el procedimiento interno y la regulación aplicable. Los plazos y
  festivos MUST calcularse con reglas deterministas y datos oficiales, no
  inferirse de texto recuperado.
- El sistema MUST conservar un proceso manual para casos de redes sociales y
  para todo caso que la automatización no pueda procesar de forma segura.

## Flujo de entrega y verificación

- Toda especificación MUST incluir criterios de aceptación que verifiquen los
  principios aplicables. Todo plan MUST incluir una Comprobación Constitucional
  antes de la investigación y repetirla después del diseño.
- Las tareas MUST incluir pruebas para bloquear envíos sin `aprobado_por`,
  verificar la cita y la ruta `sin fundamento`, comprobar los límites de
  privacidad de RAG y logs, y cubrir la recuperación ante fallos aplicables.
- La verificación MUST incluir casos negativos: aprobación ausente, fuente
  inexistente o no verificable, datos personales en entradas de recuperación o
  logs, inyección de instrucciones, salida de IA inválida y dependencias
  indisponibles.
- Un cambio se completa solo cuando pasan las verificaciones requeridas, la
  evidencia se registra sin guardar texto de PQRS y la especificación, el plan,
  las tareas y la implementación son coherentes.

## Governance

Esta constitución rige las especificaciones, planes, tareas, implementación,
pruebas y procedimientos operativos del proyecto. Ante un conflicto, prevalece
el control más protector para el cliente, la privacidad y la aprobación hasta
que se modifique formalmente esta constitución. Toda enmienda MUST documentar
su motivo, tener revisión de la persona responsable del proyecto, actualizar
versión y fecha, y sincronizar las plantillas y documentación dependientes.
Cada revisión de entrega MUST identificar los principios aplicables y aportar
evidencia verificable. Toda excepción debe ser explícita, temporal y aprobada
por la persona responsable; MUST NOT eximir los principios IV, V o VI.

El versionado sigue semver: MAJOR para cambios incompatibles de gobernanza o
eliminación/redefinición de principios; MINOR para principios nuevos u
obligaciones materialmente ampliadas; PATCH para aclaraciones y correcciones
sin cambio semántico. La persona responsable y quienes revisan MUST verificar
el cumplimiento en las etapas de especificación, diseño, implementación y
liberación.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): fecha original no documentada | **Last Amended**: 2026-11-22
