# Metodología Nebula Score® Coffee V1

## Identificación

- Producto: coffee
- Versión: 1.0.0
- Estado: experimental
- Archivo: `methodologies/coffee/v1.json`

## Ponderación general

```text
Nebula Score Coffee =
0.60 × Sensory Score
+ 0.30 × Process Score
+ 0.10 × Integrity Score
− Penalties
```

El resultado se limita al rango `[0, 100]`.

## Componente sensorial

- Variable de entrada: `sca_score` (0–100).
- Normalización:

```text
Sensory Score = clamp((SCA − 80) / 20, 0, 1) × 100
```

- SCA < 80 produce Sensory Score 0.
- SCA > 100 se clampa a 100.
- La función de normalización es reemplazable en versiones futuras mediante configuración metodológica.

## Componente de proceso

### Essential

Variables: `temperature`, `pH`, `ORP`.

```text
Process Score Essential =
0.35 × Temperature Index
+ 0.35 × pH Index
+ 0.30 × ORP Index
```

Capacidad máxima de confianza: 2.

### Insight

Variables: `temperature`, `pH`, `ORP`, `anaerobic`, `homogeneity`.

```text
Process Score Insight =
0.20 × Temperature Index
+ 0.20 × pH Index
+ 0.15 × ORP Index
+ 0.40 × Anaerobic Index
+ 0.05 × Homogeneity Index
```

Capacidad máxima de confianza: 4.

### Signature

Variables: `temperature`, `pH`, `ORP`, `anaerobic`, `biology`, `homogeneity`.

```text
Process Score Signature =
0.15 × Temperature Index
+ 0.15 × pH Index
+ 0.10 × ORP Index
+ 0.35 × Anaerobic Index
+ 0.20 × Biology Index
+ 0.05 × Homogeneity Index
```

Capacidad máxima de confianza: 5.

## Componente de integridad

```text
Integrity Score =
0.60 × Mass Balance Score
+ 0.40 × Documentation and Evidence Score
```

## Confidence Level

```text
Confidence Level = min(
  equipment_capability,
  plan_capability,
  evidence_quality
)
```

### Planes OriginBlok®

- Freemium: máximo 1
- Basic: máximo 2
- Pro: máximo 4
- Enterprise: máximo 5

## Clasificación de resultados

| Rango mínimo | Clasificación |
| --- | --- |
| 85 | Sobresaliente |
| 70 | Avanzado |
| 55 | Competente |
| 40 | En desarrollo |
| 0 | Insuficiente |

## Penalizaciones

Cada penalización incluye código, nombre, categoría, severidad, valor deducido, variable afectada, justificación y si es revisable manualmente. El total se suma y se limita para que el Nebula Score final no sea negativo.

Categorías iniciales:

- Process deviation
- Missing data
- Sensor integrity
- Calibration
- Traceability
- Mass balance
- Documentation
- Sensory inconsistency
- Manual override
- Critical failure

## Advertencia metodológica

Nebula Score® Coffee V1 es un modelo técnico en validación. Las ponderaciones, bandas y fórmulas deben validarse con datos reales antes de usarse como estándar certificado. La integridad criptográfica demuestra que un registro no fue alterado, pero no garantiza por sí sola la corrección del dato original.
