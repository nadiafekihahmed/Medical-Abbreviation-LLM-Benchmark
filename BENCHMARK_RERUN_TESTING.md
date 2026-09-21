# Project 0 — Benchmark Rerun Testing

This file records the benchmark reruns performed to verify the original results and provides instructions for additional team testing.

This file is separate from `README.md`. It is intended to keep the testing evidence, observations, and rerun results organized for comparison and review.

---

## 1. Why We Reran the Models

The original benchmark produced the following results:

| Model        | Original Accuracy |
| ------------ | ----------------: |
| Qwen2.5 1.5B |   37/50 = **74%** |
| Qwen2.5 3B   |   37/50 = **74%** |
| Qwen2.5 7B   |   35/50 = **70%** |

The 1.5B model obtaining a higher accuracy than the 7B model was somewhat unexpected.

The professor therefore asked us to rerun the models and verify whether the result was reproducible or whether there might have been an error in the original testing.

The reruns were performed using the same benchmark setup.

---

# 2. Benchmark Setup Used for Reruns

The following were kept unchanged during verification:

- Same dataset: `data/items.jsonl`
- Same 50 test items
- Same prompt: `src/prompt.py`
- Same scorer: `src/score.py`
- Temperature: `0`
- Maximum output tokens: `32`
- One warm-up request
- One request per test item
- No RAG
- No agents
- No chat history
- Same exact-match scoring procedure

The canonical prompt was:

```text
You are a medical abbreviation expansion system.

Your task is to expand the given medical abbreviation into its standard full medical term.

Return ONLY the full expansion.
Do not provide explanations, definitions, alternatives, examples, or additional text.
Do not include quotation marks or a period.

Medical abbreviation:
{ABBREVIATION}
```

### HOW TO RUN###

1/ install the models using ollam pull
2/run these : python src/run_local.py --model qwen2.5:1.5b-instruct --out results/file name // put file name related to your testing so we can seprate from my testings example i put cheap_results_rerun.csv
python src/run_local.py --model qwen2.5:7b-instruct --out results/fileName. // choose another file name than mine
python src/run_local.py --model qwen2.5:3b --out results/fileName

## Nadia's Testing

I reran the three models on my PC using the same dataset, prompt, scorer, temperature (0), and maximum output tokens (32). Each rerun was saved in a separate CSV file so previous results were not overwritten.

### Qwen2.5 1.5B

- **Result:** 37/50 (74%)
- **p50:** 367.95 ms
- **p95:** 524.26 ms
- **Speed:** 29.46 tokens/sec
- The rerun reproduced the original **74% accuracy** and the same 13 incorrect items — the outputs were identical to the original run token-for-token, not just equal in accuracy.

**What went well:**

- Correctly expanded most of the common medical abbreviations.
- Very fast on my PC.
- The same error pattern appeared again, which makes the result reproducible.

**What went wrong:**

- Some abbreviations were ambiguous, such as **PE**, **OR**, and **SC**, and the model selected the wrong meaning.
- Some answers were medically close but did not exactly match the expected answer.
- The strict scorer treats small differences as incorrect, for example **"White Blood Cells" vs "white blood cell"**.
- It also made errors with **BID, TID, QID, PRN, and NPO** — this model missed all five.
- One output for **PO** was in Chinese instead of the expected English expansion.

---

### Qwen2.5 7B

- **Result:** 35/50 (70%)
- **p50:** 1625.80 ms
- **p95:** 2292.77 ms
- **Speed:** 6.62 tokens/sec
- The rerun reproduced the original **70% accuracy** and the same 15 incorrect items — again, the outputs matched the original run exactly, not just the score.

**What went well:**

- Correctly handled many common medical abbreviations.
- The overall accuracy was reproduced during the rerun.
- It produced medically reasonable answers for many of the test cases.
- Unlike the 1.5B model, it correctly handled **BID, QID, and NPO** — only **TID** and **PRN** were wrong here.

**What went wrong:**

