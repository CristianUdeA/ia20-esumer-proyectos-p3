# Tasks: Clasificación y redacción local de PQRS

**Input**: `specs/001-clasificar-y-redactar-local/plan.md` y `specs/001-clasificar-y-redactar-local/spec.md`

**Alcance**: P1 · v1.0-local. La spec consultada conserva su estado `Approved`; este archivo no cambia la spec ni sus criterios.

**Gate de aceptación que se conserva**: evaluación con al menos 40 PQRS sintéticas etiquetadas y precisión global de clasificación ≥85%. El CSV inicial de 5 casos es únicamente un smoke test y no satisface ese gate. El dataset final de 300 casos se incorporará después, fuera de este alcance.

**Pruebas**: requeridas por la spec y la constitución. Todas las pruebas locales usan dobles/mocks de Vertex AI, GCS y Secret Manager; ninguna debe transmitir PQRS, datos personales, resúmenes o borradores a servicios cloud.

**Organización**: las cuatro fases requeridas son Setup, Test-First, Core e Integración. Core e Integración agrupan tareas por historias P1 para conservar su trazabilidad y pruebas independientes.

## Phase 1: Setup

**Propósito**: inicializar el proyecto local según la estructura del plan, sin implementar todavía el comportamiento de producto.

- [X] T001 Crear la estructura exacta del proyecto en `src/pqrs_local/{api,domain,services,adapters,observability}/`, `src/pqrs_local/main.py`, `tests/{contract,unit,integration,evaluation/fixtures}/` y `knowledge/`; incluir `__init__.py` en los paquetes Python. Verificación: `Test-Path` confirma cada ruta indicada en `plan.md`, incluidas `src/pqrs_local/` y `tests/evaluation/fixtures/`.
- [X] T002 Configurar el paquete Python y dependencias de ejecución/prueba (FastAPI, Pydantic, google-genai, Google Cloud Storage, Secret Manager, pytest y HTTPX) en `pyproject.toml`. Verificación: `python -m pip install -e ".[test]"` termina sin error y pytest queda disponible.
- [X] T003 Añadir la configuración local sin secretos en `src/pqrs_local/config.py` y `.env.example` para proyecto/región, bucket, modelos y referencias a secretos. Verificación: comprobar que existen las claves requeridas y que no hay valores de credenciales, claves privadas ni contenido de PQRS.
- [X] T004 Confirmar con la persona responsable la aprobación humana aplicable a la spec y a la constitución antes de implementar o habilitar integraciones; conservar `Status: Approved` en `specs/001-clasificar-y-redactar-local/spec.md` y no completar por inferencia la ratificación pendiente de `.specify/memory/constitution.md`. Verificación: inspeccionar evidencia explícita de aprobación; si falta alguna aprobación requerida, detener Core/Integración y no alterar el estado de la spec.

## Phase 2: Test-First

**Propósito**: definir contratos y pruebas primero; ejecutar selectivamente para verificar que fallan por comportamiento aún no implementado, no por errores de sintaxis/colección.

