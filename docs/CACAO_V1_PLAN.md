# Plan — Nebula Score® Cacao V1

## Objetivo
Extender la plataforma **Nebula Score®** para soportar cacao fino de aroma, reutilizando la arquitectura web de Coffee V1 y adaptando variables, modelos y nomenclatura al cacao.

## Referencias
- `CacaoOps/PLAN_CACAO.md` — adaptación conceptual CafeOps → CacaoOps.
- `CacaoOps/manuscript.es.md` — capítulos sobre FermentOps, secado, tueste y trazabilidad.
- `cafelium-web/app/i18n/es.json` — conceptos NOB Score / NOB SaaS.
- `methodologies/coffee/v1.json` — patrón de metodología versionada a replicar.

## Alcance V1

### 1. Metodología Cacao V1
Archivo: `methodologies/cacao/v1.json`

```text
Nebula Score Cacao =
0.60 × Calidad sensorial
+ 0.30 × Proceso de fermentación y post-cosecha
+ 0.10 × Integridad
− Penalizaciones
```

- **Calidad sensorial:** puntuación de licor/corte (`liquor_score`) entre 0 y 100.
  - Normalización propuesta: `clamp((liquor_score − 60) / 30, 0, 1) × 100`.
  - Rango de entrada: 0–100; un cacao "fine flavour" suele partir de ~60.
  - Esta curva es experimental y debe validarse con cata real.

- **Proceso de fermentación y post-cosecha:** tres modelos de instrumentación.

  - **Essential** — Cajón/saco/tina básica.
    ```text
    P = 0.35T + 0.35pH + 0.30Brix
    ```
    Variables: `temperature`, `ph`, `brix`. Capacidad de confianza: 2.

  - **Insight** — Cajón/saco con volteos y anaerobiosis.
    ```text
    P = 0.20T + 0.20pH + 0.15Brix + 0.40A + 0.05H
    ```
    Variables: `temperature`, `ph`, `brix`, `anaerobic`, `homogeneity`. Capacidad: 4.

  - **Signature** — Fermentación controlada + secado y biología.
    ```text
    P = 0.15T + 0.15pH + 0.10Brix + 0.30A + 0.20B + 0.05H + 0.05D
    ```
    Variables: `temperature`, `ph`, `brix`, `anaerobic`, `biology`, `homogeneity`, `drying`. Capacidad: 5.

- **Integridad:** `0.60 × Mass Balance + 0.40 × Documentation/Evidence`.
  - Considerar añadir `varietal_trace` en V1.1; para V1 se mantiene el mismo par `mass_balance` / `documentation`.

- **Confidence Level:** `min(equipment_capability, plan_capability, evidence_quality)` con los mismos planes de Coffee.

- **Clasificación:** mismas bandas de Coffee V1 (Sobresaliente ≥ 85, Avanzado ≥ 70, Competente ≥ 55, En desarrollo ≥ 40, Insuficiente < 40).

- **Penalizaciones:** mismas categorías de Coffee V1, con pesos y severidad configurables.

### 2. Cambios en backend

- **Motor genérico:** renombrar `sca_score` → `quality_input` en `evaluate()` para que no esté atado al café.
  - `Evaluation.sca_score` pasa a `quality_input` (raw) y `quality_score` (normalizado) se mantiene.
  - `EvaluationResponse` y `EvaluationCreate` usan `quality_input`.
  - Para Coffee V1, el `input_variable` en `methodologies/coffee/v1.json` se actualiza a `quality_input` con label "SCA score".
  - Para Cacao V1, `input_variable` es `liquor_score` con label "Puntuación de licor / corte".

- **Producto cacao:**
  - `backend/app/products/cacao/engine.py` — adaptador que carga `methodologies/cacao/v1.json` y llama a `evaluate()`.
  - `backend/app/products/cacao/__init__.py`.

- **API:**
  - `GET /api/v1/products` marcará `cacao` como `available: true`.
  - Los endpoints de evaluaciones ya son agnósticos de producto; solo necesitan la metodología correcta.

- **Servicios:**
  - `evaluation_service.py` usa `quality_input` en lugar de `sca_score`.
  - `import_service.py` acepta `quality_input` o `liquor_score`/`sca_score` como alias en CSV/JSON.
  - `report_service.py` sin cambios sustanciales.

- **Tests:**
  - `backend/tests/test_cacao_engine.py` con casos perfectos, límites, penalizaciones, confianza.
  - `backend/tests/test_api.py` añadir un caso cacao y verificar que `/api/v1/products` incluye cacao.

### 3. Cambios en frontend

- **Tipos (`frontend/src/types.ts`):**
  - Renombrar `sca_score` por `quality_input` en `EvaluationInput` y `EvaluationResult`.
  - `Methodology.quality` incluye `input_variable` y `formula`.

- **Componentes:**
  - `EvaluationForm.tsx`: usa `methodology.quality.input_variable` como label y genera inputs de proceso según el modelo seleccionado.
  - `ResultView.tsx`: muestra `quality_input` con el label de la metodología.
  - `Dashboard.tsx`: añadir columna **Producto** (coffee / cacao) para distinguir evaluaciones.

- **Páginas/routing:**
  - `App.tsx`: selector de producto al iniciar una evaluación, o detección desde URL.
  - El dashboard listará evaluaciones de todos los productos, filtrable por producto.

- **Build y tests:** `npm run build` y `npm run test` deben seguir pasando.

### 4. Documentación

- `docs/METHODOLOGY_CACAO_V1.md` — fórmulas, variables, modelos, disclaimers.
- `CHANGELOG.md` — entrada V1.1.0 con Cacao V1.
- `README.md` — actualizar lista de productos y endpoints.

### 5. Docker y entorno

- `docker-compose.yml` no requiere cambios.
- `pyproject.toml` sin cambios (misma stack).
- Añadir al blueprint conocimiento de Cacao V1 si se valida.

### 6. Entregables y PR

- Rama: `devin/cacao-v1`.
- PR: `Nebula Score® Cacao — Complete Layer V1` → `main`.
- Criterios: backend tests ≥ 90% cobertura, frontend build OK, Docker Compose levanta, ruff/mypy sin errores, documentación completa.

### 7. Limitaciones y riesgos

- La curva de normalización del licor (60–100) es experimental; debe validarse con paneles de cata de cacao.
- No se incluye secuenciación genética ni análisis de grasa/hora en V1.
- El campo `drying` en Signature es un índice proxy del secado; no reemplaza medición de humedad real.
- La plataforma sigue siendo un modelo técnico en validación, no certificación oficial.

### 8. Secuencia propuesta

1. Aprobar este plan.
2. Renombrar `sca_score` → `quality_input` en backend y frontend (con compatibilidad de alias).
3. Crear `methodologies/cacao/v1.json`.
4. Crear motor Cacao y tests.
5. Actualizar API `products` y frontend product selector.
6. Documentar y crear PR.
