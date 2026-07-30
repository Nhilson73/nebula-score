# Metodología Nebula Score® Cacao V1

## Resumen

Nebula Score® Cacao V1 agrega a la plataforma la evaluación de lotes de **cacao fino de aroma**, utilizando la misma arquitectura de motor genérico de Nebula Score® Coffee pero con variables, ponderaciones y una curva de normalización propias del cacao.

```text
Nebula Score Cacao =
0.60 × Calidad sensorial
+ 0.30 × Proceso de fermentación y post-cosecha
+ 0.10 × Integridad
− Penalizaciones
```

El resultado final se limita al rango `[0, 100]`.

## Componente sensorial

- Variable de entrada: `quality_input` (0–100). Para Cacao representa una puntuación combinada de **licor de cacao / corte de grano**.
- Normalización propuesta:

```text
Sensory Score = clamp((licor − 60) / 40, 0, 1) × 100
```

- Un cacao con puntuación de licor 60 obtendría score sensorial 0; con 100 obtendría 100.
- Esta curva es **experimental** y debe validarse con paneles de cata de cacao y estándares de ICCO / WCF.

## Proceso de fermentación y post-cosecha

Se ofrecen tres modelos de instrumentación, heredados de la filosofía Essential / Insight / Signature:

### Essential

```text
P = 0.35T + 0.35pH + 0.30Brix
```

- `temperature`: índice de temperatura de la masa fermentante (T).
- `ph`: índice de pH del mosto / miel de cacao.
- `brix`: índice de sólidos solubles totales de la pulpa (Brix).

Capacidad de confianza del equipo: 2.

### Insight

```text
P = 0.20T + 0.20pH + 0.15Brix + 0.40A + 0.05H
```

- `anaerobic`: índice de control de anaerobiosis (A).
- `homogeneity`: índice de homogeneidad de la masa y volteos (H).

Capacidad de confianza: 4.

### Signature

```text
P = 0.15T + 0.15pH + 0.10Brix + 0.30A + 0.20B + 0.05H + 0.05D
```

- `biology`: índice biológico / genética y perfil microbiano (B).
- `drying`: índice de control del secado (D), proxy de la curva de humedad y estabilidad.

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

La metodología vive en `methodologies/cacao/v1.json` y se carga en runtime, garantizando que evaluaciones históricas conserven la versión usada.

## Limitaciones y trabajo futuro

- La curva de normalización 60–100 es experimental.
- `biology` y `drying` son índices proxy; en versiones posteriores podrían reemplazarse por mediciones reales de humedad, genética o perfil microbiológico.
- No se incluye aún la distinción entre lote de grano seco y lote de chocolate.
- El modelo no sustituye certificaciones oficiales ni evaluaciones de cata profesionales.
