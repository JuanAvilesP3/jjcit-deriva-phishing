# Ficha de Instrucciones de Envío — Paper P8
**Proyecto:** Deriva Conceptual en Detección de Phishing por URL (Evaluación Temporal)  
**Marco Institucional:** FIE-ESPOCH 2026 (Planificación Oficial de Producción Científica)  
**Fecha de Actualización:** 28 de septiembre de 2026  

---

## 1. Identificación de la Revista y Política Editorial
- **Revista destino:** *Jordanian Journal of Computers and Information Technology* (JJCIT)
- **Entidad editora:** Princess Sumaya University for Technology (PSUT) / Scientific Research Support Fund (SRSF), Amán, Jordania.
- **ISSN:** 2415-1076 (En línea) | 2413-9351 (Impreso).
- **Indexación oficial:** Scopus (CiteScore 2.5), DOAJ, EBSCO, dblp, Google Scholar.
- **Portal oficial de envíos (Journal Manager):** [http://www.ejmanager.com/my/jjcit](http://www.ejmanager.com/my/jjcit) (acceso desde [https://jjcit.org/page/instructions_authors](https://jjcit.org/page/instructions_authors))
- **Modalidad de revisión por pares:** **Simple Ciego (Single-Blind Peer Review)**. Los revisores evalúan de manera anónima (mínimo 3 evaluadores internacionales), pero el manuscrito incluye los nombres y filiaciones de los autores en la primera página según la clase oficial `articleJJCIT.cls`.
- **Sección en OJS:** **Regular Research Paper**.
- **Cobra APC (Article Processing Charges)?:** **NO ($0 USD)**. Revista 100% Diamond Open Access sin cargos por envío ni procesamiento. Evidencia en `JOURNAL.md`.
- **Requisitos de originalidad:** Se somete a chequeo antiplagio estricto con **iThenticate**. Prohibición de generación de contenido por IA en violación de la ética de investigación.

---

## 2. Metadatos del Manuscrito (para carga en el formulario de envío)

### Título del artículo:
```text
CONCEPT DRIFT IN URL-BASED PHISHING DETECTION: A TEMPORAL EVALUATION
```

### Resumen en inglés (Abstract):
```text
Phishing detectors are almost universally evaluated with random train/test splits, which implicitly assume that a URL's characteristics are exchangeable across time. We test that assumption by training three lexical-feature classifiers (random forest, XGBoost, logistic regression) on 180 days of PhishTank-reported phishing URLs plus a matched sample of legitimate domains, and evaluating them under four temporal designs: a random split (the field's default), training on the earliest block and testing on each subsequent block, a sliding retraining window, and cumulative retraining. All three models achieve F1 above 0.98 in every configuration, and the gap between the random-split baseline and the worst temporally-displaced block is small in absolute terms (0.36 to 0.92 percentage points of F1, model-dependent). A regression of F1 on temporal distance is significant when pooled across models, and its precision improves substantially once model-level baseline differences are controlled for (p=0.022 naive, p=0.0048 controlling for model as a fixed effect); a Page test for a monotonic decreasing trend across the three models as judges agrees (Z = -2.66, p = 0.004). We argue the near-ceiling performance points partly to a design choice rather than a solved problem: removing the four features most associated with how the legitimate class was constructed (is_https, path_length, num_slashes, url_length) drops F1 by 3.3 to 4.1 percentage points across models, confirming that the choice of negative class (well-established top-ranked domains) inflates the reported ceiling; the four ablated features are not the sole source of the near-ceiling result, though the remaining features may still encode the same domain-versus-full-URL asymmetry; a negative class of full legitimate URLs would be needed to settle this.
```

### Palabras clave (Keywords):
```text
Phishing detection, Concept drift, Temporal evaluation, Adversarial machine learning, Lexical features, Cybersecurity
```

---

## 3. Autores y Filiación Institucional Oficial (Orden Estricto)
1. **Juan Pablo Aviles-Esparza** (*Primer Autor y Autor de Correspondencia*)
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `juan.aviles@espoch.edu.ec`
   - *ORCID:* [0009-0007-0058-8069](https://orcid.org/0009-0007-0058-8069)
2. **Italo Javier Tenempaguay-Granizo** (*Coautor*)
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `italo.tenempaguay@espoch.edu.ec`
   - *ORCID:* [0009-0001-5753-4279](https://orcid.org/0009-0001-5753-4279)
3. **Isaac David Torres-Paredes** (*Coautor y Tutor Académico*)
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `isaac.torres@espoch.edu.ec`
   - *ORCID:* [0009-0001-7057-9316](https://orcid.org/0009-0001-7057-9316)

---

## 4. Archivos a Subir en la Plataforma (Paso a Paso)
- **Carga de Manuscrito Principal:**
  - Subir: `P8_JJCIT_manuscript.pdf` (10 páginas compiladas bajo la clase oficial `articleJJCIT.cls` en A4, incluye figuras vectoriales y raster 300 DPI).
  - Opcional/Requerido para producción por JJCIT: `P8_JJCIT_manuscript.docx` (versión Word estructurada según plantilla oficial A4).
- **Archivos Complementarios (Supplementary Files):**
  1. `cover_letter.md` (Carta de presentación formal al Editor en Jefe de JJCIT).
  2. `declaraciones.md` (Declaraciones de autoría CRediT, ética COPE sobre uso de IA, disponibilidad de datos en Zenodo y ausencia de conflictos).
  3. `P08_JJCIT_paquete_envio.zip` (Paquete comprimido con fuentes completas de LaTeX: `main.tex`, `refs.bib`, `articleJJCIT.cls`, `garamond.sty`, subcarpeta `figures/` con las 8 figuras, `README.md`).

---

## 5. Revisores Pares Sugeridos (3 Expertos Internacionales en Ciberseguridad)
1. **Prof. Dr. Ahmad Odeh**  
   - *Filiación:* Department of Cybersecurity, Faculty of Information Technology, Middle East University, Amán, Jordania.  
   - *Correo electrónico:* `aodeh@meu.edu.jo`  
   - *Especialidad:* Detección de phishing, análisis de características en ciberseguridad (autor referente publicado directamente en JJCIT en 2021).
2. **Prof. Dr. Roberto Perdisci**  
   - *Filiación:* School of Computing, University of Georgia, Athens, GA, EE. UU.  
   - *Correo electrónico:* `perdisci@cs.uga.edu`  
   - *Especialidad:* Seguridad de redes, detección de dominios y tráfico malicioso a gran escala.
3. **Prof. Dr. Feargus Pendlebury**  
   - *Filiación:* Department of Informatics, King's College London, Londres, Reino Unido.  
   - *Correo electrónico:* `feargus.pendlebury@kcl.ac.uk`  
   - *Especialidad:* Evaluación temporal y deriva conceptual en aprendizaje automático para ciberseguridad (creador del marco metodológico Tesseract, USENIX Security 2019).

---

## 6. Enlaces de Reproducibilidad y Datos Abiertos
- **Repositorio público en GitHub:** [https://github.com/JuanAvilesP3/jjcit-deriva-phishing.git](https://github.com/JuanAvilesP3/jjcit-deriva-phishing.git)
- **Depósito permanente en Zenodo:** [https://doi.org/10.5281/zenodo.23005762](https://doi.org/10.5281/zenodo.23005762) (DOI: `10.5281/zenodo.23005762`).

---

## 7. Lista de Chequeo Previa al Envío (Directrices FIE-ESPOCH 2026)
- [x] Manuscrito compilado a 10 páginas (holgadamente dentro del límite máximo permitido en JJCIT de 16 páginas).
- [x] 8 figuras de alta resolución alojadas en la subcarpeta `figures/` e insertadas como `figures/figX...`.
- [x] Ninguna figura generada con IA de imágenes (regla dura de la Guía Metodológica).
- [x] Cero errores de compilación en `pdflatex` y `bibtex`.
- [x] Estilo bibliográfico IEEE numerado (`ieeetr.bst`) con 19 referencias y DOI/URL activo verificado.
- [x] 3 citas locales a artículos de JJCIT incorporadas en el manuscrito (*Odeh et al. 2021, Alslman et al. 2024, Ashi et al. 2021*).
- [x] Verificación estadística de tendencia decreciente monotónica con el test de Page ($Z = -2.66, p = 0.004$) y modelo ANCOVA ($p = 0.0048, R^2 = 0.695$).
- [x] Filiación institucional corregida con acentuación oficial LaTeX (`Polit\'ecnica`).
- [x] Exclusividad estricta de envío garantizada.