- It was much slower than the 1.5B on my PC.
- Some answers were correct in meaning but failed the exact-match scorer, for example **"thyroid stimulating hormone" vs "thyroid-stimulating hormone"**.
- A similar formatting problem appeared with **WBC**: it output **"WhiteBloodCell"** (missing spaces entirely) instead of **"white blood cell"**.
- It also selected incorrect meanings for ambiguous abbreviations such as **PE, PRN, OR, and PPE**.

---

### Qwen2.5 3B

- **Original result:** 37/50 (74%) on hadeel's PC.
- **Nadia's rerun:** 34/50 (68%) on my PC.
- The rerun therefore **did not reproduce the original accuracy** — unlike the 1.5B and 7B models, whose reruns were fully deterministic (identical outputs, only latency differed), the 3B model actually produced different text on 9 of the 50 items. Net effect: 5 items flipped from correct to incorrect, 2 flipped from incorrect to correct, for a 6-point accuracy drop. It was also noticeably faster on rerun (p50 ~674ms vs ~1100ms originally), which suggests something changed between runs (e.g. quantization, sampling, or environment) rather than pure run-to-run noise.

**What went well:**

- It correctly expanded many common abbreviations.
- Several outputs were very close to the expected answers.
- The model performed reasonably well on standard medical abbreviations.
- Unlike the other two models, it correctly handled **PRN and NPO** — only **BID, TID, and QID** were wrong here.

**What went wrong:**

- Some answers differed only slightly from the expected answer but were still marked incorrect.
- Examples include **"whitebloodcell" vs "white blood cell"**, **"red blood cells" vs "red blood cell"**, and **"chest xray" vs "chest X-ray"**.
- It also made incorrect predictions for ambiguous abbreviations such as **STAT, ED, and OR** — though the **OR** output ("orlando's ringworm") reads more like a hallucinated guess than a genuine alternate meaning, unlike **ED**, where "erectile dysfunction" is a real alternate expansion.
- Some outputs used a different but medically related expression, such as **"glycated hemoglobin"** instead of the expected **"hemoglobin A1c"**.
- The original 3B test and my rerun were performed on different PCs, so hardware differences also affect performance measurements.

---

### Overall Observation

The reruns showed that the models can correctly handle many standard medical abbreviations, but the main difficulties were:

