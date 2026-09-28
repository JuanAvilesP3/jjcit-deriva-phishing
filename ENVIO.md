# Ficha de Instrucciones de Envío — Paper P8

## 1. Identificación de la Revista y Política Editorial
- **Revista destino:** *Jordanian Journal of Computers and Information Technology* (JJCIT)
- **Entidad editora:** Princess Sumaya University for Technology (PSUT) / Scientific Research Support Fund (SRSF), Amán, Jordania.
- **ISSN:** 2415-1076 (En línea) | 2413-9351 (Impreso).
- **Indexación oficial:** Scopus (CiteScore 2.5), DOAJ, EBSCO, dblp, Google Scholar.
- **Portal oficial de envíos (OJS):** [https://jjcit.org/page/instructions_authors](https://jjcit.org/page/instructions_authors)
- **Modalidad de revisión por pares:** **Simple Ciego (Single-Blind Peer Review)**. Los revisores evalúan de manera anónima, pero el manuscrito incluye los nombres y filiaciones de los autores en la primera página según la clase oficial `articleJJCIT.cls`.
- **Sección en OJS:** **Regular Research Paper**.
- **Cobra APC (Article Processing Charges)?:** **NO ($0 USD)**. Revista 100% Diamond Open Access sin cargos por envío ni procesamiento.

---

## 2. Metadatos del Manuscrito (para carga en el formulario OJS)

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
1. **Juan Pablo Aviles-Esparza** (*Autor de correspondencia*)
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `juan.aviles@espoch.edu.ec`
   - *ORCID:* [0009-0007-0058-8069](https://orcid.org/0009-0007-0058-8069)
2. **Italo Javier Tenempaguay-Granizo**
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `italo.tenempaguay@espoch.edu.ec`
   - *ORCID:* [0009-0001-5753-4279](https://orcid.org/0009-0001-5753-4279)
3. **Isaac David Torres-Paredes**
   - *Filiación:* Facultad de Informática y Electrónica, Escuela Superior Politécnica de Chimborazo (ESPOCH), Panamericana Sur km 1 1/2, Riobamba EC060155, Ecuador.
   - *Correo electrónico:* `isaac.torres@espoch.edu.ec`
   - *ORCID:* [0009-0001-7057-9316](https://orcid.org/0009-0001-7057-9316)

---

## 4. Archivos a Subir en la Plataforma OJS (Paso a Paso)
- **Paso 2 de OJS (Upload Submission / Manuscrito Principal):**
  - Subir: [`paper/P8_JJCIT_manuscript.pdf`](file:///c:/Users/Juan/Desktop/PAPERS/08-jjcit-deriva-phishing/paper/P8_JJCIT_manuscript.pdf) (10 páginas compiladas bajo la clase oficial `articleJJCIT.cls`).
  - Opcional requerido por JJCIT en etapas de producción: [`paper/P8_JJCIT_manuscript.docx`](file:///c:/Users/Juan/Desktop/PAPERS/08-jjcit-deriva-phishing/paper/P8_JJCIT_manuscript.docx).
- **Paso 4 de OJS (Upload Supplementary Files / Archivos Complementarios):**
  1. `paper/cover_letter.md` (Carta de presentación formal al Editor en Jefe de JJCIT).
  2. `paper/declaraciones.md` (Declaraciones de autoría CRediT, ética COPE de uso de IA, disponibilidad de datos en Zenodo y ausencia de conflictos).
  3. Paquete comprimido con fuentes completas de LaTeX: [`paquetes_envio/P08_JJCIT_paquete_envio.zip`](file:///c:/Users/Juan/Desktop/PAPERS/paquetes_envio/P08_JJCIT_paquete_envio.zip) (contiene `main.tex`, `refs.bib`, `articleJJCIT.cls`, `garamond.sty`, subcarpeta `figures/` con las 8 figuras vectoriales y raster de 300 DPI, `cover_letter.md`, `declaraciones.md`, `README.md`).

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
- **Depósito de datos y código en Zenodo:** [https://doi.org/10.5281/zenodo.22907772](https://doi.org/10.5281/zenodo.22907772) (DOI: `10.5281/zenodo.22907772`).

---

## 7. Lista de Chequeo Previa al Envío (Checklist)
- [x] Manuscrito compilado a 10 páginas (límite máximo permitido en JJCIT es de 16 páginas).
- [x] Figuras en alta resolución alojadas en la subcarpeta `figures/` e insertadas como `figures/figX...`.
- [x] Cero errores de compilación en `pdflatex` y `bibtex`.
- [x] Estilo bibliográfico IEEE numerado (`ieeetr.bst`) con 19 referencias y DOI/URL activo verificado.
- [x] 3 citas locales a artículos de JJCIT incorporadas en el manuscrito (*Odeh et al. 2021, Alslman et al. 2024, Ashi et al. 2021*).
- [x] Verificación estadística de tendencia decreciente monotónica con el test de Page ($Z = -2.66, p = 0.004$) y modelo ANCOVA ($p = 0.0048, R^2 = 0.695$).
- [x] Filiación institucional corregida con acentuación oficial LaTeX (`Polit\'ecnica`).
