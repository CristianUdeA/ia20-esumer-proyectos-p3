# Plan de implementación: Clasificar y redactar PQRS localmente

**Rama**: `main` (la spec declara `001-clasificar-y-redactar-local`) | **Fecha**: 2026-11-22 | **Spec**: [spec.md](spec.md)

**Entrada**: Especificación de `specs/001-clasificar-y-redactar-local/spec.md`

> **Alcance de este artefacto**: diseño para el hito **P1 · v1.0-local**. No implementa el producto. La carpeta `.specify/scripts/powershell/setup-plan.ps1` no existe en el checkout; por ello, rama y rutas se verificaron directamente en Git y en `.specify/feature.json`. La spec está en estado `Approved`; este plan no sustituye dicha aprobación.

## Resumen

Definir un servicio Python/FastAPI que se ejecute en el equipo local para clasificar PQRS, preparar borradores consultivos con citas y exponer `/clasificar`, `/borrador` y `/salud`. Google Gen AI SDK con Vertex AI proveerá Gemini para redacción y `text-embedding-004` para embeddings; Google Cloud Storage guardará únicamente el índice RAG de fuentes aprobadas. Secret Manager alojará secretos de aplicación que existan; la autenticación Google se resolverá con Application Default Credentials (ADC) local o identidad de carga de trabajo, nunca con claves de cuenta de servicio en el repositorio.

La restricción de privacidad de la spec prevalece: la clasificación se realiza localmente; el texto original de PQRS, sus datos personales, sus resúmenes y sus borradores no se envían a Vertex AI, no se escriben en logs y no se incorporan a GCS/RAG. La consulta de recuperación se limita a etiquetas de una taxonomía controlada y la llamada de generación recibe solo dichas etiquetas no identificables y extractos de fuentes públicas aprobadas. Si no puede construirse una solicitud que cumpla ese límite, no se llama al modelo y se escala a revisión.

La aceptación local contempla 40 PQRS sintéticas etiquetadas, precisión global de clasificación ≥85%, ninguna liberación de borrador `sin fundamento` y pruebas de privacidad/fallo seguro. No se incluye envío al cliente.

## Contexto técnico

- **Lenguaje/versión**: Python 3.11+ (mínimo de proyecto por fijar en la configuración de implementación).
- **Dependencias principales**: FastAPI y Pydantic; `google-genai` configurado para Vertex AI; `google-cloud-storage`; `google-cloud-secret-manager`; pytest y HTTPX para pruebas. Motor de clasificación local desacoplado detrás de una interfaz para que su elección/calibración no envíe texto a Vertex.
- **Almacenamiento**: Google Cloud Storage privado para fuentes aprobadas, manifiesto e índice de embeddings; procesamiento de casos en memoria durante la petición, sin persistir PQRS en esta API. No se crea una base de datos de casos en P1.
- **Pruebas**: pytest con `TestClient`, dobles de Vertex/GCS/Secret Manager y 40 casos sintéticos versionados; métricas automáticas y pruebas de no fuga.
- **Plataforma destino**: API ejecutada localmente, con conectividad a servicios Google Cloud para fuentes/modelos. No es un servicio offline ni un despliegue en Cloud Run para este hito.
- **Tipo de proyecto**: servicio web backend/API local.
- **Metas de rendimiento**: sin SLO de latencia especificado para P1; medir duración como metadato operacional sin registrar contenido.
- **Restricciones**: umbral de confianza 0,70; tipos Petición/Queja/Reclamo/Sugerencia; precisión ≥85% sobre ≥40 casos sintéticos; no enviar texto de PQRS a Vertex; no registrar texto, datos personales, resúmenes ni borradores; no indexar casos; ningún endpoint de envío; todo fallo de modelo, retrieval, credencial o validación requiere revisión manual y bloquea liberación. Las categorías/urgencias deben provenir de una taxonomía aprobada; si falta, revisión manual.

## Comprobación constitucional

### Antes de investigación — puerta de diseño

| Principio/puerta | Estado | Evidencia y control de diseño |
|---|---|---|
| I. Spec acordada y trazable | **Condicional** | La spec contiene FR-001–FR-012, criterios SC-001–SC-007 y escenarios verificables, pero su estado es `Draft`. Se puede documentar el diseño solicitado; no se autoriza implementación hasta aprobación formal y trazable de la persona responsable. |
| II. La IA propone; la persona decide | **Pasa en diseño** | Los resultados son consultivos, casos dudosos pasan a revisión, y no se expone endpoint de envío ni decisión sustantiva autónoma. |
| III. Diseño para el fallo | **Pasa en diseño** | Fallos de Vertex, GCS, Secret Manager, JSON inválido, baja confianza o evidencia no verificable bloquean el borrador/liberación y ofrecen revisión manual. |
| IV. Aprobación registrada antes de liberar | **Pasa por limitación de alcance** | Esta API no puede enviar ni liberar respuestas. Una integración futura debe verificar `aprobado_por` válido asociado al hash exacto del texto final justo antes de liberar. |
| V. Fuente verificable en cada borrador | **Pasa en diseño** | Una respuesta se redacta solo con pasajes aprobados y citas trazables; falta de fuente pertinente produce estado exacto `sin fundamento` y bloqueo. |
| VI. Privacidad de PQRS | **Pasa en diseño** | Ningún texto, resumen, PII ni borrador se envía al proveedor, persiste en el índice o aparece en logs. RAG contiene solo conocimiento aprobado sin PII de casos. |

