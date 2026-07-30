# Nebula Score®

Aplicación web para calcular y documentar **Nebula Score® Coffee V1**, un índice compuesto que integra:

- **60% calidad sensorial**
- **30% desempeño del proceso de fermentación**
- **10% integridad de la evidencia**
- **Penalizaciones aplicables**

## Fórmula

```text
Nebula Score = 0.60 × Sensory Score
             + 0.30 × Process Score
             + 0.10 × Integrity Score
             − Penalizaciones
```

La normalización sensorial V1 usa:

```text
Sensory Score = clamp((SCA − 80) / 20, 0, 1) × 100
```

## Modelos de proceso

### Essential

```text
P = 0.35T + 0.35pH + 0.30ORP
```

### Insight

```text
P = 0.20T + 0.20pH + 0.15ORP + 0.40A + 0.05H
```

### Signature

```text
P = 0.15T + 0.15pH + 0.10ORP + 0.35A + 0.20B + 0.05H
```

Donde:

- `T`: índice de temperatura
- `pH`: índice de comportamiento del pH
- `ORP`: índice de potencial óxido-reducción
- `A`: índice de anaerobiosis
- `B`: índice biológico
- `H`: índice de homogeneidad

## Uso local

No requiere instalación. Abra `index.html` en un navegador moderno.

También puede servir la carpeta con Python:

```bash
python -m http.server 8000
```

Luego abra `http://localhost:8000`.

## Alcance de esta versión

Esta versión implementa el calculador para **café**. Las próximas variantes previstas son:

1. Nebula Score® Cacao
2. Nebula Score® Wine

La arquitectura de cálculo está separada por producto para permitir diferentes variables, curvas, ponderaciones y escalas sensoriales.

## Estado metodológico

Nebula Score® Coffee V1 es un modelo técnico en validación. Las penalizaciones, bandas comerciales, reglas de descalificación y normalización sensorial deben validarse con datos reales antes de presentarse como estándar certificado.

## Propiedad

Nebula Score®, Nebula Fermentation® y Nebula OriginBlok® son conceptos y marcas del ecosistema Nebula. Todo uso comercial debe respetar la titularidad y las políticas aplicables.
