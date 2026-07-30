# Nebula Score®

Plataforma multiproducto para calcular y documentar el **Nebula Score®** de café, cacao y vino. Integra calidad sensorial, control del proceso de fermentación e integridad de la evidencia en una puntuación verificable de 0 a 100.

> **Estado metodológico:** Nebula Score® Coffee V1 es un modelo técnico en validación. No sustituye certificaciones oficiales, cataciones profesionales ni análisis de laboratorios acreditados.

## Arquitectura

- **Backend:** Python · FastAPI · Pydantic · SQLAlchemy · SQLite (desarrollo), preparado para PostgreSQL.
- **Frontend:** React · TypeScript · Vite.
- **Métodos:** Configuración versionada en `methodologies/` como JSON validable.
- **Contenedores:** Docker Compose para levantar backend y frontend.

```text
nebula-score/
├── backend/           # API y motores de puntuación
│   ├── app/
│   │   ├── api/       # Rutas FastAPI
│   │   ├── core/      # Motor genérico, normalización, penalizaciones, confianza
│   │   ├── models/    # Modelos SQLAlchemy
│   │   ├── products/  # Motores por producto (coffee)
│   │   ├── schemas/   # Pydantic request/response
│   │   └── services/  # Lógica de negocio
│   ├── tests/         # Pruebas pytest
│   └── Dockerfile
├── frontend/          # Interfaz React
├── methodologies/     # Definiciones metodológicas versionadas
├── docs/              # Documentación técnica y funcional
├── docker-compose.yml
└── pyproject.toml
```

## Requisitos

- Python 3.11+
- Node.js 20+ (para frontend)
- Docker y Docker Compose (opcional)

## Configuración local

1. Clonar el repositorio.
2. Copiar el archivo de ejemplo de entorno:

```bash
cp .env.example .env
```

3. Crear un entorno virtual e instalar dependencias del backend:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

4. Iniciar el backend:

```bash
python -m backend.app.main
```

El API estará disponible en `http://localhost:8000`. La documentación OpenAPI está en `http://localhost:8000/docs`.

5. En otra terminal, instalar y ejecutar el frontend:

```bash
cd frontend
npm install
npm run dev
```

La interfaz estará en `http://localhost:5173`.

## Docker Compose

```bash
docker compose up --build
```

- Frontend: `http://localhost`
- Backend: `http://localhost:8000`

## Pruebas

Backend:

```bash
source .venv/bin/activate
PYTHONPATH=. pytest backend/tests -v
```

Frontend:

```bash
cd frontend
npm run test
```

Lint y tipado del backend:

```bash
source .venv/bin/activate
ruff check backend
mypy -p backend
```

## Métodos y productos

La plataforma soporta múltiples productos. Cada producto tiene su metodología versionada en `methodologies/<producto>/<version>.json`. La única metodología disponible en V1 es:

- `methodologies/coffee/v1.json` — Nebula Score® Coffee V1

Cada evaluación almacena el `methodology_id` y `methodology_version` con los que fue calculada, garantizando reproducibilidad histórica.

## Fórmula Nebula Score® Coffee V1

```text
Nebula Score Coffee =
0.60 × Sensory Score
+ 0.30 × Process Score
+ 0.10 × Integrity Score
− Penalties
```

- **Sensory Score:** `clamp((SCA − 80) / 20, 0, 1) × 100` para SCA entre 0 y 100.
- **Process Score:** ponderado según el modelo de fermentación: Essential, Insight o Signature.
- **Integrity Score:** `0.60 × Mass Balance + 0.40 × Documentation/Evidence`.
- **Penalties:** lista deducible con categorías configurables.
- **Confidence Level:** `min(equipment_capability, plan_capability, evidence_quality)` en escala 0–5.

## API principal

Rutas bajo `/api/v1`:

- `GET /api/v1/products`
- `GET /api/v1/methodologies`
- `GET /api/v1/methodologies/{product}/{version}`
- `GET /api/v1/evaluations`
- `GET /api/v1/evaluations/{id}`
- `POST /api/v1/evaluations`
- `PUT /api/v1/evaluations/{id}`
- `POST /api/v1/evaluations/{id}/calculate`
- `GET /api/v1/evaluations/{id}/report`
- `POST /api/v1/import/csv`
- `POST /api/v1/import/json`
- `GET /api/v1/export/csv`

## Estado del proyecto

- Coffee V1: implementado y cubierto por pruebas.
- Cacao V1 y Wine V1: preparados en la arquitectura; su desarrollo comienza tras la validación de Coffee V1.

## Marcas y propiedad

Nebula Score®, Nebula Fermentation® y Nebula OriginBlok® son conceptos y marcas del ecosistema Nebula.