No se identifica una excepción a los principios IV, V o VI. La aprobación pendiente de la spec es una condición bloqueante para implementación, no una dispensa.

### Re-evaluación después del diseño — puerta de salida

| Principio | Resultado | Comprobación de diseño |
|---|---|---|
| I. Trazabilidad y spec acordada | **Condicional / bloquea implementación** | Plan, modelo, contrato y guía vinculan el alcance y las métricas a la spec. La spec continúa `Draft`; no se declara aprobada ni se habilitan tareas de implementación. |
| II. Decisión humana | **Pasa** | El contrato no incluye envío; clasificación de baja confianza y borradores se mantienen en revisión. |
| III. Fallo seguro | **Pasa** | Los fallos simulados de dependencias, credenciales, retrieval o validación abstienen y no liberan. |
| IV. `aprobado_por` y texto exacto | **Pasa por alcance** | No existe liberación en este servicio; una integración posterior debe comprobar identidad y digest del texto final antes de enviar. |
| V. Fuente verificable | **Pasa** | El esquema exige citas y estado; sin fuente se usa `sin fundamento`, revisión y bloqueo. |
| VI. Privacidad | **Pasa** | Modelo, almacenamiento y logs excluyen texto de PQRS, PII, resúmenes y borradores; la prueba con marcadores verifica el límite de salida. |

**Resultado**: el diseño puede entregarse para revisión. La aprobación explícita de la spec y la taxonomía de categoría/urgencia siguen siendo prerequisitos de implementación/evaluación; no son aprobaciones implícitas en este plan.

## Decisiones arquitectónicas

1. **API local y componentes delimitados**: `api` valida/serializa; `classification` procesa el texto solo localmente; `retrieval` carga o consulta el índice de fuentes; `generation` prepara un prompt con lista permitida de etiquetas no identificables y pasajes RAG; `security` aplica guardas de privacidad, fuentes y revisión; `observability` emite solo metadatos. Si la clasificación tiene confianza <0,70, faltan datos requeridos o hay conflicto, no se genera un borrador listo para liberar y se responde con revisión requerida.
2. **Datos sensibles efímeros**: el texto de entrada se mantiene en memoria de proceso durante la petición. No se persiste ni se guarda en cachés, trazas, excepciones, métricas o volcados. La respuesta se entrega al operador; no hay almacenamiento ni envío a cliente en esta versión.
3. **RAG solo de conocimiento aprobado**: ingestión administrativa (fuera de los tres endpoints) de contrato, tarifas, procedimiento y regulación aprobados, sin PQRS ni datos personales. GCS almacena artefactos versionados de fuentes/chunks/vectorización. Para el corpus pequeño local, la recuperación puede cargar el manifiesto/vectores y calcular similitud en memoria; GCS no se trata como motor vectorial. Citas conservan identificador de documento, versión, página/cláusula/artículo y fragmento que el revisor pueda ubicar.
4. **No exfiltrar el caso a Vertex**: ni los campos `cliente`, `contrato`, texto libre, resumen ni borrador final se envían a la nube. Se generan consultas solo de etiquetas controladas (no paráfrasis del cliente); el generador recibe esas etiquetas y fragmentos aprobados. Se verifica con marcadores sintéticos únicos en pruebas de transporte. Ante duda sobre filtrado, abstenerse y pedir revisión.
5. **Credenciales**: en local, ADC mediante `gcloud auth application-default login` con permisos mínimos y acceso explícito a los secretos necesarios; en ejecución Google Cloud, identidad de carga de trabajo. Secret Manager se consulta mediante su cliente, privilegio mínimo y versiones fijadas; no se exporta una clave JSON ni se imprimen valores de secretos. No incluir secretos en `.env`, fixtures ni logs.
6. **Pruebas que no dependen de la nube**: dobles verificables para Vertex, GCS y Secret Manager; el endpoint local y el cálculo de las métricas de los 40 fixtures deben ser ejecutables sin llamadas externas. La integración con Google Cloud se valida por separado cuando existe proyecto/permisos, sin usar datos reales de clientes.
7. **Sin liberación**: `/borrador` devuelve texto consultivo y estado de revisión. No existe `/enviar`, tarea programada ni ruta alternativa que libere mensajes. Si una fase posterior incorpora liberación, deberá implementarse aparte con aprobación humana y hash del texto final.