- [X] T005 [P] Crear `tests/evaluation/fixtures/pqrs_smoke_5.csv` con exactamente 5 PQRS totalmente sintéticas y columnas `id,texto,tipo_esperado`; este archivo solo arranca el pipeline como smoke test. El dataset final de 300 casos se incorporará después y no forma parte de esta fase. Verificación: validar encabezado, cinco filas de datos, cuatro valores de tipo permitidos cuando sea posible y ausencia de datos reales.
- [X] T006 [P] [US1] Escribir pruebas de contrato de `POST /clasificar` para JSON Pydantic válido, campos ausentes/nulos, enums, confianza <0,70, revisión manual y errores seguros en `tests/contract/test_clasificar.py`. Verificación: `pytest -q tests/contract/test_clasificar.py` se recolecta y falla únicamente por la ruta/comportamiento aún no implementado.
- [X] T007 [P] [US1] Escribir la prueba de aceptación que calcula aciertos/total y exige ≥0,85 sobre al menos 40 casos etiquetados en `tests/evaluation/test_acceptance_40.py`. Verificación: `pytest -q tests/evaluation/test_acceptance_40.py` se recolecta y detecta explícitamente que falta el dataset de aceptación de 40; no acepta el CSV smoke de 5 como sustituto.
- [x] T008 [P] [US2] Escribir pruebas de contrato para `POST /borrador`: cita trazable con fuente aprobada, estado exacto `sin fundamento`, revisión requerida y bloqueo ante falta/fallo de fuente o generación en `tests/contract/test_borrador.py`. Verificación: `pytest -q tests/contract/test_borrador.py` se recolecta y reporta solo el comportamiento aún no implementado.
- [X] T009 [P] [US3] Escribir pruebas de contrato para `GET /salud`, sin inferencia ni exposición de credenciales, en `tests/contract/test_salud.py`. Verificación: `pytest -q tests/contract/test_salud.py` se recolecta y falla por endpoint/comportamiento ausente.
- [x] T010 [P] [US3] Escribir pruebas unitarias de inyección de prompt, privacidad de logs/RAG y bloqueo de liberación sin `aprobado_por` asociado al texto final exacto en `tests/unit/test_privacy_and_approval.py`. Verificación: `pytest -q tests/unit/test_privacy_and_approval.py` se recolecta y evidencia las protecciones aún no implementadas.
- [X] T011 [P] Crear fixtures autouse y dobles de Vertex AI, GCS y Secret Manager en `tests/conftest.py` para que ninguna prueba local cree clientes reales ni abra conexiones cloud. Verificación: una prueba centinela sustituye los clientes externos por dobles y falla si intenta una llamada de red; `pytest -q tests/` puede ejecutarse sin credenciales cloud.

## Phase 3: Core

**Propósito**: implementar los contratos FastAPI/Pydantic y la lógica local por historia, usando interfaces inyectables para las integraciones externas.

### US1 — Clasificar una PQRS localmente (P1, MVP)

**Prueba independiente**: `pytest -q tests/contract/test_clasificar.py tests/evaluation/test_acceptance_40.py`; exigir JSON conforme al contrato, revisión en casos incompletos/baja confianza y ≥85% sobre ≥40 casos sintéticos.

- [x] T012 [P] [US1] Definir modelos y validaciones Pydantic de entrada/salida de clasificación en `src/pqrs_local/domain/classification.py`, incluidos tipo permitido, confianza 0–1, campos nulos y motivo de revisión. Verificación: `pytest -q tests/contract/test_clasificar.py` valida el esquema y rechaza valores fuera de contrato.
- [x] T013 [US1] Implementar clasificación local, extracción sin invención y abstención/revisión para confianza <0,70, faltantes, contradicciones o salida inválida en `src/pqrs_local/services/classification.py` y `src/pqrs_local/api/classification.py`. Verificación: `pytest -q tests/contract/test_clasificar.py` pasa y los casos de revisión devuelven el estado esperado.
- [x] T014 [US1] Incorporar el corpus de aceptación versionado `tests/evaluation/fixtures/pqrs_acceptance_40.csv`, con al menos 40 casos sintéticos etiquetados y cobertura de Petición, Queja, Reclamo y Sugerencia. Verificación: contar ≥40 filas, confirmar cobertura de los cuatro tipos y comprobar que el corpus no contiene datos reales.
- [x] T015 [US1] Conectar la prueba de aceptación con el corpus de 40 casos en `tests/evaluation/test_acceptance_40.py` y calcular precisión como aciertos de tipo/total sin cambiar el gate de ≥85%. Verificación: `pytest -q tests/evaluation/test_acceptance_40.py` pasa solo si hay ≥40 casos y precisión ≥0,85; los 5 casos smoke no cuentan para el resultado.

### US2 — Preparar un borrador con respaldo verificable (P1)

**Prueba independiente**: `pytest -q tests/contract/test_borrador.py`; borrador fundamentado requiere cita comprobable, y sin fuente debe quedar exactamente `sin fundamento`, en revisión y bloqueado.

- [x] T016 [P] [US2] Definir modelos Pydantic de borrador, cita y referencia verificable en `src/pqrs_local/domain/drafts.py`, incluyendo identificador/versión/ubicación de fuente y estado de fundamento. Verificación: la prueba de contrato acepta citas completas y rechaza citas no trazables.
- [x] T017 [US2] Implementar el servicio consultivo de borradores y la ruta `POST /borrador` en `src/pqrs_local/services/drafting.py` y `src/pqrs_local/api/drafting.py`, consumiendo puertos inyectables de recuperación/generación y bloqueando toda liberación. Verificación: `pytest -q tests/contract/test_borrador.py` pasa para fuente presente, ausente e indisponible; no se define `/enviar`.

