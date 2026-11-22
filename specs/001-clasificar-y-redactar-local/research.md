# Investigación: Clasificación y redacción local de PQRS

**Fecha de consulta**: 2026-11-22
**Alcance**: decisiones tecnológicas y de privacidad para P1 · v1.0-local. La spec vigente y la Constitución son la autoridad para las restricciones de producto.

## Decisiones

### D1. API FastAPI ejecutada localmente; no implica procesamiento sin red

- **Decisión**: ejecutar FastAPI en el equipo local. Los adaptadores usan clientes oficiales de Google Cloud cuando se requiere Vertex AI, Cloud Storage o Secret Manager. `/salud` informa estado sin hacer llamadas de prueba que transmitan datos.
- **Racional**: cumple el límite local del hito y separa el proceso HTTP de los servicios cloud administrados.
- **Alternativas consideradas**: Cloud Run, descartado para P1 · v1.0-local porque el hito es de validación local; API offline, descartada porque Vertex AI/GCS requieren conexión.

### D2. Google Gen AI SDK para Vertex AI; modelo Gemini configurable

- **Decisión**: integrar Gemini mediante `google-genai` en modo Vertex AI, con proyecto, región y nombre de modelo configurados fuera del código. Fijar modelo GA y API estable en la configuración de implementación; no usar Gemini Developer API ni una API key directa.
- **Racional**: el SDK oficial Python admite la plataforma empresarial Vertex; permite autenticación con identidad Google y hace explícito el destino.
- **Alternativas consideradas**: SDK específico de modelos anterior, no elegido para nuevo código; API Gemini Developer con API key, descartada por separar credenciales y evitar una identidad distinta de Vertex.
- **Condición de privacidad**: a pesar de que el servicio de inferencia está en la nube, el payload no puede incluir texto, PII, contrato, resumen ni borrador de una PQRS. Solo puede llevar taxonomía fija no identificable y fuentes públicas aprobadas. Si ese contrato no puede verificarse, no se invoca Vertex y se requiere revisión manual.

### D3. Clasificación dentro del proceso local

- **Decisión**: crear una interfaz de clasificación local desacoplada de la ruta Gemini. El motor elegido para implementación debe operar con el texto dentro del proceso local, producir campos validados contra taxonomía y abstenerse cuando falten datos, haya contradicciones o confianza <0,70. En esos casos, `/borrador` no debe generar una respuesta lista para liberar. El conjunto de aceptación de 40 casos debe evaluar el motor real configurado, no un doble que fuerce etiquetas correctas.
- **Racional**: la spec prohíbe enviar texto de PQRS a servicios externos; Vertex/Gemini no puede clasificar esos textos sin contradecir esa condición.
- **Alternativas consideradas**: clasificación con Gemini/Vertex enviando texto, rechazada por la restricción de privacidad; reglas de clasificación acopladas a la ruta HTTP, rechazadas por hacer difícil verificar rendimiento y reemplazar/calibrar el motor.
- **Decisión para la puerta de implementación**: evaluar y elegir el motor local con datos sintéticos etiquetados. Las opciones de categoría/urgencia serán configuración aprobada por el servicio; si la taxonomía no está disponible, marcar para revisión, según la suposición de la spec. No se afirma todavía que la meta de 85% esté alcanzada.

### D4. Embeddings RAG con `text-embedding-004` y corpus cerrado

- **Decisión**: usar `text-embedding-004` con tarea de documento para fragmentos de conocimiento aprobado. En recuperación, generar el vector de consulta únicamente a partir de etiquetas controladas no derivadas como texto del cliente. Mantener el ID de modelo y versión del índice en el manifiesto; rechazar mezclas de dimensiones/modelos.
- **Racional**: satisface el modelo solicitado y distingue contexto de documento y consulta. La documentación oficial consultada anuncia retiro de `text-embedding-004` el **2027-04-01**; hay margen para el hito local, pero no para asumir disponibilidad indefinida.
- **Alternativas consideradas**: `gemini-embedding-001`, alternativa recomendada para migración porque la tabla oficial consultada indica que no se retirará antes de 2028-05-20; no se cambia al modelo alternativo en este plan porque el requisito indica explícitamente `text-embedding-004`. Versionar y planificar migración es requisito previo a uso posterior al retiro.
- **Límites**: documentos RAG aprobados, vigentes y sin datos personales; ninguna PQRS, resumen, nombre, número de contrato o borrador se vectoriza.

### D5. GCS como almacenamiento de objetos del índice, no como motor de similitud

