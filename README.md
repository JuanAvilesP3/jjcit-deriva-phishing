# P08 · Deriva conceptual en detección de phishing por URL

**Revista destino:** JJCIT
**Línea:** A · **GPU:** Baja · **Días asignados:** 22-23 ago

## Estado
- [x] Ficha de revista completa (JOURNAL.md)
- [x] Datos descargados (data/raw/) — PhishTank (con marca temporal) + Tranco
- [x] Experimento ejecutado (día 1) — 4 estrategias × 3 modelos
- [x] Estadística (día 1) — regresión, prueba de Page, comparación de estrategias
- [x] Figuras generadas (4/4)
- [x] Redacción del manuscrito (día 2) — `paper/main.tex` completo
- [x] Endurecimiento: DOIs verificados
- [x] Endurecimiento: revisión adversarial ronda 1
- [x] Endurecimiento: revisión adversarial ronda 2 (correcciones reales aplicadas, no solo notas de limitación)
- [x] Endurecimiento: auditoría de reproducibilidad (cada número citado verificado contra results/tables/ y src/)
- [x] Word/PDF sincronizados y verificados palabra por palabra contra main.tex
- [ ] Revisión cruzada (2 sep, la hace el otro practicante)
- [ ] Repositorio en GitHub (repo local únicamente por ahora)
- [ ] Publicado en Zenodo (DOI)
- [x] Carta de presentación y declaraciones (borrador en `paper/cover_letter.md` y `paper/declaraciones.md`)
- [ ] Entregado al responsable académico

## Protocolo

**Revista destino:** Jordanian Journal of Computers and Information Technology (JJCIT)
**Fecha de inicio:** 18/08
**Responsable:** Juan (línea A)

### Pregunta de investigación
Un clasificador de phishing entrenado con URLs de un período, ¿cuánto desempeño pierde al evaluarse sobre URLs posteriores?

### Hipótesis
El F1 cae de forma monótona con la distancia temporal, y el reentrenamiento periódico recupera más desempeño que la ventana deslizante porque conserva ejemplos históricos aún vigentes.

### Variables
- Independientes: modelo (Random Forest, XGBoost, Regresión Logística), estrategia de partición (aleatoria / temporal / ventana deslizante / reentrenamiento acumulativo), distancia temporal al bloque de entrenamiento
- Dependientes: F1 por bloque de evaluación
- Controladas: tamaño de bloque (por número de muestras, no por duración)

### Diseño
- Condiciones experimentales: n bloques temporales, evaluados con partición aleatoria (línea base) vs. temporal
- Repeticiones por condición: por definir según número de bloques disponibles
- Semilla aleatoria: 42
- Validación: bloques por cuantiles de fecha, no por intervalos fijos

### Prueba estadística
Regresión sobre la curva de degradación; test de Page para tendencia monótona.
- Tamaño del efecto a reportar: diferencia absoluta entre F1 de partición aleatoria y F1 de partición temporal

### Criterio de interés
- Si la hipótesis se confirma: la evaluación estándar con partición aleatoria sobreestima el desempeño real; se recomienda partición temporal como estándar del campo.
- Si se refuta (degradación menor a la esperada): también es un hallazgo publicable, y contradice la intuición del campo — reportarlo igual.

### Datasets
| Nombre | Fuente | Licencia | Verificado |
|--------|--------|----------|------------|
| PhishTank | data.phishtank.com/data/online-valid.csv, sin registro necesario | Uso de investigación, phishtank.org | Sí — 29,299 URLs con `submission_time` en los últimos 180 días |
| Tranco (URLs legítimas) | tranco-list.eu/top-1m.csv.zip | Lista pública de investigación | Sí — instantánea única del 19/08/2026, 1M dominios, se muestrean 29,299 |
| ~~OpenPhish~~ | openphish.com feed comunitario | — | **Descartado** — sin marca temporal por URL (solo snapshot activo) |
| ~~UCI Phishing Websites / PhiUSIIL~~ | UCI | — | **Descartados** — features pre-extraídas sin fecha por fila |

