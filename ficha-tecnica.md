# Proyecto 3 · PQRS a tiempo

**Ficha técnica: RAG, Spec Kit y Google Cloud** · IA Aplicada y Automatización de Procesos con IA Generativa (IA20) · Esumer

📋 [Ficha de especificación](README.md) · 📄 [Ficha en PDF](proyecto-03-pqrs-a-tiempo.pdf) · 🗂️ [Volver al índice de proyectos](../../README.md) · 🗓️ [Flujo de trabajo y cronograma](../../README.md#flujo-de-trabajo-y-cronograma)

Esta ficha resume **cómo se construye el proyecto** en la etapa final del curso: cómo se organiza el repositorio del equipo, qué parte resuelve un RAG, qué principios propios lleva la constitución de Spec Kit, qué specs se escriben, cómo se prueba en local, qué se despliega en Google Cloud y cómo se presenta en el Demo. El **qué y el porqué** del proyecto (necesidades, requisitos, reglas, modelo de ML y flujo) siguen en la [ficha de especificación](README.md).

| Ficha técnica | |
|---|---|
| **Organización** | ConectaHogar (proveedor de internet de barrio) |
| **Sector** | Telecomunicaciones |
| **Dificultad** | ★★★ |
| **Machine Learning** | Orange con el complemento *Text* (referencia frente al LLM) |
| **Conexión modelo–flujo** | El LLM clasifica en el flujo y Orange sirve de referencia de validación |
| **Orquestación** | Make + AppSheet |
| **Base de conocimiento del RAG** | Contrato, plan de tarifas y régimen de usuarios |
| **Complejidad del despliegue** | Medio |
| **Código del proyecto** | `p03` |
| **Servicio en Cloud Run** | `pqrs-a-tiempo` |
| **Proyecto de Google Cloud** | `ia20-p03-<equipo>` |
| **Orden en el Demo** | 5 de 7 |

## 1. Repositorio del equipo

Cada equipo trabaja en **su propio repositorio** con esta estructura:

```text
<repositorio-del-equipo>/
├── README.md         # Ficha del proyecto: problema, alcance, equipo y estado de avance
├── PROMPT_SPEC.md    # Prompt con el que se genera la spec (parte de la guía 01_prompt_crear_spec.md)
├── docs/             # Lo que el equipo produce: specs, informes, recomendación del modelo, presentaciones y guion del demo
└── insumos/          # Lo que el equipo recibe o recolecta: datasets, documentos de la organización, normativa y PDF de la ficha
```

Las specs que genera Spec Kit quedan en `specs/` (y su configuración en `.specify/`), en la raíz del repositorio. Los nombres de carpeta van en minúscula. La estructura común está en el [índice de proyectos](../../README.md#repositorio-de-cada-equipo).

## 2. Dónde entra el RAG

El borrador de respuesta debe ser correcto frente al contrato y la norma, no solo empático. Con RAG cita la cláusula, la tarifa o el artículo del régimen de usuarios que aplica, y el área solo verifica y aprueba.

| ✅ Va al RAG | ❌ No va al RAG |
|---|---|
| Contrato de servicio y plan de tarifas | El texto de las PQRS (datos personales) |
| Procedimiento interno de PQRS | Los días hábiles (regla + API de festivos) |
| Resumen del régimen de usuarios (CRC, 15 días hábiles) | La aprobación (la da una persona) |

> Un buen diseño **no mete todo en el RAG**: lo que cambia cada día o debe ser exacto va en tablas y reglas, y lo sensible lo decide una persona.

## 3. Principios propios de la constitución

El archivo `.specify/memory/constitution.md` del equipo parte de los **7 principios comunes** (ver el [flujo de trabajo](../../README.md#flujo-de-trabajo-y-cronograma)) y suma estos, propios del proyecto:

1. Nada sale al cliente sin `aprobado_por`.
2. Borrador sin fuente → «sin fundamento» y revisión.
3. Las PQRS no se guardan en el índice ni en los registros.

## 4. Specs de Spec Kit

| Spec | Qué construye |
|---|---|
| `specs/001-clasificar-y-redactar-local/` | Clasifica en JSON y redacta un borrador fundamentado con citas. |
| `specs/002-flujo-make-appsheet/` | Recepción → radicado → servicio → acuse; vencimientos; envío aprobado. |
| `specs/003-despliegue-gcp/` | Copia de la spec de despliegue del ejemplo, con `CODIGO_PROYECTO=p03` y el servicio `pqrs-a-tiempo`. |

Cada spec recorre el ciclo `/speckit-constitution` → `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement`.

## 5. Pruebas locales

- 40 PQRS sintéticas con su categoría y su documento esperado.
- Clasificación ≥ 85 %; LLM vs. Orange en la misma muestra.
- 0 borradores sin fundamento enviados.

Las metas se registran en `docs/informes/evaluacion_local` antes de pasar a la nube: **sin metas cumplidas no hay nube**.

## 6. Google Cloud

- Cloud Run: `/clasificar`, `/borrador` y `/salud`.
- Vertex AI (Gemini y embeddings).
- Cloud Storage (índice) · Secret Manager.

> Los festivos y AppSheet siguen igual en Make.

Lo que se despliega se **borra el mismo día**, con evidencia en `docs/informes/despliegue` e `docs/informes/borrado`.

## 7. Guion del Demo (12 min)

**Desplegar** → 3 PQRS de ejemplo → Borrador citado → Aprobar y enviar → Alerta de vencimiento → **Borrar**

## 8. Cronograma del proyecto

| Fechas | Etapa | Qué hace el equipo en este proyecto | Puerta |
|---|---|---|---|
| 14 y 15 Nov | Definición del alcance y Spec Kit | Leer la ficha, definir qué va y qué no va al RAG (sección 2), instalar las herramientas y escribir la constitución con los principios de la sección 3. | — |
| 21 Nov | Crear la spec e implementarla | Escribir y aclarar `001-clasificar-y-redactar-local` y `002-flujo-make-appsheet`, generar plan y tareas, armar el set de prueba e implementar por historia. | P0 · spec |
| 22 al 27 Nov | Solución de temas locales | Correr las pruebas de la sección 5, corregir y calibrar hasta cumplir las metas. | P1 · `v1.0-local` |
| 28 y 29 Nov | Despliegue en la nube | Aplicar `003-despliegue-gcp`: desplegar, verificar y borrar (sección 6). | P2 · nube |
| 1 al 6 Dic | Bootcamp | No hay clase. | — |
| 12 y 13 Dic | Demo | Desplegar desde cero, presentar con el guion de la sección 7 y borrar con evidencia. | Demo · `v1.0-demo` |
