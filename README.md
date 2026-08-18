# P08 · Deriva conceptual en detección de phishing por URL

**Revista destino:** JJCIT
**Línea:** A · **GPU:** Baja · **Días asignados:** 22-23 ago

## Estado
- [ ] Ficha de revista completa (JOURNAL.md)
- [ ] Datos descargados (data/raw/)
- [ ] Experimento ejecutado (día 1)
- [ ] Redacción y figuras (día 2)
- [ ] Endurecimiento: DOIs verificados
- [ ] Endurecimiento: revisión adversarial ronda 1
- [ ] Endurecimiento: revisión adversarial ronda 2
- [ ] Revisión cruzada
- [ ] Repositorio en GitHub
- [ ] Publicado en Zenodo (DOI)
- [ ] Carta de presentación y declaraciones
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
| PhishTank | phishtank.org, con marca temporal | Verificar | No |
| OpenPhish | openphish.com, con marca temporal | Verificar | No |
| UCI Phishing Websites | UCI | Verificar | No |
| PhiUSIIL | Verificar fuente | Verificar | No |
| Tranco / Majestic Million (URLs legítimas) | tranco-list.eu / majestic.com | Verificar | No |

Crítico: verificar el día 1 que el dataset tenga marca temporal utilizable — si no la tiene, no sirve para este diseño.

### Citas obligatorias de la revista destino
1. (pendiente — extraer de trabajos sobre seguridad, detección de intrusiones y ML aplicado a ciberseguridad publicados en JJCIT)
2.
3.

## Bitácora

## 18/08 - Montaje
- Hecho: estructura de carpetas creada, plantilla de figuras copiada, repositorio Git inicializado.
- Bloqueado en: pendiente ficha de revista y descarga de datos.
- Siguiente: completar JOURNAL.md y descargar dataset.
- Tiempo de computo consumido: 0h
