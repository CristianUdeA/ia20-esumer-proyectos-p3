# Modelo de datos: Clasificación y redacción local de PQRS

Este modelo define datos en memoria y artefactos de conocimiento aprobados. No autoriza a almacenar texto o datos personales de casos en Cloud Storage, logs, trazas, cachés ni el índice RAG.

## Entidades

### SolicitudPQRS (payload transitorio)

| Campo | Tipo/forma | Reglas |
|---|---|---|
| `texto` | string | Obligatorio, longitud máxima definida por configuración; se procesa localmente. Nunca se registra, persiste ni transmite a Vertex. |
| `correlation_id` | UUID opaco | Opcional o generado por servidor; solo metadato operacional, no derivado del texto. |

**Ciclo de vida**: validación → clasificación/redacción en memoria → respuesta al operador → liberación de referencias de memoria al completar la petición. No se conserva en esta API.

### Clasificacion

| Campo | Tipo/forma | Reglas |
|---|---|---|
| `cliente` | string o null | Extraído localmente; nunca inventar; sensible; no enviar a cloud ni logs. |
| `contrato` | string o null | Extraído localmente; nunca inventar; sensible; no enviar a cloud ni logs. |
| `tipo` | enum | `Petición`, `Queja`, `Reclamo`, `Sugerencia`; salida fuera del enum invalida la clasificación. |
| `categoria` | string | Debe pertenecer a la taxonomía aprobada y configurada; si no, revisión. |
| `urgencia` | string | Debe pertenecer a la taxonomía aprobada y configurada; si no, revisión. |
| `resumen` | string o null | Solo para respuesta de la petición; no almacenar ni registrar; no enviar a Vertex. |
| `nivel_confianza` | número [0,1] | <0,70 es baja; ausente/no válido equivale a resultado no confiable. |
| `motivo` | string | Explicación para el operador; no poner en logs. |
| `datos_ausentes` | lista de nombres de campo | Indica campos no extraídos; no incluye valores. |
| `revision_requerida` | boolean | True si confianza <0,70, datos requeridos ausentes, conflicto, salida inválida o taxonomía desconocida. |

### FuenteAprobada

| Campo | Tipo/forma | Reglas |
|---|---|---|
| `source_id` | string estable | Identificador opaco del documento permitido. |
| `titulo` | string | Título aprobado; sin datos de cliente. |
| `tipo_fuente` | enum | Contrato, tarifa, procedimiento o norma/regulación. |
| `version` | string/fecha | Versión vigente para trazabilidad. |
| `ubicacion` | string | Página, cláusula, tarifa o artículo verificable. |
| `aprobada` | boolean | Solo `true` puede entrar a ingesta y retrieval. |
| `contenido` | string | Fragmento de fuente no personal y aprobado. |

**Validación**: negar ingesta si no está aprobado, está vencido, contiene datos personales de PQRS o falta identificación de versión/ubicación verificable.

### FragmentoRAG

| Campo | Tipo/forma | Reglas |
|---|---|---|
| `chunk_id` | string estable | Referencia opaca al fragmento. |
| `source_id`, `version`, `ubicacion` | referencias | Deben apuntar a FuenteAprobada aprobada. |
| `texto_fragmento` | string | Solo contenido de fuente permitida; sin entrada, resumen ni respuesta de caso. |
| `embedding_model` | string | `text-embedding-004` para el índice de este hito; registrado en manifiesto. |
| `embedding` | vector numérico | Dimensión consistente dentro de un índice/versionado. |

**Ubicación**: objeto versionado en bucket privado de Cloud Storage. No contiene identificadores de caso, texto de PQRS ni metadatos personales.

### BorradorRespuesta

| Campo | Tipo/forma | Reglas |
|---|---|---|
| `texto` | string o null | Consultivo; no se libera al cliente. Puede incluir datos sensibles en el resultado al operador, pero nunca en logs ni payloads cloud. |
| `estado` | enum | `fundamentado`, `sin fundamento`, `revision_requerida`, `no_disponible`. |
| `citas` | lista de CitaFuente | Vacía o una o más citas verificables; toda afirmación factual del borrador debe estar apoyada. |
| `revision_requerida` | boolean | Obligatorio para sin fuente, baja confianza, fallo o datos insuficientes. |
| `bloqueado_para_liberacion` | boolean | True siempre en este servicio; no ofrece endpoint de envío. |
| `motivo_revision` | enum/string corto | Código de control, nunca un volcado de texto de entrada. |

### CitaFuente

| Campo | Tipo/forma | Reglas |
|---|---|---|
| `source_id` | referencia | Debe existir en el manifiesto aprobado. |
| `version` | string | Debe coincidir con la versión recuperada. |
| `ubicacion` | string | Página/cláusula/artículo consultable por la persona revisora. |
| `fragmento` | string | Extracto no personal que sustenta afirmaciones. |

### EventoOperacional (metadatos únicamente)

| Campo | Tipo/forma | Reglas |
|---|---|---|
| `correlation_id` | UUID opaco | No contiene identificadores de caso/persona. |
| `ruta`, `resultado`, `codigo_error` | enums/códigos | Sin texto de PQRS, prompt, resumen, secreto o respuesta. |
| `duracion_ms` | entero | Métrica permitida si se requiere. |
| `dependencias_estado` | lista de códigos | No incluir valores sensibles. |

## Entidades fuera de persistencia de esta API

**AprobacionHumana** no se administra en el servicio P1. Un sistema futuro que libere respuestas deberá mantener `aprobado_por`, fecha y digest del texto final exacto, y validar la correspondencia inmediatamente antes de liberar. Sin esa referencia válida, bloquear. Esta definición no agrega endpoint de aprobación o envío a los contratos de esta característica.

## Relaciones y estados

```text
SolicitudPQRS (efímera)
  ├─> Clasificacion (efímera; revisión si baja confianza/incompleta/conflictiva)
  └─> Retrieval de FragmentoRAG aprobado
        └─> BorradorRespuesta (efímero; fundamentado o sin fundamento)
```

Estados de borrador:

```text
inicio → fuentes verificadas → fundamentado + revisión humana
       ↘ sin fuente pertinente → "sin fundamento" + revisión + bloqueado
       ↘ dependencia/salida inválida → no_disponible/revision_requerida + bloqueado
```

No existe transición a `enviado` dentro de esta API. La revisión humana y la eventual aprobación viven en el flujo de operación externo.

## Invariantes de privacidad

1. Únicos datos admitidos en GCS/RAG: FuenteAprobada, FragmentoRAG, manifiesto y vectores asociados.
2. Ningún texto original, cliente, contrato, resumen, borrador, prompt completo o respuesta de un caso se escribe en logs, trazas o métricas.
3. Ningún dato anterior se manda al cliente Gemini/Vertex; prueba automatizada con marcadores únicos debe comprobar los payloads.
4. Los fixtures de evaluación son sintéticos; los logs de pruebas también omiten el contenido.
