---
id: model-comparison
title: Local Model Comparison
type: evaluation
status: completed
authority: canonical
relations:
  - type: depends-on
    target: evaluation-methodology
  - type: informs
    target: ollama-mvp-decision
  - type: part-of
    target: roadmap-phase-1-quality-validation
last_reviewed: 2026-07-16
---

# Local Model Comparison

Phase 1 compared two local 4B-class models with the same 16-case dataset,
Translate Mode prompt, Ollama runtime, and generation parameters.

## Candidate record

| Model | Parameters | Quantization | Protected pass | Coverage | Added requirements | Output discipline | Warm median / p95 | Result |
|---|---:|---|---:|---:|---:|---:|---:|---|
| `qwen3.5:4b` | 4.7B | Q4_K_M | 100% | 100% | 0% | 100% | 1,085 / 1,455 ms | Selected |
| `gemma3:4b` | 4.3B | Q4_K_M | 87.5% | 82.29% | 0% | 87.5% | 1,073 / 2,679 ms | Rejected |

## Required context

The committed [raw result](../../evaluation/results/phase1-apple-m5-2026-07-16.json)
records dataset and prompt paths, model metadata, Ollama 0.32.0, Apple M5 with 24
GiB unified memory, macOS version, run time, and generation settings. Both models
used temperature 0, seed 42, a 4,096-token context, and a 1,024-token output cap.

The comparison used Ollama with cloud and history disabled, bound to
`127.0.0.1`. Model thinking was disabled so latency measures the Translate Mode
output rather than hidden reasoning.

## Scoring calibration

An initial complete run scored `qwen3.5:4b` coverage at 89.58%. Human review
found that all five apparent misses preserved the requirements but used valid
phrases absent from the deterministic marker lists, such as "order of passes"
for "pass order." Those paraphrases were added with regression tests, and the
full two-model comparison was rerun. No model output or quality threshold was
changed to obtain the final result.

## Failure classes

`gemma3:4b` exposed four material classes:

- exact-token loss, including changing `Node*` to `Node`;
- untranslated Korean output on one Git case;
- conversational preambles instead of output-only translation; and
- omitted source constraints, lowering requirement coverage.

The selected Qwen result had no detected failure in this dataset. That is not a
claim of general correctness: phrase matching can miss semantic additions or
valid paraphrases, and 16 synthetic cases do not cover production prompt
diversity. Phase 2 must still enforce protected elements independently before
automatic replacement.

## Decision

Select `qwen3.5:4b` Q4_K_M with
[`translate-v1`](../../evaluation/prompts/translate-v1.txt) and the recorded
generation settings as the Phase 1 baseline. Accept Ollama as the initial MVP
runtime subject to the runtime-neutral interface constraint in
[ADR-0002](../decisions/ADR-0002-ollama-mvp.md).

Re-run the versioned comparison after model, prompt, runtime, dataset, or scoring
rule changes. New failing cases become synthetic regression fixtures.