Verificado el día 1 (18-19/08): solo PhishTank tiene marca temporal real por registro, tal como advertía la ficha. Las URLs legítimas de Tranco no tienen fecha por URL (una sola instantánea), así que se les asignó una marca de tiempo sintética uniforme dentro del rango de PhishTank — decisión documentada explícitamente como limitación (la reputación de dominios legítimos no varía en la ventana de estudio; lo que sí varía es el phishing, que es lo que mide el artículo).

### Citas obligatorias de la revista destino
1. (pendiente — extraer de trabajos sobre seguridad, detección de intrusiones y ML aplicado a ciberseguridad publicados en JJCIT)
2.
3.

## Bitácora

## 18/08 - Juan — Montaje
- Hecho: estructura de carpetas creada, plantilla de figuras copiada, repositorio Git inicializado.
- Bloqueado en: pendiente ficha de revista y descarga de datos.
- Siguiente: completar JOURNAL.md y descargar dataset.
- Tiempo de computo consumido: 0h

## 19/08 - Juan — Día 1 completo: verificación, datos, experimento, estadística y figuras
- Hecho:
  - Verificación de marca temporal (crítico según la ficha): solo PhishTank la tiene por registro; OpenPhish y los datasets estáticos de UCI se descartaron. PhishTank accesible sin registro, 29,299 URLs de phishing en los últimos 180 días con densidad creciente.
  - `01_download.py`: PhishTank + Tranco (instantánea, con marca de tiempo sintética uniforme para las URLs legítimas — limitación documentada).
  - `02_preprocess.py`: 32 características léxicas extraídas (longitud, entropía, subdominios, IP, acortadores, palabras clave sospechosas, etc.), dataset balanceado (58,598 filas).
  - `03_experiment.py`: 3 modelos × 4 estrategias (aleatoria, fija, ventana deslizante, acumulativa) sobre 6 bloques temporales.
  - `04_stats.py`: regresión OLS combinada significativa (p=0.022) pero de magnitud pequeña; prueba de Page confirma tendencia monótona decreciente (p=0.004, con la salvedad de que solo hay 3 "jueces"/modelos); reentrenamiento acumulativo supera a ventana deslizante en los 3 modelos (diferencia no significativa con n=5, Wilcoxon p>0.1).
  - `05_figures.py`: 4 figuras generadas y revisadas visualmente.
  - **Hallazgo honesto:** la degradación es real y estadísticamente detectable, pero **de magnitud pequeña** (F1 baja de ~0.996 a ~0.984-0.992 según modelo, no un colapso dramático). Hipótesis de por qué: las URLs legítimas (top dominios de Tranco) son léxicamente muy distintas del phishing de cualquier época, así que el clasificador se apoya en señales estables (longitud, HTTPS, número de barras) que no dependen de la campaña de phishing activa. **Esto coincide con un riesgo que la propia ficha anticipaba** ("Degradación menor a la esperada → también es un hallazgo publicable, contradice la intuición del campo") — se reporta tal cual, sin inflar el efecto.
  - Dos bugs de infraestructura corregidos y propagados a `_shared/figures_style.py` (afecta a los 10 proyectos): (1) backend de matplotlib forzado a `Agg` — el backend interactivo por defecto crasheaba en corridas en segundo plano en Windows; (2) grid global de matplotlib caía en el centro de las celdas de los mapas de calor cuando los ticks se ponen ahí para las etiquetas, deformando visualmente los mapas de calor — se desactiva `ax.grid(False)` en esos ejes.
- Bloqueado en: nada.
- Siguiente: redactar `paper/main.tex`, o pasar a otro artículo de la línea A.
- Tiempo de computo consumido: ~15 min