- **Decisión**: bucket privado de Cloud Storage para documentos versionados permitidos, chunks, vectores y manifiesto. Para el corpus P1, cargar el manifiesto y calcular similitud coseno localmente; si el corpus crece, revisar arquitectura por separado. Acceso IAM limitado a los buckets/objetos necesarios.
- **Racional**: GCS es almacenamiento de objetos; no se presenta como una base vectorial administrada. La búsqueda local mantiene explícito el alcance pequeño y ayuda a asegurar que los casos de evaluación no se persistan.
- **Alternativas consideradas**: Vertex AI Vector Search, descartado para este hito porque el usuario pidió índice en GCS y no hay requerimiento de escala que justifique un segundo servicio; bucket público o ACL amplia, descartado por no limitar acceso.

### D6. ADC e IAM/Secret Manager sin claves estáticas

- **Decisión**: ADC de `gcloud auth application-default login` para desarrollo local y una identidad de carga para un despliegue Google futuro. Los secretos de aplicación se leen por cliente de Secret Manager con permisos mínimos y versión explícita; secretos de autenticación de Google no se sustituyen por archivos de clave descargables.
- **Racional**: las prácticas oficiales de Secret Manager recomiendan ADC para desarrollo y evitar exportar/almacenar claves de cuenta de servicio; conceder solo permisos mínimos.
- **Alternativas consideradas**: clave JSON en el repositorio, archivos `.env` con credenciales o variables con valores secretos, descartados por exposición accidental y por reducir auditoría/control.
- **Manejo de fallo**: credencial ausente, secreto inaccesible o versión deshabilitada impide las operaciones cloud; no se activa modo inseguro ni se registra el valor.

### D7. Pruebas API con pytest y aislamiento de servicios

- **Decisión**: FastAPI `TestClient`/HTTPX y pytest; simular Vertex/GCS/Secret Manager en las pruebas locales. La suite de evaluación mantiene ≥40 ejemplos sintéticos con etiqueta de referencia y calcula precisión global. Una llamada real a la nube es prueba de integración opcional, nunca requisito para el umbral local.
- **Racional**: el patrón oficial de FastAPI permite probar rutas sin levantar un servidor y pytest soporta aserciones directas; dobles permiten inspeccionar payloads y asegurar ausencia de marcadores de PQRS.
- **Alternativas consideradas**: pruebas que dependen de credenciales/red para cada corrida, descartadas por no ser reproducibles; medir precisión solo sobre respuestas simuladas, descartado porque no evalúa el motor de clasificación elegido.

### D8. Esquemas de API y ausencia de interfaz de envío

- **Decisión**: contrato OpenAPI 3.1 para `POST /clasificar`, `POST /borrador` y `GET /salud`. No hay `/enviar`; el borrador nunca queda marcado como aprobado ni listo para liberar.
- **Racional**: hace validables las entradas/salidas del servicio y preserva control humano. La aprobación de una integración futura requiere `aprobado_por` y vínculo al hash del texto final; queda fuera del alcance presente.
- **Alternativas consideradas**: endpoint de liberación implementado en la misma API, descartado por alcance y por riesgo de saltarse el sistema humano de aprobación.

## Restricciones resueltas y puntos de verificación

- **“Local” frente a Vertex**: el proceso FastAPI y la clasificación corren localmente; la integración Vertex procesa solo taxonomía fija y fuentes aprobadas, nunca el contenido de casos. Esto permite usar generación cloud sin contradecir la asunción de la spec.
- **Latencia**: no hay objetivo numérico en la spec; no se introduce un umbral nuevo. Se podrá registrar duración sin contenido para formar una línea base.
- **Retención de casos**: no hay base local de casos en esta versión; los datos viven solo durante la petición y en la respuesta al operador. Un requisito de persistencia requeriría especificar controles/retención antes de implementarse.
- **Aprobación de spec**: el archivo está en estado `Draft`; no es un desconocido técnico, pero bloquea implementación hasta aprobación formal.
- **Taxonomía**: tipo está fijado por spec; categoría y urgencia deben configurarse/aprobarse. Un valor sin taxonomía vigente se escala manualmente.

## Fuentes consultadas

1. Google Gen AI Python SDK, guía de instalación, clientes Vertex y configuración: <https://googleapis.github.io/python-genai/>
2. Google Cloud, ciclo de vida de modelos (fechas de retiro de `text-embedding-004` y `gemini-embedding-001`): <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions>
3. Google Cloud, API de embeddings (modelos soportados, tipos de tarea y parámetros): <https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api>
4. Google Cloud Secret Manager, buenas prácticas (ADC, IAM de mínimo privilegio y no exportar credenciales): <https://cloud.google.com/secret-manager/docs/best-practices>
5. Google Cloud Storage, roles IAM: <https://cloud.google.com/storage/docs/access-control/iam-roles>
6. FastAPI, pruebas con `TestClient` y pytest: <https://fastapi.tiangolo.com/tutorial/testing/>

> Las páginas de Google Cloud cambian durante el ciclo de vida del proyecto. Verificar de nuevo el modelo, región, API y fechas de retiro antes de implementación y antes de P1.