- **Ambiguous abbreviations** with multiple possible meanings (and in at least one case, a likely hallucination rather than a true alternate meaning — see OR above).
- **Small wording differences**, such as _cell/cells_.
- **Spacing and hyphenation**, such as _thyroid stimulating hormone_ vs _thyroid-stimulating hormone_, or missing spaces entirely (_WhiteBloodCell_).
- **Alternative medical terminology**, where the model gives a medically related answer but not the exact expected answer.
- **BID, TID, QID, PRN, and NPO** were each difficult for at least one model, but not consistently across all three — **TID** was the only one all three models missed; the others were split differently per model (see each model's section above).

Because the scorer uses strict exact matching, these small differences are counted as incorrect even when the model's answer may be medically understandable or closely related to the expected answer.

## Two of the three reruns (1.5B and 7B) were **exactly reproducible** — same outputs, same score. Only the 3B rerun showed real output variation, which is the one worth flagging to the professor as the actual case of non-reproducibility.

## Hajer's Testing

I reran the benchmark on my PC using the same dataset, prompt, scorer, temperature (0), maximum output tokens (32), and exact-match scoring procedure described above.

The original benchmark results were compared with my rerun results. I kept the original Hajer result files unchanged and saved my rerun results under separate filenames:

- Top: `results/hajer_top_results.csv` vs `results/top_results_rerun.csv`
- Cheap: `results/hajer_cheap_results.csv` vs `results/cheap_results_rerun.csv`
- Local: `results/hajer_local_results.csv` vs `results/local_results_rerun.csv`

The purpose of the rerun was to check whether the original results were reproducible, especially the Cheap model result.

### Qwen2.5 1.5B — Top

- **Original result:** 36/50 (72%)
- **Hajer's rerun:** 35/50 (70%)
- **Accuracy change:** -1 correct answer
- **Outputs changed:** 10/50
- **Correct → incorrect:** 3
- **Incorrect → correct:** 2

The rerun did not reproduce the original accuracy exactly. The model changed its output on 10 of the 50 test items.

Examples of changed outputs included:

- **IBS:** `Irritable Bowel Syndrome` → `IrritableBowelSyndrome`
- **WBC:** `white blood cell` → `WhiteBloodCell`
- **Hct:** `hematocrit` → `Hematocrit`
- **CRP:** `C-reactive protein` → `C-Reactive Protein`
- **HbA1c:** `hemoglobin a1c` → `hemoglobin A1c`
- **SOB:** `shortness of breath` → `ShortnessOfBreath`
- **QID:** `Four times a day` → `Four Times Daily`
- **ENT:** `ear nose and throat` → `Ear Nose and Throat`
- **PPE:** `Pre Exposure Prophylaxis` → `Preventive Pulmonary Evaluation`

These changes show that some differences were caused by capitalization, spacing, wording, or a different interpretation of an abbreviation.

### Qwen2.5 1.5B — Cheap

- **Original result:** 36/50 (72%)
- **Hajer's rerun:** 37/50 (74%)
- **Accuracy change:** +1 correct answer
- **Outputs changed:** 5/50
- **Correct → incorrect:** 0
- **Incorrect → correct:** 1

The rerun slightly improved the original accuracy. Importantly, none of the previously correct answers became incorrect, while one previously incorrect answer became correct.

Changed outputs included:

- **CAD:** `Cardiac Arrest` → `Coronary Artery Disease`
- **NPO:** `Non-Prn` → `Non-Patient Ordered`
- **PO:** `PO - POISONOUS` → `口服`
- **OBGYN:** `OBSTETRICS AND GYNAECOLOGY` → `OBSTETRICIAN AND GYNAECOLOGIST`
- **DNR:** `DO NOT RESUSCITATE` → `Do Not Resuscitate`

The Cheap rerun therefore reached **74% accuracy**, compared with the original **72%**.

### Qwen2.5 1.5B — Local

- **Original result:** 35/50 (70%)
- **Hajer's rerun:** 34/50 (68%)
- **Accuracy change:** -1 correct answer
- **Outputs changed:** 10/50
- **Correct → incorrect:** 3
- **Incorrect → correct:** 2

The Local rerun did not reproduce the original accuracy and decreased by one correct answer.

Changed outputs included:

- **CHF:** `congestive heart failure` → `Congestive heart failure`
- **PUD:** `peptic ulcer disease` → `Pyloric Ulcer Disease`
- **IBS:** `Irritable Bowel Syndrome` → `irritable bowel syndrome`
- **RA:** `rheumatoidarthritis` → `rheumatoid arthritis`
- **BUN:** `blood urea nitrogen` → `Blood Urea Nitrogen`
- **HbA1c:** `hemoglobin a1c` → `glycated hemoglobin`
- **TSH:** `thyroid-stimulating-hormone` → `thyroid-stimulating hormone`
- **BID:** `twice-daily` → `bis daily`
- **IM:** `Intramuscular` → `intramuscularly`
- **OR:** `orlando` → `orlando's ringworm`

Several of these differences were formatting or capitalization changes, while others were genuine changes in the model's answer.

### Hajer Rerun — Performance Comparison

The latency and speed measurements also changed between the original runs and my reruns:

| Test  | Original p50 |  Rerun p50 | Original speed | Rerun speed |
| ----- | -----------: | ---------: | -------------: | ----------: |
| Top   |   3428.31 ms | 1734.47 ms |     6.00 tok/s |  6.35 tok/s |
| Cheap |   2415.20 ms |  416.54 ms |    24.70 tok/s | 27.27 tok/s |
| Local |   2654.38 ms |  670.11 ms |    13.14 tok/s | 15.69 tok/s |

The reruns were faster in p50 latency for all three tests. The average token-per-second speed also increased for all three.

### Overall Observation — Hajer's Rerun

The rerun results show that the original results were not reproduced exactly on my PC.

- **Top:** decreased from 72% to 70%.
- **Cheap:** increased from 72% to 74%.
- **Local:** decreased from 70% to 68%.

The Cheap model was therefore the only one of the three whose accuracy increased in my rerun. It also remained the highest-scoring model among these three reruns at **74%**.

The changed outputs show several recurring causes of exact-match errors:

- capitalization differences;
- missing or added spaces;
- hyphenation differences;
- alternative but medically related terminology;
- ambiguous abbreviations;
- different interpretations of the same abbreviation.

Because the benchmark uses strict exact-match scoring, even medically similar answers can be counted as incorrect when they do not exactly match the expected output.

The rerun therefore provides additional evidence that benchmark accuracy can vary between runs and environments, while also showing that the original observation about the Cheap model achieving strong accuracy was reproduced in this rerun: the Cheap model achieved **37/50 (74%)**.
## Khira's Testing

I reran the three Qwen2.5 models on my PC using the same dataset, prompt, scorer, temperature (0), maximum output tokens (32), and exact-match scoring procedure described above. Each rerun was saved in a separate CSV file so that the previous results were not overwritten.

The files used for my reruns were:

- 1.5B: `results/khira_cheap_results.csv`
- 3B: `results/khira_local_results.csv`
- 7B: `results/khira_top_results.csv`

The purpose of my testing was to verify the benchmark results and check whether the smaller models could still achieve similar or better accuracy than the larger model.

---

### Qwen2.5 1.5B — Cheap

- **Khira's rerun:** 36/50 (72%)
- **p50:** 2345.79 ms
- **p95:** 2487.29 ms
- **Speed:** 35.60 tokens/sec

The 1.5B model achieved **72% accuracy** in my rerun. It was also the fastest of the three models I tested.

**What went well:**

- It correctly expanded most of the common medical abbreviations.
- It achieved the same overall accuracy as the much larger 7B model.
- It was the fastest model in my testing, reaching an average speed of **35.60 tokens/sec**.
- It correctly handled abbreviations such as **TSH, CXR, STAT, PACU, PPE, AED, and DNR**.

**What went wrong:**

- Some abbreviations were interpreted incorrectly. For example, **CAD** was expanded as `Cardiac Arrest` instead of `coronary artery disease`.
- **PE** was interpreted as `Physical Examination` instead of `pulmonary embolism`.
- It struggled with several medication and frequency abbreviations, including **NPO, PRN, BID, TID, and QID**.
- Some answers were close to the expected output but failed the exact-match scorer. For example, **WBC** produced `White Blood Cells` instead of `white blood cell`.
- **CVA** produced `Cerebral Vascular Accident` instead of the expected `cerebrovascular accident`.
- Other incorrect interpretations included **SC** as `Sepsis` and **OR** as `orthopedic surgery`.
- **ENT** produced `Ear, Nose, and Throat`, which is understandable but did not exactly match the expected output.

---

### Qwen2.5 3B — Local

- **Khira's rerun:** 35/50 (70%)
- **p50:** 2567.97 ms
- **p95:** 2768.94 ms
- **Speed:** 19.51 tokens/sec

The 3B model achieved **70% accuracy**, which was slightly lower than both the 1.5B and 7B models in my testing.

**What went well:**

- It correctly expanded many common medical abbreviations.
- It correctly handled **PE**, which both the 1.5B and 7B models interpreted incorrectly.
- It also correctly answered **NPO, PRN, PO, PPE, and AED**.
- Several of its incorrect outputs were very close to the expected answers.

**What went wrong:**

- Some errors were caused by spacing differences. For example, **RA** produced `rheumatoidarthritis` and **WBC** produced `whitebloodcell`.
- **RBC** produced `red blood cells` instead of the expected singular `red blood cell`.
- **TSH** produced `thyroid-stimulating-hormone` instead of `thyroid-stimulating hormone`.
- **CXR** produced `chest xray` instead of `chest X-ray`.
- It struggled with the frequency abbreviations **BID, TID, and QID**.
- **ED** was interpreted as `erectile dysfunction` instead of `emergency department`.
- **STAT** was incorrectly expanded as `statistically`.
- **OR** produced `orlando`.
- **OBGYN** produced `obstetrician gynecologist` instead of `obstetrics and gynecology`.

These results show that some of the errors came from formatting and wording differences, while others came from a different interpretation of an abbreviation.

---

### Qwen2.5 7B — Top

- **Original result:** 36/50 (72%)
- **Khira's rerun:** 36/50 (72%)
- **Accuracy change:** No change
- **Outputs changed:** 0/50
- **Correct → incorrect:** 0
- **Incorrect → correct:** 0

The rerun fully reproduced the original Top model result. All **50 outputs were identical** between the original test and my rerun, resulting in the same accuracy of **36/50 (72%)**.

**What went well:**

- The model reproduced exactly the same outputs across both runs.
- It correctly expanded many common medical abbreviations.
- The identical outputs and accuracy show that the Top model result was reproducible in this test.
- It correctly handled **NPO, BID, QID, ED, and DNR**.

**What went wrong:**

- **PE** was interpreted as `Physical Examination` instead of `pulmonary embolism`.
- Some answers failed because of spacing differences. **IBS** produced `IrritableBowelSyndrome`, **CKD** produced `ChronicKidneyDisease`, and **WBC** produced `WhiteBloodCell`.
- **TSH** produced `thyroid stimulating hormone` instead of `thyroid-stimulating hormone`.
- **CXR** produced `chest x ray` instead of `chest X-ray`.
- **SOB** produced `ShortnessOfBreath` instead of `shortness of breath`.
- Some outputs were medically related but did not match the expected wording. **PRN** produced `pro re nata` instead of `as needed`, while **TID** produced `three times a day` instead of `three times daily`.
- Other incorrect interpretations included **STAT** as `STANDING ORDER`, **OR** as `operative report`, and **PPE** as `Preventive Pulmonary Evaluation`.
- **PACU** produced `Post Anesthesia Care Unit` instead of `post-anesthesia care unit`.
- **AED** produced `Automatic External Defibrillator` instead of `automated external defibrillator`.

The main difference between the original Top test and my rerun was therefore performance rather than accuracy or model output.

---

### Khira's Rerun — Performance Comparison

| Model | Accuracy | p50 | p95 | Speed |
| --- | ---: | ---: | ---: | ---: |
| Qwen2.5 1.5B | 36/50 (**72%**) | 2345.79 ms | 2487.29 ms | **35.60 tok/s** |
| Qwen2.5 3B | 35/50 (**70%**) | 2567.97 ms | 2768.94 ms | 19.51 tok/s |
| Qwen2.5 7B | 36/50 (**72%**) | 3421.38 ms | 4510.35 ms | 7.53 tok/s |

The results show that increasing the model size did not increase the accuracy in my rerun. The **1.5B and 7B models both achieved 72%**, while the 3B model achieved **70%**.

There was a clearer difference in performance speed. The 1.5B model was the fastest at **35.60 tokens/sec**, followed by the 3B model at **19.51 tokens/sec**. The 7B model was the slowest at **7.53 tokens/sec**.

The 1.5B model therefore achieved the same accuracy as the 7B model while generating output much faster on my PC.

---

### Overall Observation — Khira's Rerun

My rerun produced the following results:

- **1.5B:** 36/50 (**72%**)
- **3B:** 35/50 (**70%**)
- **7B:** 36/50 (**72%**)

The results show that the larger model did not automatically achieve higher accuracy on this specific benchmark. The smallest 1.5B model matched the 7B model at **72%**, while the 3B model achieved **70%**.

For the Top/7B model, I was also able to compare the original test with the rerun. The result was fully reproduced: both runs achieved **36/50 (72%)**, and all **50 outputs were identical**. Only the performance measurements changed between the two runs.

Across the three models, several recurring causes of errors were observed:

- ambiguous abbreviations with multiple possible meanings;
- missing or added spaces;
- singular and plural differences;
- hyphenation differences;
- alternative but medically related terminology;
- different interpretations of the same abbreviation.

Examples include `WhiteBloodCell` instead of `white blood cell`, `chest x ray` instead of `chest X-ray`, and `three times a day` instead of `three times daily`.

Because the benchmark uses strict exact-match scoring, medically understandable or closely related answers can still be marked incorrect when they do not exactly match the expected output.

Overall, my testing supports the observation that model size alone did not determine performance on this benchmark. In my rerun, the **1.5B model matched the 7B model's 72% accuracy while running substantially faster**, and the 7B original result was exactly reproduced in terms of both accuracy and outputs.