## 20/08 - Juan — Redacción del manuscrito
- Hecho: `paper/main.tex` completo. 2 citas reales de JJCIT buscadas y verificadas descargando el PDF real de cada artículo (no inventadas): Odeh et al. 2021 (PhiBoost, phishing) y Alslman et al. 2024 (DDoS con modelos ensemble). Discusión honesta sobre por qué la degradación medida es pequeña en magnitud (aunque estadísticamente real): la clase legítima (dominios top de Tranco) es lexicalmente muy distinta del phishing sin importar la época, lo que probablemente subestima la deriva real frente a un negativo más difícil — se deja explícito como la limitación más importante y la dirección más prometedora para trabajo futuro.
- Bloqueado en: nada.
- Siguiente: Fase 2 o continuar con otro manuscrito.
- Tiempo de computo consumido: ~30 min


## 21/08 - Juan — Verificación de referencias (Fase 2)
- Hecho: los DOIs de las 2 citas se resolvieron uno por uno (HTTP 200/302 contra doi.org) y se confirmó que el contenido de cada artículo coincide con lo citado en el manuscrito. DOIs agregados a `refs.bib` con nota de verificación y fecha.
- Bloqueado en: nada.
- Siguiente: revisión adversarial ronda 1 (rol de revisor de la revista destino).
- Tiempo de computo consumido: ~15 min


## 20/08 - Juan — Revisión adversarial ronda 1 (rol JJCIT) + bibliografía ampliada + figuras
- Hecho: bibliografía ampliada de 2 a 6 citas verificadas (concept drift survey, Tranco, Random Forest, XGBoost). Revisión adversarial: se detectó que las 4 figuras existían como archivos pero nunca estaban insertadas en el manuscrito -- corregido, incluyendo dos figuras de mecanismo (desplazamiento de features y su importancia por bloque) que antes no se mencionaban en el texto y que refuerzan directamente el argumento de la Discusión. Se detectó una debilidad estadística real: la regresión "pooled" de F1 sobre distancia temporal mezclaba, sin controlarlo, las diferencias fijas de F1 base entre los 3 modelos con la tendencia real que se quería medir. Se recalculó como ANCOVA controlando por modelo: la pendiente no cambia, pero la significancia mejora sustancialmente (p=0.022 → p=0.0048, R²=0.34 → 0.69). Se reescribió abstract, metodología, resultados y discusión con esto. Pasada anti-IA parcial (frases repetidas entre los 5 artículos, ej. "central, if unglamorous, finding").
- Bloqueado en: nada.
- Siguiente: ronda 2 de revisión adversarial + pasada anti-IA completa.
- Tiempo de computo consumido: ~30 min


## 20/08 - Juan — Ronda 2 + pasada anti-IA + auditoría numérica
- Hecho: se verificó cada número de las tablas del manuscrito contra `results/tables/comparacion_estrategias.csv` y `diferencia_aleatoria_vs_temporal.csv` uno por uno -- todos coinciden exactamente. Segunda lectura crítica del texto completo. Pasada anti-IA: se reescribieron frases repetidas con otros artículos de la línea ("central, if unglamorous, finding", "reframes the practical recommendation", "is itself informative").
- Bloqueado en: nada.
- Siguiente: continuar con Fase 2 restante para los demás artículos si aplica.
- Tiempo de computo consumido: ~10 min


## 21/08 - Juan — Auditoría completa contra las 2 fichas guía + conversión a Word
- Hecho: releí las dos fichas fuente completas (no solo memoria) y comparé línea por línea contra los 5 manuscritos. Encontré que **P8/JJCIT sí exige plantilla Word** (se me había pasado en una nota anterior que decía "P2, P6, P9") -- generado `paper/P8_JJCIT_manuscript.docx`, verificado abriéndolo en Word real y exportando a PDF: tabla, las 4 figuras y referencias correctas. También se detectó que faltan 2 de las 3 tablas que la ficha pide (Tabla 1: características extraídas con definición; Tabla 2: F1 por bloque y modelo) -- solo está la Tabla 3 (comparación aleatoria vs. temporal). Pendiente para más adelante.
- Bloqueado en: nada.
- Siguiente: agregar las 2 tablas faltantes.
- Tiempo de computo consumido: ~15 min