### US3 — Mantener límites de seguridad y privacidad (P1)

**Prueba independiente**: `pytest -q tests/contract/test_salud.py tests/unit/test_privacy_and_approval.py`; las entradas se tratan como datos, ningún marcador personal llega a logs/salida no permitida y falta de aprobación bloquea liberación.

- [x] T018 [US3] Montar la aplicación FastAPI y `GET /salud` en `src/pqrs_local/main.py` y `src/pqrs_local/api/health.py`, reportando estado operacional sin texto de caso, secretos ni llamada de inferencia. Verificación: `pytest -q tests/contract/test_salud.py` pasa y la respuesta solo contiene los campos de salud permitidos.
- [x] T019 [US3] Implementar la política de revisión/aprobación humana que valida `aprobado_por` y el digest del texto final, sin crear una ruta de envío, en `src/pqrs_local/services/approval.py`. Verificación: `pytest -q tests/unit/test_privacy_and_approval.py` bloquea aprobación ausente, identidad ambigua y texto modificado.

## Phase 4: Integración

**Propósito**: integrar RAG y adaptadores cloud detrás de interfaces seguras; las pruebas locales usan siempre los dobles creados en Test-First.

### US2 — RAG, generación y citas

**Prueba independiente**: pruebas locales de recuperación/generación con dobles; las citas deben ser aprobadas, pertinentes y localizables, y cualquier falta o fallo debe producir `sin fundamento` y revisión.

- [x] T020 [P] [US2] Implementar el adaptador de almacenamiento privado de fuentes aprobadas, manifiesto y artefactos RAG en `src/pqrs_local/adapters/gcs_storage.py`; rechazar objetos que no sean fuentes aprobadas y no ofrecer operaciones de indexación de PQRS. Verificación: pruebas con GCS mock aceptan solo manifiestos aprobados y comprueban que no se escribe texto de caso.
- [x] T021 [P] [US2] Implementar la recuperación RAG en `src/pqrs_local/services/rag.py`, usando solo etiquetas de taxonomía controlada y pasajes de conocimiento aprobados; producir citas con documento, versión y página/cláusula/artículo. Verificación: pruebas RAG con dobles rechazan fuentes no aprobadas/no pertinentes y verifican la trazabilidad de cada cita.
- [x] T022 [P] [US2] Implementar el adaptador Vertex AI con `google-genai` en `src/pqrs_local/adapters/vertex_ai.py`; su contrato solo admite etiquetas controladas y extractos aprobados, nunca PQRS, PII, resumen ni borrador del cliente. Verificación: prueba de payload con marcadores sintéticos confirma que ninguno aparece en la solicitud al doble Vertex.
- [x] T023 [US2] Conectar `src/pqrs_local/services/drafting.py` con los puertos RAG y Vertex mediante inyección de dependencias y respuesta de fallo seguro. Verificación: `pytest -q tests/contract/test_borrador.py` pasa con dependencias simuladas y verifica citas, `sin fundamento`, revisión y bloqueo.

### US3 — Privacidad, credenciales y fallo seguro

**Prueba independiente**: pruebas locales con clientes simulados y sin credenciales; inyección, fallos de credencial/retrieval/generación y marcadores sintéticos no pueden eludir revisión ni llegar a RAG, logs o payloads externos.

- [x] T024 [P] [US3] Implementar autenticación ADC/identidad de carga de trabajo y lectura de referencias de Secret Manager sin claves de cuenta de servicio en `src/pqrs_local/adapters/google_credentials.py`. Verificación: pruebas con Secret Manager/ADC mock confirman que no se requiere ni se registra una clave JSON y que credenciales ausentes generan fallo seguro.
- [x] T025 [US3] Implementar guardas de privacidad y de inyección de prompt en `src/pqrs_local/services/input_safety.py` y `src/pqrs_local/observability/privacy.py`; mantener texto del cliente como dato no confiable y emitir solo metadatos mínimos. Verificación: `pytest -q tests/unit/test_privacy_and_approval.py` confirma que marcadores sintéticos no aparecen en logs ni contexto permitido y que no cambian reglas/acciones.
- [x] T026 [US3] Añadir pruebas de integración locales de adaptadores, RAG, fallo seguro y ausencia de fuga en `tests/integration/test_local_boundaries.py`, con los mocks autouse de `tests/conftest.py`. Verificación: `pytest -q tests/integration/test_local_boundaries.py` pasa sin credenciales/red y falla si un payload/log/RAG contiene un marcador de PQRS o PII.
- [x] T027 [US3] Verificar la suite local completa y la ausencia contractual de cualquier endpoint de envío en `tests/` y `src/pqrs_local/main.py`. Verificación: `pytest -q` pasa, se reporta el resultado del gate ≥85% sobre ≥40 casos y la revisión de rutas en `src/pqrs_local/main.py` confirma que solo existen `/clasificar`, `/borrador` y `/salud`.

