# Metodología Nebula Score® Wine V1

## Resumen

Nebula Score® Wine V1 extiende la plataforma a la evaluación de **vinos de autor / terruño**, usando el motor genérico de Nebula Score® con una metodología propia para fermentación alcohólica, crianza e integridad de evidencia.

```text
Nebula Score Wine =
0.60 × Calidad sensorial
+ 0.30 × Proceso (fermentación y crianza)
+ 0.10 × Integridad
− Penalizaciones
```

El resultado final se limita al rango `[0, 100]`.

## Componente sensorial

- Variable de entrada: `quality_input` (0–100). Representa una puntuación de cata o evaluación OIV del vino.
- Normalización propuesta:

```text
Sensory Score = clamp((cata − 70) / 30, 0, 1) × 100
```

- Un vino con cata 70 obtendría score sensorial 0; con 100 obtendría 100.
- Esta curva es **experimental** y debe validarse con paneles de cata y estándares OIV/DO.

## Proceso: fermentación alcohólica y crianza

Se ofrecen tres modelos de instrumentación Essential / Insight / Signature:

### Essential

```text
P = 0.35T + 0.35pH + 0.30Brix
```

- `temperature`: índice de temperatura de mosto (T).
- `ph`: índice de pH.
- `brix`: índice de azúcar potencial / Brix.

Capacidad de confianza del equipo: 2.

### Insight

```text
P = 0.20T + 0.20pH + 0.15Brix + 0.40M + 0.05H
```

- `maceration`: índice de maceración y contacto piel-mosto (M).
- `homogeneity`: índice de homogeneidad de la masa fermentante (H).

Capacidad de confianza: 4.

### Signature

```text
P = 0.15T + 0.15pH + 0.10Brix + 0.30M + 0.20B + 0.05H + 0.05C
```

- `biology`: índice biológico / levaduras nativas e inoculación (B).
- `cellar`: índice de crianza / élevage y estabilización en bodega (C).

Capacidad de confianza: 5.

## Integridad y confianza

- Integridad: `0.60 × Mass Balance + 0.40 × Documentation/Evidence`.
- Confidence Level: `min(equipment_capability, plan_capability, evidence_quality)`, con los mismos planes de Coffee V1.

## Penalizaciones y clasificación

Se reutilizan las categorías de penalización y las bandas de clasificación de Coffee V1:

- Sobresaliente: ≥ 85
- Avanzado: ≥ 70
- Competente: ≥ 55
- En desarrollo: ≥ 40
- Insuficiente: < 40

## Archivo de metodología

La metodología vive en `methodologies/wine/v1.json` y se carga en runtime, garantizando que evaluaciones históricas conserven la versión usada.

## Limitaciones y trabajo futuro

- La curva de normalización 70–100 es experimental.
- `maceration`, `biology` y `cellar` son índices proxy; en versiones posteriores podrían reemplazarse por mediciones reales de antocianinas, compuestos volátiles, análisis microbiológico o estado de barrica.
- No se incluye aún la distinción entre tipos de vino (tinto, blanco, espumoso).
- El modelo no sustituye certificaciones oficiales ni evaluaciones de cata profesionales.
