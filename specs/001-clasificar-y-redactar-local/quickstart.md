# Guía de validación local — P1 · v1.0-local

> Guía prevista para la implementación. El repositorio aún no contiene aplicación Python ni suite pytest; estos comandos describen el flujo de validación que deberá quedar disponible al implementar. Este plan no instala dependencias ni ejecuta pruebas de producto.

## Prerrequisitos

- Python 3.11+ y `uv` o un entorno virtual Python equivalente.
- Google Cloud SDK (`gcloud`) solo para las pruebas de integración opcionales con servicios reales.
- Proyecto/región Vertex habilitados y permisos IAM mínimos para Vertex AI, el bucket RAG y Secret Manager.
- Bucket privado con fuentes aprobadas, vigentes y sin PQRS/datos personales.
- Modelo Gemini GA seleccionado y registrado en configuración. `text-embedding-004` debe seguir disponible en la región prevista; el ciclo de vida consultado anuncia retiro el 2027-04-01.
- Spec aprobada antes de iniciar la implementación.

## Preparar el entorno local

Una vez creada la aplicación y su manifiesto de dependencias:

```powershell
uv sync --extra test
```

Configurar solo identificadores no secretos en el entorno (`GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `RAG_BUCKET`, `GEMINI_MODEL_ID`, `EMBEDDING_MODEL_ID=text-embedding-004`, y referencias de Secret Manager). No guardar claves JSON o secretos en el repositorio. Para acceso local a Google Cloud usar ADC:

```powershell
gcloud auth application-default login
```

La autenticación no habilita a transmitir contenido de PQRS: las pruebas deben confirmar que Vertex recibe únicamente taxonomía fija y pasajes aprobados.

## Ejecutar la suite de aceptación

```powershell
uv run pytest -q
```

La implementación debe exponer el conjunto de aceptación sintético en `tests/evaluation/fixtures/pqrs_40.jsonl` o formato equivalente y la medición en `tests/evaluation/test_acceptance_40.py`. La suite local no requiere credenciales Google: usa dobles para Vertex, GCS y Secret Manager.

Resultado esperado:

- Se cargan al menos 40 PQRS sintéticas con tipo de referencia cubriendo Petición, Queja, Reclamo y Sugerencia.
- La métrica se calcula sobre la predicción del motor local configurado: `aciertos_tipo / total_casos`; pytest falla si es menor que `0.85`.
- Entradas sin datos, contradictorias, con confianza <0,70, taxonomía desconocida o salida inválida se marcan para revisión manual.
- Sin fuente aprobada pertinente, `estado` es exactamente `sin fundamento`, `revision_requerida=true` y `bloqueado_para_liberacion=true`.
- Ningún flujo permite liberar o enviar borradores; no existe endpoint `/enviar`.
- Al menos el 80% de las personas revisoras califica como empático y claro el borrador fundamentado con puntuación ≥4/5; conservar solo conteos/promedios agregados, nunca el texto de PQRS o borradores en logs.
- Marcadores sintéticos de texto, PII, resumen y borrador no aparecen en payloads de Vertex, objetos GCS del índice ni logs capturados.
- Fallos simulados de Vertex/GCS/Secret Manager terminan en abstención/revisión, sin respuesta no fundamentada.

## Verificar contrato HTTP

Con el servidor local ejecutándose en otra terminal, consultar el documento OpenAPI generado por FastAPI y verificar los contratos definidos en [`contracts/openapi.yaml`](contracts/openapi.yaml):

```powershell
Invoke-RestMethod http://127.0.0.1:8000/openapi.json
Invoke-RestMethod http://127.0.0.1:8000/salud
```

Las rutas POST se validan primero mediante `TestClient` y fixtures sintéticos para no copiar datos de caso al historial de la terminal. `GET /salud` no debe activar inferencias ni incluir secretos.

## Integración cloud opcional

Solo después de la suite local y con corpus no sensible aprobado:

1. Verificar ADC, permisos de mínimo privilegio y acceso a versiones fijadas de Secret Manager.
2. Comprobar lectura del manifiesto/índice desde el bucket privado y consistencia entre modelo, versión y dimensión de embeddings.
3. Ejecutar una consulta controlada construida con taxonomía fija; inspeccionar que el payload a Vertex no incluye marcadores del texto sintético ni valores del caso.
4. Verificar que errores de permisos, red o modelo no producen borrador liberable.

No usar PQRS reales en esta validación. Los logs de evidencia deben guardar únicamente resultado, códigos y métricas agregadas.