## Dependencias y orden de ejecución

- **Setup → Test-First → Core → Integración**: las fases se completan en ese orden. T004 es una puerta humana: si falta aprobación requerida, se permite preparar/ejecutar pruebas locales, pero no avanzar a implementación o integración bloqueada.
- **US1**: T006–T007 preceden T012–T015; el corpus de 40 casos y el gate de ≥85% son necesarios para completar esta historia. El CSV de 5 casos solo permite smoke test.
- **US2**: T008 precede T016–T017; T020–T022 implementan por separado fuentes/RAG/Vertex y T023 los conecta al borrador. Ninguna ruta devuelve un borrador liberable.
- **US3**: T009–T011 preceden T018–T019; T024–T026 completan las barreras de credenciales, privacidad, inyección y pruebas de fallos.
- **Todas las pruebas locales** dependen de T011 y deben usar sus dobles; no se configura una prueba local que contacte Vertex, GCS o Secret Manager reales.
- La evaluación de empatía de SC-007 continúa siendo revisión humana y agregada; no se registran textos de PQRS.

## Oportunidades de paralelismo

- Tras T001, se pueden trabajar en paralelo T005–T011, pues escriben fixtures y archivos de prueba distintos; T002/T003 permanecen como configuración secuencial de Setup.
- En Core, T012 y T016 son modelos en archivos distintos; T014 puede preparar el corpus en paralelo con los contratos, y T018–T019 son independientes de la clasificación una vez completado Test-First.
- En Integración, T020, T022 y T024 pueden ejecutarse en paralelo (archivos distintos); T021 depende del contrato de fuentes, T023 espera los puertos RAG/Vertex y T026 espera los adaptadores y guardas.

### Ejemplos de ejecución paralela

```text
Después de T001:
  T006 tests de POST /clasificar
  T008 tests de POST /borrador
  T009 tests de GET /salud
  T010 tests de privacidad/aprobación
  T011 dobles locales de servicios cloud

Después de Test-First:
  T012 modelos de clasificación  || T016 modelos de borrador
  T014 corpus sintético de 40 casos || T018 montaje de salud

En Integración, después de Core:
  T020 adaptador GCS || T022 adaptador Vertex || T024 ADC/Secret Manager
```

## Estrategia MVP

1. Completar Setup y Test-First; conservar la aprobación humana como puerta para la implementación.
2. MVP = US1: completar clasificación local y su contrato, luego validar con al menos 40 PQRS sintéticas y precisión ≥85%; no declarar éxito con los 5 casos smoke.
3. Incorporar US2 con RAG/citas verificables y `sin fundamento` ante ausencia de fuente; mantener el borrador bloqueado para liberación.
4. Completar US3 y las integraciones con dobles en todas las pruebas locales; verificar privacidad, inyección, revisión humana y fallos seguros.
5. El dataset final de 300 casos se incorporará en una etapa futura y no altera el gate vigente ni el estado de la spec.

## Verificación constitucional

- Ningún texto de PQRS/PII, resumen o borrador se envía a Vertex, se incorpora al RAG o aparece en logs de texto.
- El RAG usa exclusivamente fuentes aprobadas y citas verificables; sin respaldo se devuelve exactamente `sin fundamento` y se requiere revisión humana.
- Inyección de prompt se trata como dato; no modifica reglas de clasificación, privacidad ni aprobación.
- No existe endpoint de envío. Toda futura liberación exige aprobación humana válida asociada al texto final exacto.
- Fallos de clasificación, credenciales, recuperación, validación o generación se abstienen y ofrecen revisión manual.