## Estructura del proyecto

No hay código de aplicación en el repositorio actual; esta es la estructura propuesta, no una descripción de archivos ya existentes:

```text
src/pqrs_local/
├── main.py                 # creación de FastAPI y ciclo de vida
├── api/                    # rutas y esquemas HTTP
├── domain/                 # entidades, enums y reglas
├── services/               # clasificación local, RAG, generación y guardas
├── adapters/                # Vertex AI, GCS, Secret Manager
└── observability/           # metadatos mínimos, redactados
tests/
├── contract/                # contrato HTTP y esquemas
├── unit/                    # reglas, privacidad y fallo seguro
├── integration/             # adaptadores con dobles; nube optativa
└── evaluation/
    ├── fixtures/             # 40+ casos sintéticos y etiquetas
    └── test_acceptance_40.py # precisión y bloqueo de borradores
knowledge/                    # fuentes de ingestión aprobadas; no PQRS
```

**Decisión de estructura**: un solo backend FastAPI local, dividido en dominio y adaptadores externos. Los documentos de conocimiento y sus artefactos se separan físicamente del código de pruebas y de cualquier dato de caso.

## Trazabilidad de requisitos

| Requisito de spec | Decisión/diseño | Verificación prevista |
|---|---|---|
| FR-001–FR-004 | `POST /clasificar`, esquema JSON tipado, motor local, confianza 0,70 y revisión para campos ausentes/conflictos. | Casos unitarios de esquema/abstención y fixtures sintéticos de evaluación. |
| FR-005–FR-006 | `POST /borrador`, recuperación de fuentes aprobadas, cita verificable y estado `sin fundamento` ante ausencia de fuente pertinente. | Dobles de RAG/Vertex; cita y fuente ausente en pruebas. |
| FR-007 | Texto del cliente se trata como dato; el contexto de generación usa únicamente taxonomía controlada y pasajes permitidos. | Casos de inyección sintéticos y aserción del payload saliente. |
| FR-008–FR-009 | No persistencia de casos; GCS/RAG solo contiene documentos aprobados; observabilidad de metadatos mínimos. | Prueba de marcadores en logs/payloads/índice y revisión de artefactos GCS. |
| FR-010 | Sin endpoint de envío; todo borrador queda bloqueado para liberación. La aprobación con digest exacto corresponde a una integración futura. | Contrato sin `/enviar`; aserciones `bloqueado_para_liberacion=true`. |
| FR-011 | Fallo de modelo, retrieval, credenciales, salida inválida o fuente no verificable produce abstención y revisión. | Pruebas de fallos simulados por adaptador. |
| FR-012 | Dataset versionado con ≥40 casos sintéticos y tipos de referencia. | Pytest calcula aciertos/total y falla bajo 0,85. |
| SC-001–SC-002 | Umbral de precisión y revisión de casos baja confianza/incompletos. | Prueba de aceptación 40 y pruebas de umbral 0,70. |
| SC-003–SC-004 | Citas trazables, `sin fundamento`, sin liberación ni envío. | Tests de contrato/fuente y bloqueo. |
| SC-005–SC-006 | Privacidad de índice/logs y resistencia a instrucciones de entrada. | Pruebas de marcadores sintéticos y reglas de control. |
| SC-007 | La evaluación de empatía queda como medición humana/documentada, sin texto de PQRS en logs. | Guía de revisión manual: ≥80% de revisores puntúa claridad/empatía ≥4/5; guardar solo agregados. |

## Puertas posteriores al diseño

- Antes de implementar: obtener aprobación de la spec Draft; acordar taxonomía de categoría/urgencia; confirmar proyecto/región Vertex y permisos mínimos; verificar vigencia/disponibilidad del modelo Gemini elegido; comprobar que `text-embedding-004` sigue disponible (retiro anunciado para 2027-04-01) y registrar plan de migración antes de esa fecha.
- Antes de P1 · v1.0-local: ejecutar pytest en entorno sin llamadas de nube para 40 casos; calcular precisión global como aciertos de tipo / total y exigir ≥0,85; comprobar todos los borradores sin fuente verificable quedan con `sin fundamento`, revisión requerida y bloqueados; comprobar cero marcadores de entrada en payloads/logs/índice.
- No se autoriza despliegue en Cloud Run ni liberación a clientes en este plan.

## Seguimiento de complejidad

No se detectan violaciones constitucionales aprobadas ni se solicita excepción. La separación de adaptadores/servicios se justifica por los límites de datos, la necesidad de probar modo local sin nube y el bloqueo seguro; no añade otro servicio desplegable.
