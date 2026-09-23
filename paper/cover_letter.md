# Cover Letter — Jordanian Journal of Computers and Information Technology (JJCIT)

**To:**  
Editors-in-Chief and Editorial Board, *Jordanian Journal of Computers and Information Technology* (JJCIT)  

**Date:** August 27, 2026  
**Subject:** Submission of original research paper: *"Concept Drift in URL-Based Phishing Detection: A Temporal Evaluation"*  

---

Dear Editors-in-Chief and Editorial Board of *JJCIT*,

We are pleased to submit our original research manuscript titled **"Concept Drift in URL-Based Phishing Detection: A Temporal Evaluation"** for publication as a regular research article in the *Jordanian Journal of Computers and Information Technology* (JJCIT). Our study directly addresses machine learning applied to cybersecurity and network threat detection, perfectly fitting JJCIT's core scope and building upon foundational cybersecurity and phishing detection studies previously published in this journal (including *Odeh et al., 2021* and *Alslman et al., 2024*).

In this work, we rigorously evaluate a critical methodological gap in the literature: the ubiquitous practice of evaluating URL phishing classifiers using standard random train/test splits, which fundamentally assumes data stationarity and ignores adversarial concept drift. Using a curated dataset of **58,598 URLs** (**29,299 real phishing URLs** collected continuously from PhishTank over **180 days** with unauthenticated timestamps, paired with **29,299 legitimate domains** from the Tranco research list), we extract 32 lexical features and benchmark three classifier families (Random Forest, XGBoost, and Logistic Regression) under four distinct evaluation protocols: random split baseline, fixed earliest-to-latest temporal blocks, sliding retraining windows, and cumulative retraining. 

Our statistical analysis confirms a statistically significant performance degradation trend across time using an ANCOVA specification controlling for model fixed effects ($p = 0.0048$) and a non-parametric Page test ($Z = -2.66$, $p = 0.004$). Importantly, our feature ablation demonstrates that near-ceiling laboratory performance in published literature is heavily driven by negative-class construction choices (such as domain-level vs. path-level lexical artifacts), providing concrete recommendations for robust, temporal evaluation protocols in real-world security operations.

We confirm that:
1. This manuscript represents original research, has not been published previously, and is not currently under consideration for publication elsewhere.
2. The manuscript adheres to JJCIT length and ethical guidelines.
3. The authors have reviewed and approved the manuscript for submission.

In accordance with standard submission practices, we suggest the following three independent expert reviewers in machine learning security and phishing detection:

1. **Prof. Dr. Ahmad Odeh**  
   *Affiliation:* Faculty of Information Technology, Middle East University, Amman, Jordan  
   *E-mail:* `aodeh@meu.edu.jo`  
   *Expertise:* Phishing URL Detection, Ensemble Learning in Cybersecurity, Adaptive Boosting  

2. **Prof. Dr. Roberto Perdisci**  
   *Affiliation:* Department of Computer Science, University of Georgia, USA  
   *E-mail:* `perdisci@cs.uga.edu`  
   *Expertise:* Network Security, Domain and URL Classification, Adversarial Machine Learning  

3. **Prof. Dr. Feargus Pendlebury**  
   *Affiliation:* Department of Informatics, King's College London, United Kingdom  
   *E-mail:* `feargus.pendlebury@kcl.ac.uk`  
   *Expertise:* Temporal Bias in Machine Learning Security, Concept Drift, Classifier Evaluation  

Thank you very much for your time, editorial handling, and consideration of our manuscript.

Sincerely,
 
**Juan Pablo Aviles-Esparza** (on behalf of all coauthors)  
Software Engineering Department, Faculty of Informatics and Electronics  
Escuela Superior Politécnica de Chimborazo (ESPOCH), Riobamba 060155, Ecuador  
*Corresponding e-mail:* `juan.aviles@espoch.edu.ec`
