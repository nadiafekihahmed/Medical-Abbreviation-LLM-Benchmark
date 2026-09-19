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
