# Changelog

## [1.1.0] — 2026-07-30

### Added

- Metodología Nebula Score® Cacao V1 en `methodologies/cacao/v1.json`.
- Motor de Cacao (`backend/app/products/cacao/engine.py`) con modelos Essential, Insight y Signature adaptados a fermentación de cacao.
- Selector de producto en el frontend para alternar entre Coffee y Cacao.
- Soporte de evaluación para cacao en la API: `product` en `EvaluationCreate` y carga dinámica de metodología.
- Tests del motor de Cacao y de la API para evaluaciones cacao.

### Changed

- Campo `sca_score` renombrado a `quality_input` en modelo, esquemas, motor y frontend para hacer el motor agnóstico del producto.
- `EvaluationForm` y `ResultView` usan el label y fórmula de calidad definidos por la metodología activa.
- Dashboard muestra la columna Producto para evaluaciones mixtas.

## [1.0.0] — 2026-07-30

### Added

- Plataforma base multiproducto con arquitectura modular.
- Motor de puntuación genérico: normalización, penalizaciones, confianza e integridad.
- Motor específico para Nebula Score® Coffee V1 con modelos Essential, Insight y Signature.
- Metodología Coffee V1 en `methodologies/coffee/v1.json` con pesos, límites y bandas configurables.
- API REST FastAPI versionada bajo `/api/v1` con documentación OpenAPI.
- Modelo de datos SQLAlchemy para evaluaciones, auditoría y trazabilidad.
- Importación CSV y JSON de evaluaciones.
- Exportación CSV y JSON de resultados.
- Frontend React + TypeScript + Vite con dashboard, formulario de evaluación y vista de resultados.
- Interfaz responsive basada en la identidad visual de la versión estática anterior.
- Docker Compose para despliegue local de backend y frontend.
- Pruebas unitarias e integración del motor y la API con pytest.
- Pruebas de utilidad frontend con vitest.
- Linting con ruff y verificación de tipos con mypy para el backend.

### Changed

- La calculadora estática original (`index.html`, `app.js`, `styles.css`) se migra a `archive/static-v1/` como referencia. Su lógica se incorpora en la metodología Coffee V1.

### Removed

- Aplicación estática pura de la raíz; ahora la interfaz es una SPA React alimentada por el backend.
